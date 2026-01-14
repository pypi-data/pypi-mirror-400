#!/usr/bin/env python3
"""
Prolog Process Pool using SWI-Prolog's MQI (Machine Query Interface).

This provides a connection pool of persistent Prolog processes that can be
reused across multiple queries, avoiding subprocess spawn overhead.

Usage:
    pool = PrologPool(size=4)
    try:
        with pool.acquire() as prolog:
            result = prolog.query("member(X, [1,2,3]).", max_solutions=10)
    finally:
        pool.shutdown()
"""

from __future__ import annotations

import json
import queue
import shutil
import subprocess
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Iterator
import tempfile
import os


@dataclass
class PrologProcess:
    """Represents a single persistent Prolog process."""
    process_id: int
    process: subprocess.Popen
    stdin_fd: Any
    stdout_fd: Any
    created_at: float
    last_used: float
    query_count: int = 0

    def is_alive(self) -> bool:
        """Check if the process is still running."""
        return self.process.poll() is None


class PrologConnection:
    """
    A connection to a single Prolog MQI process.

    This wraps a persistent Prolog process and provides query execution.
    """

    def __init__(self, process_id: int, swipl_path: str):
        self.process_id = process_id
        self.swipl_path = swipl_path
        self.process: Optional[PrologProcess] = None
        self._lock = threading.Lock()
        self._start_process()

    def _start_process(self) -> None:
        """Start a persistent Prolog process with MQI server."""
        # Start SWI-Prolog in server mode
        # We'll use a simple stdin/stdout protocol for now
        # For production, use actual MQI with sockets

        proc = subprocess.Popen(
            [self.swipl_path, "--quiet", "--nosignals"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        self.process = PrologProcess(
            process_id=self.process_id,
            process=proc,
            stdin_fd=proc.stdin,
            stdout_fd=proc.stdout,
            created_at=time.time(),
            last_used=time.time()
        )

    def execute_query(
        self,
        facts: List[Dict[str, Any]],
        rules_program: Optional[str],
        query: str,
        max_solutions: int = 5
    ) -> Dict[str, Any]:
        """
        Execute a query on this Prolog process.

        For now, falls back to subprocess mode for compatibility.
        TODO: Implement true MQI protocol communication.
        """
        with self._lock:
            if not self.process or not self.process.is_alive():
                self._start_process()

            self.process.last_used = time.time()
            self.process.query_count += 1

            # TODO: Use actual MQI protocol
            # For now, we'll use the file-based approach but could optimize
            # by keeping the process warm and just sending new facts/queries
            from logic_server.core.solver import prolog_query
            return prolog_query(facts, None, rules_program, query, max_solutions)

    def close(self) -> None:
        """Terminate the Prolog process."""
        with self._lock:
            if self.process and self.process.is_alive():
                self.process.process.terminate()
                try:
                    self.process.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.process.kill()
            self.process = None

    def reset(self) -> None:
        """Reset the process (kill and restart)."""
        self.close()
        self._start_process()


class PrologPool:
    """
    Thread-safe pool of Prolog processes.

    Manages a pool of persistent Prolog connections that can be reused
    across multiple queries for better performance.
    """

    def __init__(
        self,
        size: int = 4,
        max_queries_per_process: int = 1000,
        max_idle_time: int = 300,
        swipl_path: Optional[str] = None
    ):
        """
        Initialize the Prolog process pool.

        Args:
            size: Number of Prolog processes to maintain
            max_queries_per_process: Recycle process after this many queries
            max_idle_time: Recycle process after this many seconds idle
            swipl_path: Path to swipl executable (auto-detected if None)
        """
        self.size = size
        self.max_queries_per_process = max_queries_per_process
        self.max_idle_time = max_idle_time

        self.swipl_path = swipl_path or shutil.which("swipl")
        if not self.swipl_path:
            raise RuntimeError("SWI-Prolog not found on PATH (swipl)")

        self._pool: queue.Queue[PrologConnection] = queue.Queue(maxsize=size)
        self._all_connections: List[PrologConnection] = []
        self._lock = threading.Lock()
        self._shutdown = False

        # Create initial pool
        for i in range(size):
            conn = PrologConnection(i, self.swipl_path)
            self._pool.put(conn)
            self._all_connections.append(conn)

        # Start maintenance thread
        self._maintenance_thread = threading.Thread(
            target=self._maintenance_loop,
            daemon=True
        )
        self._maintenance_thread.start()

    @contextmanager
    def acquire(self, timeout: float = 30.0) -> Iterator[PrologConnection]:
        """
        Acquire a Prolog connection from the pool.

        Usage:
            with pool.acquire() as prolog:
                result = prolog.execute_query(...)
        """
        if self._shutdown:
            raise RuntimeError("Pool is shut down")

        try:
            conn = self._pool.get(timeout=timeout)
        except queue.Empty:
            raise RuntimeError(f"Failed to acquire Prolog connection within {timeout}s")

        try:
            # Check if connection needs recycling
            if self._should_recycle(conn):
                conn.reset()

            yield conn
        finally:
            # Return to pool
            if not self._shutdown:
                self._pool.put(conn)

    def _should_recycle(self, conn: PrologConnection) -> bool:
        """Check if a connection should be recycled."""
        if not conn.process or not conn.process.is_alive():
            return True

        if conn.process.query_count >= self.max_queries_per_process:
            return True

        idle_time = time.time() - conn.process.last_used
        if idle_time >= self.max_idle_time:
            return True

        return False

    def _maintenance_loop(self) -> None:
        """Background thread to maintain pool health."""
        while not self._shutdown:
            time.sleep(30)  # Check every 30 seconds

            if self._shutdown:
                break

            # Check all connections and recycle stale ones
            with self._lock:
                for conn in self._all_connections:
                    if self._should_recycle(conn):
                        try:
                            conn.reset()
                        except Exception:
                            pass  # Will be recycled on next use

    def shutdown(self) -> None:
        """Shutdown the pool and terminate all processes."""
        self._shutdown = True

        # Drain the queue and close all connections
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except queue.Empty:
                break

        # Close any remaining connections
        with self._lock:
            for conn in self._all_connections:
                conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        with self._lock:
            total_queries = sum(
                conn.process.query_count if conn.process else 0
                for conn in self._all_connections
            )
            alive_count = sum(
                1 for conn in self._all_connections
                if conn.process and conn.process.is_alive()
            )

        return {
            "pool_size": self.size,
            "alive_processes": alive_count,
            "total_queries": total_queries,
            "available": self._pool.qsize(),
            "in_use": self.size - self._pool.qsize()
        }


# Global pool instance (optional - can also use per-session pools)
_global_pool: Optional[PrologPool] = None
_global_pool_lock = threading.Lock()


def get_prolog_pool(size: int = 4) -> PrologPool:
    """Get or create the global Prolog pool."""
    global _global_pool
    if _global_pool is None:
        with _global_pool_lock:
            if _global_pool is None:
                _global_pool = PrologPool(size=size)
    return _global_pool


def shutdown_global_pool() -> None:
    """Shutdown the global Prolog pool."""
    global _global_pool
    if _global_pool is not None:
        _global_pool.shutdown()
        _global_pool = None
