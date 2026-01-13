"""Integration tests for conftool2git."""

import asyncio
import logging
import os
import pathlib
import shutil
import sys
import tempfile
import time

import pygit2

import pytest
import yaml

from conftool.cli import conftool2git

from conftool.tests.integration import IntegrationTestBase, MockArg, fixtures_base
from conftool.cli import syncer, tool


@pytest.mark.skipif(sys.version_info < (3, 11), reason="async tests require python 3.11")
class TestConftool2Git(IntegrationTestBase):
    """Integration tests for conftool2git."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @staticmethod
    def sync(directory: pathlib.Path = fixtures_base / "integration_cycle_data"):
        """Load data into conftool"""
        schema_path = str(fixtures_base / "schema.yaml")
        MockArg.schema = schema_path
        # Run a first sync
        sync = syncer.Syncer(schema_path, str(directory))
        sync.load()
        # Let's modify a single object
        # Now let's modify a single object
        t = tool.ToolCliByLabel(MockArg("name=Varenne"))
        t._action = "get"
        for obj in t.host_list():
            obj.update({"height": 167, "nick": "The Captain"})

    def setUp(self):
        super().setUp()
        # Run sync.
        self.sync()
        self.base_path = tempfile.mkdtemp()
        self.repo_path = pathlib.Path(self.base_path) / "repo"
        os.makedirs(self.repo_path)
        self.repo = pygit2.init_repository(self.repo_path, False)
        if sys.version_info >= (3, 11):
            queue = asyncio.Queue()
            self.log_handler = conftool2git.AuditLogHandler(str(self.repo_path), queue, False)
        logging.basicConfig(level=logging.DEBUG)

    def tearDown(self):
        super().tearDown()
        self.repo.free()
        shutil.rmtree(self.base_path)

    def test_first_sync(self):
        """Test that the initial sync works."""
        asyncio.run(self.log_handler.startup_sync())
        horse = self.repo_path / "horses" / "brown" / "runner" / "Varenne.yaml"
        assert horse.is_file()
        with horse.open() as f:
            horse = yaml.safe_load(f)
        assert horse["height"] == 167
        assert horse["nick"] == "The Captain"

    def test_sync_element_modified(self):
        """Test that elements modified are reproduced in a sync."""
        asyncio.run(self.log_handler.startup_sync())
        # Now let's modify Secretariat
        t = tool.ToolCliByLabel(MockArg("name=Secretariat"))
        t._action = "get"
        for obj in t.host_list():
            obj.update({"height": 169, "nick": "Big Red"})
        # Sync conftool2git again
        asyncio.run(self.log_handler.startup_sync())
        horse = self.repo_path / "horses" / "brown" / "runner" / "Secretariat.yaml"
        assert horse.is_file()
        with horse.open() as f:
            horse = yaml.safe_load(f)
        assert horse["height"] == 169
        assert horse["nick"] == "Big Red"

    @pytest.mark.skip(reason="This test works locally but fails in CI. Will need to invesitgate.")
    def test_sync_element_deleted(self):
        """Test that elements deleted are removed when syncing."""
        asyncio.run(self.log_handler.startup_sync())
        # Now let's delete one horse
        t = tool.ToolCliByLabel(MockArg("name=Secretariat"))
        t._action = "get"
        for obj in t.host_list():
            obj.delete()
        # Sync again
        asyncio.run(self.log_handler.startup_sync())
        # Check that the action is gone
        big_red = self.repo_path / "horses" / "brown" / "runner" / "Secretariat.yaml"
        assert not big_red.is_file()

    def test_sync_created(self):
        """Test that elements created are added in a sync."""
        asyncio.run(self.log_handler.startup_sync())
        # Now let's sync from another directory; this should create
        # a new horse under other directories/tags.
        self.sync(fixtures_base / "integration_cycle_data_1")
        # Sync conftool2git again
        asyncio.run(self.log_handler.startup_sync())
        # Check that the action is there
        frodo = self.repo_path / "horses" / "white" / "shire" / "Frodo.yaml"
        assert frodo.is_file()
        with frodo.open() as f:
            frodo = yaml.safe_load(f)

    def test_audit_handling_modify(self):
        """Test handling a modification."""
        # First, sync the data
        asyncio.run(self.log_handler.startup_sync())
        obj_path = self.repo_path / "horses" / "brown" / "runner" / "Varenne.yaml"
        with obj_path.open() as f:
            varenne = yaml.safe_load(f)
        assert varenne["nick"] == "The Captain"
        # Add a modification to the object
        t = tool.ToolCliByLabel(MockArg("name=Varenne"))
        t._action = "get"
        for obj in t.host_list():
            obj.update({"nick": "Il Capitano"})
        # Now let's simulate this emitted an audit log message
        audit_log_msg = {
            "ecs.version": "1.11.0",
            "@timestamp": "2024-09-16T07:23:53.977580+00:00",
            "log.level": "info",
            "event.action": "write",
            "event.dataset": "conftool.audit",
            "event.module": "conftool",
            "event.kind": "event",
            "event.outcome": "success",
            "user.name": "godzilla",
            "service.type": "horse",
            "service.name": "horses/brown/runner/Varenne",
            "host.hostname": "pinkunicorn",
        }
        expected_time = int(
            time.mktime(time.strptime("2024-09-16T07:23:53.977580+00:00", "%Y-%m-%dT%H:%M:%S.%f%z"))
        )
        asyncio.run(self.log_handler.process_audit_log_entry(audit_log_msg))
        assert obj_path.is_file()
        # Verify it's a well formed yaml file
        with obj_path.open() as f:
            varenne = yaml.safe_load(f)
        assert varenne["nick"] == "Il Capitano"

        # now let's check the latest commit
        commit = self.repo[self.repo.head.target]
        assert commit.message == "Commit of write for horses/brown/runner/Varenne.yaml"
        assert commit.author.name == "godzilla"
        assert commit.author.email == "root+godzilla@wikimedia.org"
        assert commit.author.time == expected_time

    def test_audit_handling_delete(self):
        """Test removing an object."""
        asyncio.run(self.log_handler.startup_sync())
        audit_log_msg = {
            "ecs.version": "1.11.0",
            "@timestamp": "2024-09-16T07:23:53.977580+00:00",
            "log.level": "info",
            "event.action": "delete",
            "event.dataset": "conftool.audit",
            "event.module": "conftool",
            "event.kind": "event",
            "event.outcome": "success",
            "user.name": "godzilla",
            "service.type": "horse",
            "service.name": "horses/brown/runner/Secretariat",
            "host.hostname": "pinkunicorn",
        }

        expected_time = int(
            time.mktime(time.strptime("2024-09-16T07:23:53.977580+00:00", "%Y-%m-%dT%H:%M:%S.%f%z"))
        )
        asyncio.run(self.log_handler.process_audit_log_entry(audit_log_msg))
        obj_path = self.repo_path / "horses" / "brown" / "runner" / "Secretariat.yaml"
        assert not obj_path.exists()
        # now let's check the latest commit
        commit = self.repo[self.repo.head.target]
        assert commit.message == "Commit of delete for horses/brown/runner/Secretariat.yaml"
        assert commit.author.name == "godzilla"
        assert commit.author.email == "root+godzilla@wikimedia.org"
        assert commit.author.time == expected_time

    def test_audit_handling_error(self):
        """Test handling a non-existing object."""
        asyncio.run(self.log_handler.startup_sync())
        current_commit = self.repo.head.target
        audit_log_msg = {
            "ecs.version": "1.11.0",
            "@timestamp": "2024-09-16T07:23:53.977580+00:00",
            "log.level": "info",
            "event.action": "write",
            "event.dataset": "conftool.audit",
            "event.module": "conftool",
            "event.kind": "event",
            "event.outcome": "error",
            "user.name": "godzilla",
            "service.type": "horse",
            "service.name": "horses/brown/runner/NonExisting",
            "host.hostname": "pinkunicorn",
        }
        asyncio.run(self.log_handler.process_audit_log_entry(audit_log_msg))
        # We should not have created any commit
        assert self.repo.head.target == current_commit
