"""
PostgreSQL checkpoint saver implementation using pg8000 driver.

NOTE: This is nearly 100% copy-pasted from LangGraph's `langgraph-checkpoint-postgres` package, which internally leverages
`psycopg` for database connectivity.  This is a temporary mechanism until psycopg support is fully enabled within the Google
Cloud SQL Connector (expected early 2026)!
"""

import asyncio
from collections import defaultdict
import random
from contextlib import contextmanager
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Sequence, cast

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id,
    get_checkpoint_metadata,
    WRITES_IDX_MAP,
    BaseCheckpointSaver,
    ChannelVersions,
)
from langgraph.checkpoint.serde.types import TASKS

from sqlalchemy import Engine

MetadataInput = Optional[dict[str, Any]]


class Pg8000Saver(BaseCheckpointSaver[str]):
    """
    PostgreSQL checkpoint saver using pg8000 driver.  Nearly all logic is copied as-is from
    `langgraph-checkpoint-postgres with minor adjustments to convert `psycopg` connection handling
    and query support to `pg8000`.
    """

    def __init__(
        self,
        engine: Engine,
        serde: Optional[Any] = None,
    ):
        """
        Initialize the Pg8000Saver.

        Args:
            engine: SQLAlchemy engine
            serde: Optional serializer/deserializer (uses default if None)
        """
        super().__init__(serde=serde)

        self.engine = engine

        self._setup_database()

    @contextmanager
    def _get_connection(self):
        """Get a database connection context manager."""
        connection = self.engine.raw_connection()
        try:
            yield connection
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.close()

    @contextmanager
    def _dict_cursor(self, connection):
        """Context manager that yields a cursor with automatic dict conversion."""
        cursor = connection.cursor()
        try:
            # Store original fetchone and fetchall methods
            original_fetchone = cursor.fetchone
            original_fetchall = cursor.fetchall

            def dict_fetchone():
                if not cursor.description:
                    return None
                columns = [desc[0] for desc in cursor.description]
                row = original_fetchone()
                return dict(zip(columns, row)) if row else None

            def dict_fetchall():
                if not cursor.description:
                    return []
                columns = [desc[0] for desc in cursor.description]
                rows = original_fetchall()
                return [dict(zip(columns, row)) for row in rows]

            # Replace methods
            cursor.fetchone = dict_fetchone
            cursor.fetchall = dict_fetchall

            yield cursor
        finally:
            cursor.close()

    def _setup_database(self):
        """Create the necessary database tables if they don't exist."""
        with self._get_connection() as conn:
            with self._dict_cursor(conn) as cursor:
                cursor.execute(self.MIGRATIONS[0])
                cursor.execute(
                    "SELECT v FROM checkpoint_migrations ORDER BY v DESC LIMIT 1"
                )
                row = cursor.fetchone()
                if row is None:
                    version = -1
                else:
                    version = row["v"]
                for v, migration in zip(
                    range(version + 1, len(self.MIGRATIONS)),
                    self.MIGRATIONS[version + 1 :],
                ):
                    cursor.execute(migration)
                    cursor.execute(
                        f"INSERT INTO checkpoint_migrations (v) VALUES ({v})"
                    )

                conn.commit()

    def list(
        self,
        config: RunnableConfig | None,
        *,
        filter: dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> Iterator[CheckpointTuple]:
        """List checkpoints from the database.

        This method retrieves a list of checkpoint tuples from the Postgres database based
        on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).

        Args:
            config: The config to use for listing the checkpoints.
            filter: Additional filtering criteria for metadata. Defaults to None.
            before: If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None.
            limit: The maximum number of checkpoints to return. Defaults to None.

        Yields:
            Iterator[CheckpointTuple]: An iterator of checkpoint tuples.
        """

        where, args = self._search_where(config, filter, before)
        query = self.SELECT_SQL + where + " ORDER BY checkpoint_id DESC"
        if limit:
            query += f" LIMIT {limit}"
        # if we change this to use .stream() we need to make sure to close the cursor
        with self._get_connection() as conn:
            with self._dict_cursor(conn) as cur:
                cur.execute(query, args)
                values = cur.fetchall()
                if not values:
                    return
                # migrate pending sends if necessary
                if to_migrate := [
                    v
                    for v in values
                    if v["checkpoint"]["v"] < 4 and v["parent_checkpoint_id"]
                ]:
                    cur.execute(
                        self.SELECT_PENDING_SENDS_SQL,
                        (
                            values[0]["thread_id"],
                            [v["parent_checkpoint_id"] for v in to_migrate],
                        ),
                    )
                    grouped_by_parent = defaultdict(list)
                    for value in to_migrate:
                        grouped_by_parent[value["parent_checkpoint_id"]].append(value)
                    for sends in cur:
                        for value in grouped_by_parent[sends["checkpoint_id"]]:
                            if value["channel_values"] is None:
                                value["channel_values"] = []
                            self._migrate_pending_sends(
                                sends["sends"],
                                value["checkpoint"],
                                value["channel_values"],
                            )
                for value in values:
                    yield self._load_checkpoint_tuple(value)

    async def alist(
        self,
        config: RunnableConfig | None,
        *,
        filter: dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """Async version of list() method.

        This is a simple wrapper around the synchronous list() method that runs it
        in a thread pool and converts the iterator to an async iterator.

        Args:
            config: Base configuration for filtering checkpoints.
            filter: Additional filtering criteria for metadata.
            before: If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None.
            limit: Maximum number of checkpoints to return.

        Yields:
            AsyncIterator[CheckpointTuple]: An asynchronous iterator of matching checkpoint tuples.
        """
        # Run the sync method in a thread pool and collect all results
        checkpoints = await asyncio.to_thread(
            lambda: list(self.list(config, filter=filter, before=before, limit=limit))
        )

        # Convert to async iterator
        for checkpoint in checkpoints:
            yield checkpoint

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Get a checkpoint tuple from the database.

        This method retrieves a checkpoint tuple from the Postgres database based on the
        provided config. If the config contains a "checkpoint_id" key, the checkpoint with
        the matching thread ID and timestamp is retrieved. Otherwise, the latest checkpoint
        for the given thread ID is retrieved.

        Args:
            config: The config to use for retrieving the checkpoint.

        Returns:
            Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found.
        """

        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = get_checkpoint_id(config)
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        if checkpoint_id:
            args: tuple[Any, ...] = (thread_id, checkpoint_ns, checkpoint_id)
            where = "WHERE thread_id = %s AND checkpoint_ns = %s AND checkpoint_id = %s"
        else:
            args = (thread_id, checkpoint_ns)
            where = "WHERE thread_id = %s AND checkpoint_ns = %s ORDER BY checkpoint_id DESC LIMIT 1"

        with self._get_connection() as conn:
            with self._dict_cursor(conn) as cur:
                cur.execute(
                    self.SELECT_SQL + where,
                    args,
                )
                value = cur.fetchone()
                if value is None:
                    return None

                # migrate pending sends if necessary
                if value["checkpoint"]["v"] < 4 and value["parent_checkpoint_id"]:
                    cur.execute(
                        self.SELECT_PENDING_SENDS_SQL,
                        (thread_id, [value["parent_checkpoint_id"]]),
                    )
                    if sends := cur.fetchone():
                        if value["channel_values"] is None:
                            value["channel_values"] = []
                        self._migrate_pending_sends(
                            sends["sends"],
                            value["checkpoint"],
                            value["channel_values"],
                        )

                return self._load_checkpoint_tuple(value)

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Async version of get_tuple() method.

        This is a simple wrapper around the synchronous get_tuple() method that runs it
        in a thread pool

        Args:
            config: The config to use for retrieving the checkpoint.

        Returns:
            Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found.
        """
        return await asyncio.to_thread(lambda: self.get_tuple(config))

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Save a checkpoint to the database.

        This method saves a checkpoint to the Postgres database. The checkpoint is associated
        with the provided config and its parent config (if any).

        Args:
            config: The config to associate with the checkpoint.
            checkpoint: The checkpoint to save.
            metadata: Additional metadata to save with the checkpoint.
            new_versions: New channel versions as of this write.

        Returns:
            RunnableConfig: Updated configuration after storing the checkpoint."""

        configurable = config["configurable"].copy()
        thread_id = configurable.pop("thread_id")
        checkpoint_ns = configurable.pop("checkpoint_ns")
        checkpoint_id = configurable.pop("checkpoint_id", None)
        copy = checkpoint.copy()
        copy["channel_values"] = copy["channel_values"].copy()
        next_config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint["id"],
            }
        }

        # inline primitive values in checkpoint table
        # others are stored in blobs table
        blob_values = {}
        for k, v in checkpoint["channel_values"].items():
            if v is None or isinstance(v, (str, int, float, bool)):
                pass
            else:
                blob_values[k] = copy["channel_values"].pop(k)

        with self._get_connection() as conn:
            with self._dict_cursor(conn) as cur:
                if blob_versions := {
                    k: v for k, v in new_versions.items() if k in blob_values
                }:
                    cur.executemany(
                        self.UPSERT_CHECKPOINT_BLOBS_SQL,
                        self._dump_blobs(
                            thread_id,
                            checkpoint_ns,
                            blob_values,
                            blob_versions,
                        ),
                    )
                cur.execute(
                    self.UPSERT_CHECKPOINTS_SQL,
                    (
                        thread_id,
                        checkpoint_ns,
                        checkpoint["id"],
                        checkpoint_id,
                        copy,
                        get_checkpoint_metadata(config, metadata),
                    ),
                )
                conn.commit()

        return next_config

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Async version of put() method.

        This is a simple wrapper around the synchronous put() method that runs it
        in a thread pool

        Args:
            config: The config to associate with the checkpoint.
            checkpoint: The checkpoint to save.
            metadata: Additional metadata to save with the checkpoint.
            new_versions: New channel versions as of this write.

        Returns:
            RunnableConfig: Updated configuration after storing the checkpoint."""
        return await asyncio.to_thread(
            lambda: self.put(
                config=config,
                checkpoint=checkpoint,
                metadata=metadata,
                new_versions=new_versions,
            )
        )

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        """Store intermediate writes linked to a checkpoint.

        This method saves intermediate writes associated with a checkpoint to the Postgres database.

        Args:
            config: Configuration of the related checkpoint.
            writes: List of writes to store.
            task_id: Identifier for the task creating the writes.
        """

        query = (
            self.UPSERT_CHECKPOINT_WRITES_SQL
            if all(w[0] in WRITES_IDX_MAP for w in writes)
            else self.INSERT_CHECKPOINT_WRITES_SQL
        )
        with self._get_connection() as conn:
            with self._dict_cursor(conn) as cur:
                cur.executemany(
                    query,
                    self._dump_writes(
                        config["configurable"]["thread_id"],
                        config["configurable"]["checkpoint_ns"],
                        config["configurable"]["checkpoint_id"],
                        task_id,
                        task_path,
                        writes,
                    ),
                )
                conn.commit()

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        """Async version of put_writes() method.

        This is a simple wrapper around the synchronous put_writes() method that runs it
        in a thread pool

        Args:
            config: Configuration of the related checkpoint.
            writes: List of writes to store.
            task_id: Identifier for the task creating the writes.
        """
        await asyncio.to_thread(
            lambda: self.put_writes(
                config=config, writes=writes, task_id=task_id, task_path=task_path
            )
        )

    def delete_thread(self, thread_id: str) -> None:
        """Delete all checkpoints and writes associated with a thread ID.

        Args:
            thread_id: The thread ID to delete.

        Returns:
            None
        """
        with self._get_connection() as conn:
            with self._dict_cursor(conn) as cur:
                cur.execute(
                    "DELETE FROM checkpoints WHERE thread_id = %s",
                    (str(thread_id),),
                )
                cur.execute(
                    "DELETE FROM checkpoint_blobs WHERE thread_id = %s",
                    (str(thread_id),),
                )
                cur.execute(
                    "DELETE FROM checkpoint_writes WHERE thread_id = %s",
                    (str(thread_id),),
                )
                conn.commit()

    async def adelete_thread(self, thread_id: str) -> None:
        """Async version of delete_thread() method.

        This is a simple wrapper around the synchronous delete_thread() method that runs it
        in a thread pool.

        Args:
            thread_id: The thread ID to delete.

        Returns:
            None
        """
        await asyncio.to_thread(lambda: self.delete_thread(thread_id=thread_id))

    def _load_checkpoint_tuple(self, value: Dict) -> CheckpointTuple:
        """
        Convert a database row into a CheckpointTuple object.

        Args:
            value: A row from the database containing checkpoint data.

        Returns:
            CheckpointTuple: A structured representation of the checkpoint,
            including its configuration, metadata, parent checkpoint (if any),
            and pending writes.
        """
        return CheckpointTuple(
            {
                "configurable": {
                    "thread_id": value["thread_id"],
                    "checkpoint_ns": value["checkpoint_ns"],
                    "checkpoint_id": value["checkpoint_id"],
                }
            },
            {
                **value["checkpoint"],
                "channel_values": {
                    **value["checkpoint"].get("channel_values"),
                    **self._load_blobs(value["channel_values"]),
                },
            },
            value["metadata"],
            (
                {
                    "configurable": {
                        "thread_id": value["thread_id"],
                        "checkpoint_ns": value["checkpoint_ns"],
                        "checkpoint_id": value["parent_checkpoint_id"],
                    }
                }
                if value["parent_checkpoint_id"]
                else None
            ),
            self._load_writes(value["pending_writes"]),
        )

    def _migrate_pending_sends(
        self,
        pending_sends: List[tuple[bytes, bytes]],
        checkpoint: Dict[str, Any],
        channel_values: List[tuple[bytes, bytes, bytes]],
    ) -> None:
        if not pending_sends:
            return
        # add to values
        enc, blob = self.serde.dumps_typed(
            [self.serde.loads_typed((c.decode(), b)) for c, b in pending_sends],
        )
        channel_values.append((TASKS.encode(), enc.encode(), blob))
        # add to versions
        checkpoint["channel_versions"][TASKS] = (
            max(checkpoint["channel_versions"].values())
            if checkpoint["channel_versions"]
            else self.get_next_version(None, None)
        )

    def _load_blobs(
        self, blob_values: List[tuple[bytes, bytes, bytes]]
    ) -> Dict[str, Any]:
        if not blob_values:
            return {}
        return {
            k.decode(): self.serde.loads_typed((t.decode(), v))
            for k, t, v in blob_values
            if t.decode() != "empty"
        }

    def _dump_blobs(
        self,
        thread_id: str,
        checkpoint_ns: str,
        values: Dict[str, Any],
        versions: ChannelVersions,
    ) -> List[tuple[str, str, str, str, str, bytes | None]]:
        if not versions:
            return []

        return [
            (
                thread_id,
                checkpoint_ns,
                k,
                cast(str, ver),
                *(
                    self.serde.dumps_typed(values[k])
                    if k in values
                    else ("empty", None)
                ),
            )
            for k, ver in versions.items()
        ]

    def _load_writes(
        self, writes: List[tuple[bytes, bytes, bytes, bytes]]
    ) -> List[tuple[str, str, Any]]:
        return (
            [
                (
                    tid.decode(),
                    channel.decode(),
                    self.serde.loads_typed((t.decode(), v)),
                )
                for tid, channel, t, v in writes
            ]
            if writes
            else []
        )

    def _dump_writes(
        self,
        thread_id: str,
        checkpoint_ns: str,
        checkpoint_id: str,
        task_id: str,
        task_path: str,
        writes: Sequence[tuple[str, Any]],
    ) -> List[tuple[str, str, str, str, str, int, str, str, bytes]]:
        return [
            (
                thread_id,
                checkpoint_ns,
                checkpoint_id,
                task_id,
                task_path,
                WRITES_IDX_MAP.get(channel, idx),
                channel,
                *self.serde.dumps_typed(value),
            )
            for idx, (channel, value) in enumerate(writes)
        ]

    def get_next_version(self, current: str | None, channel: None) -> str:
        if current is None:
            current_v = 0
        elif isinstance(current, int):
            current_v = current
        else:
            current_v = int(current.split(".")[0])
        next_v = current_v + 1
        next_h = random.random()
        return f"{next_v:032}.{next_h:016}"

    def _search_where(
        self,
        config: RunnableConfig | None,
        filter: MetadataInput,
        before: RunnableConfig | None = None,
    ) -> tuple[str, List[Any]]:
        """Return WHERE clause predicates for alist() given config, filter, before.

        This method returns a tuple of a string and a tuple of values. The string
        is the parametered WHERE clause predicate (including the WHERE keyword):
        "WHERE column1 = $1 AND column2 IS $2". The list of values contains the
        values for each of the corresponding parameters.
        """
        wheres = []
        param_values = []

        # construct predicate for config filter
        if config:
            wheres.append("thread_id = %s ")
            param_values.append(config["configurable"]["thread_id"])
            checkpoint_ns = config["configurable"].get("checkpoint_ns")
            if checkpoint_ns is not None:
                wheres.append("checkpoint_ns = %s")
                param_values.append(checkpoint_ns)

            if checkpoint_id := get_checkpoint_id(config):
                wheres.append("checkpoint_id = %s ")
                param_values.append(checkpoint_id)

        # construct predicate for metadata filter
        if filter:
            wheres.append("metadata @> %s ")
            param_values.append(filter)

        # construct predicate for `before`
        if before is not None:
            wheres.append("checkpoint_id < %s ")
            param_values.append(get_checkpoint_id(before))

        return (
            "WHERE " + " AND ".join(wheres) if wheres else "",
            param_values,
        )

    MIGRATIONS = [
        """CREATE TABLE IF NOT EXISTS checkpoint_migrations (
        v INTEGER PRIMARY KEY
    );""",
        """CREATE TABLE IF NOT EXISTS checkpoints (
        thread_id TEXT NOT NULL,
        checkpoint_ns TEXT NOT NULL DEFAULT '',
        checkpoint_id TEXT NOT NULL,
        parent_checkpoint_id TEXT,
        type TEXT,
        checkpoint JSONB NOT NULL,
        metadata JSONB NOT NULL DEFAULT '{}',
        PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
    );""",
        """CREATE TABLE IF NOT EXISTS checkpoint_blobs (
        thread_id TEXT NOT NULL,
        checkpoint_ns TEXT NOT NULL DEFAULT '',
        channel TEXT NOT NULL,
        version TEXT NOT NULL,
        type TEXT NOT NULL,
        blob BYTEA,
        PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
    );""",
        """CREATE TABLE IF NOT EXISTS checkpoint_writes (
        thread_id TEXT NOT NULL,
        checkpoint_ns TEXT NOT NULL DEFAULT '',
        checkpoint_id TEXT NOT NULL,
        task_id TEXT NOT NULL,
        idx INTEGER NOT NULL,
        channel TEXT NOT NULL,
        type TEXT,
        blob BYTEA NOT NULL,
        PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
    );""",
        "ALTER TABLE checkpoint_blobs ALTER COLUMN blob DROP not null;",
        # NOTE: this is a no-op migration to ensure that the versions in the migrations table are correct.
        # This is necessary due to an empty migration previously added to the list.
        "SELECT 1;",
        """
        CREATE INDEX IF NOT EXISTS checkpoints_thread_id_idx ON checkpoints(thread_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS checkpoint_blobs_thread_id_idx ON checkpoint_blobs(thread_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS checkpoint_writes_thread_id_idx ON checkpoint_writes(thread_id);
        """,
        """ALTER TABLE checkpoint_writes ADD COLUMN task_path TEXT NOT NULL DEFAULT '';""",
    ]
    SELECT_SQL = """
        select
            thread_id,
            checkpoint,
            checkpoint_ns,
            checkpoint_id,
            parent_checkpoint_id,
            metadata,
            (
                select array_agg(array[bl.channel::bytea, bl.type::bytea, bl.blob])
                from jsonb_each_text(checkpoint -> 'channel_versions')
                inner join checkpoint_blobs bl
                    on bl.thread_id = checkpoints.thread_id
                    and bl.checkpoint_ns = checkpoints.checkpoint_ns
                    and bl.channel = jsonb_each_text.key
                    and bl.version = jsonb_each_text.value
            ) as channel_values,
            (
                select
                array_agg(array[cw.task_id::text::bytea, cw.channel::bytea, cw.type::bytea, cw.blob] order by cw.task_id, cw.idx)
                from checkpoint_writes cw
                where cw.thread_id = checkpoints.thread_id
                    and cw.checkpoint_ns = checkpoints.checkpoint_ns
                    and cw.checkpoint_id = checkpoints.checkpoint_id
            ) as pending_writes
        from checkpoints
        """

    SELECT_PENDING_SENDS_SQL = f"""
        select
            checkpoint_id,
            array_agg(array[type::bytea, blob] order by task_path, task_id, idx) as sends
        from checkpoint_writes
        where thread_id = %s
            and checkpoint_id = any(%s)
            and channel = '{TASKS}'
        group by checkpoint_id
    """

    UPSERT_CHECKPOINT_BLOBS_SQL = """
        INSERT INTO checkpoint_blobs (thread_id, checkpoint_ns, channel, version, type, blob)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (thread_id, checkpoint_ns, channel, version) DO NOTHING
    """

    UPSERT_CHECKPOINTS_SQL = """
        INSERT INTO checkpoints (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, checkpoint, metadata)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (thread_id, checkpoint_ns, checkpoint_id)
        DO UPDATE SET
            checkpoint = EXCLUDED.checkpoint,
            metadata = EXCLUDED.metadata;
    """

    UPSERT_CHECKPOINT_WRITES_SQL = """
        INSERT INTO checkpoint_writes (thread_id, checkpoint_ns, checkpoint_id, task_id, task_path, idx, channel, type, blob)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (thread_id, checkpoint_ns, checkpoint_id, task_id, idx) DO UPDATE SET
            channel = EXCLUDED.channel,
            type = EXCLUDED.type,
            blob = EXCLUDED.blob;
    """

    INSERT_CHECKPOINT_WRITES_SQL = """
        INSERT INTO checkpoint_writes (thread_id, checkpoint_ns, checkpoint_id, task_id, task_path, idx, channel, type, blob)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (thread_id, checkpoint_ns, checkpoint_id, task_id, idx) DO NOTHING
    """
