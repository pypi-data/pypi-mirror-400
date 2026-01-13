"""Dump conftool data to a git repository, retaining authorship.

This is done by listening for a specific audit log handler that
allows us to know what changes were made by whom, and then we
fetch the data from conftool and store it in a git repository.

Usage:

```bash
# first of all create an empty git repository
$ pushd /path/to/empty/repo
$ git init
# Make sure you added the correct data in the configuration file
$ grep conftool2git /etc/conftool/config.yaml
conftool2git_address: localhost:1312
# Now run the conftool2git server
$ conftool2git --config /etc/conftool/config.yaml --port 1312 /path/to/empty/repo
# You can make all the changes you want in conftool and the git repo will be populated
# with a commit per edit made in conftool
$ confctl --config /etc/conftool/config.yaml set foo/bar '{"baz": "quux"}'
```
"""

import argparse
import asyncio
from dataclasses import dataclass
import logging
import os
import pathlib
import json
import sys
import time

from typing import Callable, Generator, List, Optional

from aiohttp import web

# pylint: disable=no-name-in-module
from pygit2 import GIT_FILEMODE_TREE, GitError, Repository, Signature, Tree

# pylint: enable=no-name-in-module

import yaml

from conftool import audit, drivers
from conftool.kvobject import Entity
from conftool.cli import ConftoolClient


MAX_QUEUE_SIZE = 1000
logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--bind-addr",
        default="0.0.0.0",
        help="Address to bind the TCP server to (default: all interfaces)",
    )
    parser.add_argument("--port", type=int, default=1312, help="Port to bind the TCP server to")
    parser.add_argument(
        "--config", help="Path to the configuration file", default="/etc/conftool/config.yaml"
    )
    parser.add_argument(
        "--no-startup-sync",
        action="store_true",
        help="Do not sync on startup. Useful during development.",
    )
    parser.add_argument("--max-queue-size", type=int, default=MAX_QUEUE_SIZE)
    parser.add_argument("repo", help="Path to the git repository")
    return parser.parse_args(args)


# conveniently patch the audit.AuditLogEntry class to have a key property
# that returns the key in the format expected by conftool
audit.AuditLogEntry.key = property(
    lambda self: Entity.backend.driver.abspath(f"{self.kind}/{self.object}")
)


@dataclass
class GitTreeElement:
    """A tree element in a git repository."""

    tree: Tree
    path: List[str]
    repo: Repository

    def children(self) -> Generator["GitTreeElement", None, None]:
        """Return the next tree element."""
        for entry in self.tree:
            if entry.filemode == GIT_FILEMODE_TREE:
                yield GitTreeElement(self.repo.get(entry.id), self.path + [entry.name], self.repo)


