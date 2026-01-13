import unittest
from conftool.audit import get_actor, set_actor_func, reset_actor_func
from unittest.mock import patch
from conftool.configuration import Config
from conftool.kvobject import Entity
from unittest.mock import patch, MagicMock
from conftool.tests.unit import MockBackend, MockEntity


class TestGetActor(unittest.TestCase):
    def tearDown(self):
        reset_actor_func()

    def test_default_behavior(self):
        """Test the default behavior of get_actor."""
        fallback = "default_user"
        self.assertEqual(get_actor(fallback), fallback)

    def test_set_reset_actor_func(self):
        """Test that setting a custom function works as expected."""

        def custom_get_actor(fallback):
            return "patched_user"

        # Monkey-patch the function
        set_actor_func(custom_get_actor)
        self.assertEqual(get_actor("default_user"), "patched_user")
        # Reset to default
        reset_actor_func()
        self.assertEqual(get_actor("default_user"), "default_user")

    def test_set_actor_func_twice(self):
        """Test that setting the actor function twice raises an error."""

        def custom_get_actor(fallback):
            return "patched_user"

        set_actor_func(custom_get_actor)

        with self.assertRaises(RuntimeError):
            set_actor_func(custom_get_actor)

    def test_kvobject_audit_calls_modified_get_actor(self):
        """Test that Kvobject.audit calls the modified get_actor."""

        def custom_get_actor(action):
            return "custom_actor"

        set_actor_func(custom_get_actor)

        Entity.backend = MockBackend({})
        Entity.config = Config(driver="")
        entity = MockEntity("Foo", "Bar", "test")
        with patch(
            "conftool.kvobject.audit_log",
        ) as mock_audit_log:
            entity.audit("test_action", True)

            mock_audit_log.assert_called_with(
                action="test_action",
                actor="custom_actor",
                kind="mockentity",
                obj=entity.key,
                success=True,
            )