class AuditLogHandler:
    """Handles audit log messages."""

    def __init__(self, repo: str, q: asyncio.Queue, run_sync_on_startup: bool = True) -> None:
        self.repo = Repository(repo)
        self.queue = q
        self.repo_path = pathlib.Path(repo)
        self.run_sync_on_startup = run_sync_on_startup

    async def run(self) -> None:
        """Run the audit log handler."""
        if self.run_sync_on_startup:
            logger.info("Running startup sync")
            await self.startup_sync()
            logger.info("Startup sync done")
        keep_running = True
        while keep_running:
            done = False
            try:
                entry = self.queue.get_nowait()
                await self.process_audit_log_entry(entry)
                done = True
            except asyncio.QueueEmpty:
                logger.debug("Queue is empty, waiting 1 second.")
                # Sleep for a bit to avoid busy waiting
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                logger.info("Received cancellation, exiting")
                keep_running = False
                done = True
            except RuntimeError as e:
                logger.error("RuntimeError: %s", e)
                keep_running = False
            finally:
                # Mark the task as done in any case where we're done
                if done:
                    self.queue.task_done()

    async def startup_sync(self) -> None:
        """Reconcile the repository with the current state of the backend."""
        all_on_backend = {}
        for backend_path, data in Entity.backend.driver.all_data(""):
            relpath = pathlib.Path(backend_path).relative_to(Entity.backend.driver.base_path)
            all_on_backend[str(relpath)] = data

        # First, we need to ensure that the repository is in sync with the backend
        for relpath, data in all_on_backend.items():
            relpath = f"{relpath}.yaml"
            key_path = self.repo_path / relpath
            if not key_path.is_file():
                logger.info("Creating %s", key_path)
                key_path.parent.mkdir(parents=True, exist_ok=True)
                to_write = True
            else:
                with key_path.open() as f:
                    existing_data = yaml.safe_load(f)
                to_write = existing_data != data

            if to_write:
                logger.info("Writing %s", key_path)
                key_path.write_text(yaml.dump(data))
                self.repo.index.add(relpath)

        # Now we need to remove any object that's been removed from the backend
        all_on_backend_files = set([f"{k}.yaml" for k in all_on_backend])
        for filepath in self._all_repo_files():
            if filepath not in all_on_backend_files:
                logger.info("Removing %s", filepath)
                (self.repo_path / filepath).unlink()
                self.repo.index.remove(filepath)

        self.repo.index.write()
        # Now commit the changes
        await self._commit(None, "audit2git reconciliation on startup")

    async def process_audit_log_entry(self, msg: dict) -> None:
        """Process an audit log entry."""
        entry = audit.AuditLogEntry.from_json(msg)
        key_path = self.repo_path / f"{entry.object}.yaml"
        key_relpath = key_path.relative_to(self.repo_path)
        logger.info("Processing audit log entry for: %s", entry.object)
        if entry.action == "delete":
            # Delete the key from the git repository
            data = None
        else:
            try:
                data = Entity.backend.driver.read(entry.object).data
            except drivers.NotFoundError:
                logger.warning("Key %s not found", entry.object)
                return

        if data is None:
            # Delete the key from the git repository
            key_path.unlink(missing_ok=True)
            self.repo.index.remove(key_relpath)
        else:
            # Write the data to the git repository
            # ensure we have all the directory structure
            if not key_path.is_file():
                key_path.parent.mkdir(parents=True, exist_ok=True)

            key_path.write_text(yaml.dump(data))
            self.repo.index.add(str(key_relpath))
        # Now commit the changes
        self.repo.index.write()
        timestamp = int(time.mktime(entry.timestamp.timetuple()))
        author = Signature(entry.actor, f"root+{entry.actor}@wikimedia.org", time=timestamp)
        message = f"Commit of {entry.action} for {key_relpath}"
        await self._commit(author, message)
        logger.info("Committed changes for %s", entry.object)

    async def _commit(self, author: Optional[Signature], message: str) -> None:
        """Commit the current index."""
        committer = Signature("conftool2git", "root@wikimedia.org")
        if author is None:
            author = committer

        # Allow for an empty repository
        try:
            ref = self.repo.head.name
            parents = [self.repo.head.target]
        except GitError:
            ref = "HEAD"
            parents = []

        # libgit2 does not support git hooks, and doesn't even mention it in its documentation.
        # This is a known issue:
        #  https://github.com/libgit2/libgit2/issues/964
        # Apparently something being hard to do cross-platform is a reason to not do it at all,
        # and also not to warn your users.
        # Let's at least implement pre-commit and post-commit hooks here ourselves.
        await self._exec_git_hook("pre-commit")

        self.repo.create_commit(
            ref,
            author,
            committer,
            message,
            self.repo.index.write_tree(),
            parents,
        )
        await self._exec_git_hook("post-commit")

    async def _exec_git_hook(self, hook: str) -> None:
        hook = self.repo_path / ".git" / "hooks" / hook
        if hook.is_file():
            logger.debug("Running %s hook", hook)
            proc = await asyncio.create_subprocess_shell(
                str(hook),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.repo_path),
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                raise RuntimeError(f"{hook} failed: {stderr.decode()}")
            logger.debug("%s output: %s", hook, stdout.decode())

    def _all_repo_files(self) -> List[str]:
        """Return all the files in the repository.

        Method from https://www.hydrogen18.com/blog/list-all-files-git-repo-pygit2.html
        """
        all_files = []
        git_elements = []
        # First check if we have a main branch
        try:
            git_elements.append(
                GitTreeElement(self.repo.revparse_single("main").tree, [], self.repo)
            )
        except KeyError:
            return []

        while git_elements:
            element = git_elements.pop()
            for entry in element.tree:
                if entry.filemode == GIT_FILEMODE_TREE:
                    next_tree = element.repo.get(entry.id)
                    next_path = element.path + [entry.name]
                    git_elements.append(GitTreeElement(next_tree, next_path, element.repo))
                else:
                    all_files.append(os.path.join(*element.path, entry.name))
        return all_files


def get_req_handler(queue: asyncio.Queue) -> Callable:
    """Return a request handler for the audit log server."""

    async def handle_audit_log_msg(request: web.Request) -> None:
        """Receives an audit log message and puts it in the queue."""
        try:
            logger.info("Received request from %s", request.remote)
            data = await request.content.read()
            entry = json.loads(data.decode())
            queue.put_nowait(entry)
            logger.info("Enqueued audit log entry")
        except json.JSONDecodeError as e:
            logger.error("Failed to decode JSON message: %s", e)
            return web.Response(status=400)
        except asyncio.QueueFull:
            logger.error(
                "Queue is full, dropping message. You should consider increasing MAX_QUEUE_SIZE"
            )
            return web.Response(status=503)
        return web.Response(status=200)

    return handle_audit_log_msg


def main(arguments=None):
    """Run the conftool2git server."""
    if sys.version_info < (3, 11):
        raise RuntimeError("Python 3.11 or higher is required")
    if arguments is None:
        arguments = sys.argv[1:]
    args = parse_args(arguments)
    queue = asyncio.Queue(maxsize=args.max_queue_size)

    # Load a conftool client with an empty schema.
    # While loading Schema.from_data() will mark the schema as having errors
    # we don't care about that here. We care about inizializing Entity.backend.driver
    _ = ConftoolClient(configfile=args.config, schema={})
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    audit_handler = AuditLogHandler(args.repo, queue, not args.no_startup_sync)

    # Make aiohttp handle the loop and add the audit handler as a background task.
    # take from the recipe at https://docs.aiohttp.org/en/v3.8.1/web_advanced.html
    # under "Background tasks"
    async def start_background_tasks(app):
        """Start the background tasks."""
        app["audit_handler"] = asyncio.create_task(audit_handler.run())

    async def cleanup_background_tasks(app):
        """Cleanup the background tasks."""
        app["audit_handler"].cancel()
        await app["audit_handler"]

    app = web.Application()
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.add_routes([web.post("/auditlog", get_req_handler(queue))])
    web.run_app(app, host=args.bind_addr, port=args.port)


if __name__ == "__main__":
    main()
