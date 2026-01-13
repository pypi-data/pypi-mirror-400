from unittest import mock

import etcd

from conftool import drivers
from conftool.drivers.etcd import Driver
from conftool.tests.integration import IntegrationTestBase
from conftool.kvobject import Entity


class EtcdDriverTest(IntegrationTestBase):

    def setUp(self):
        super().setUp()
        self.driver: Driver = Entity.backend.driver
        self.client: etcd.Client = self.driver.client

    def client_write(self, key: str, value: str, **kwargs):
        self.client.write(self.driver.abspath(key), value, **kwargs)

    def test_is_dir(self):
        self.client_write("a/key", "{}")
        # A key that does not exist returns false.
        self.assertFalse(self.driver.is_dir("nope"))
        # A key that corresponds to a directory returns true.
        self.assertTrue(self.driver.is_dir("a"))
        # A key that corresponds to a node returns false.
        self.assertFalse(self.driver.is_dir("a/key"))

    def test_all_keys(self):
        # Build a hierarchy of KV pairs.
        self.client_write("a/key", '{"value": 1}')
        self.client_write("a/b/key", '{"value": 2}')
        self.client_write("a/b/c/key", '{"value": 3}')
        # Add an empty leaf directory.
        self.client_write("a/b/c/d", None, dir=True)
        # An all_keys on the root of the above hierarchy returns all
        # non-directory leaf key-segment lists.
        self.assertCountEqual(
            self.driver.all_keys("a"),
            [
                ["key"],
                ["b", "key"],
                ["b", "c", "key"],
            ],
        )

    def test_all_keys_returns_empty_on_non_directory(self):
        # An all_keys on a non-directory returns an empty list.
        self.client_write("a/key", "{}")
        self.assertEqual(self.driver.all_keys("a/key"), [])

    def test_all_keys_fails_on_non_existent_key(self):
        # An all_keys on a non-existent key raises NotFoundError.
        with self.assertRaises(drivers.NotFoundError):
            self.driver.all_keys("nope")

    def test_all_objects(self):
        # Build a hierarchy of KV pairs.
        self.client_write("a/key", '{"value": 1}')
        self.client_write("a/b/key", '{"value": 2}')
        self.client_write("a/b/c/key", '{"value": 3}')
        # Add an empty leaf directory.
        self.client_write("a/b/c/d", None, dir=True)
        # An all_objects on the root of the above hierarchy returns key value
        # pairs for all non-directory leaves.
        result = self.driver.all_objects("a")
        for k, v in result:
            self.assertIsInstance(v, drivers.ObjectWireRepresentation)

        self.assertCountEqual(
            [(k, v.data) for k, v in result],
            [
                ("key", {"value": 1}),
                ("b/key", {"value": 2}),
                ("b/c/key", {"value": 3}),
            ],
        )

    def test_all_objects_returns_empty_on_non_directory(self):
        # An all_objects on a non-directory returns an empty list.
        self.client_write("a/key", "{}")
        self.assertEqual(self.driver.all_objects("a/key"), [])

    def test_all_objects_fails_on_non_existent_key(self):
        # An all_objects on a non-existent key raises NotFoundError.
        with self.assertRaises(drivers.NotFoundError):
            self.driver.all_objects("nope")

    def test_all_objects_fails_on_malformed_data(self):
        # An all_objects on a path containing malformed data raises BackendError.
        self.client_write("a/key", "definitely not json")
        with self.assertRaises(drivers.BackendError):
            self.driver.all_objects("a")

    def test_all_data(self):
        # Build a hierarchy of KV pairs.
        self.client_write("a/key", '{"value": 1}')
        self.client_write("a/b/key", '{"value": 2}')
        self.client_write("a/b/c/key", '{"value": 3}')
        # Add an empty leaf directory.
        self.client_write("a/b/c/d", None, dir=True)
        # An all_data on the root of the above hierarchy returns key value pairs
        # for all non-directory leaves.
        self.assertCountEqual(
            self.driver.all_data("a"),
            [
                ("key", {"value": 1}),
                ("b/key", {"value": 2}),
                ("b/c/key", {"value": 3}),
            ],
        )

    def test_all_data_returns_empty_on_non_directory(self):
        # An all_data on a non-directory returns an empty list.
        self.client_write("a/key", "{}")
        self.assertEqual(self.driver.all_data("a/key"), [])

    def test_all_data_fails_on_non_existent_key(self):
        # An all_data on a non-existent key raises NotFoundError.
        with self.assertRaises(drivers.NotFoundError):
            self.driver.all_data("nope")

    def test_all_data_fails_on_malformed_data(self):
        # An all_data on a path containing malformed data raises BackendError.
        self.client_write("a/key", "definitely not json")
        with self.assertRaises(drivers.BackendError):
            self.driver.all_data("a")

    def test_write_and_read(self):
        # A write initially returns None, as the key does not yet exist.
        self.assertIsNone(self.driver.write("a/key", {"x": 1}))
        # A read returns the expected value.
        self.assertEqual(self.driver.read("a/key").data, {"x": 1})
        # A subsequent write will update the stored object.
        self.assertEqual(self.driver.write("a/key", {"y": 2}).data, {"x": 1, "y": 2})
        # ... and a read will see the expected updated valued as well.
        self.assertEqual(self.driver.read("a/key").data, {"x": 1, "y": 2})

    def test_read_returns_none_on_directory(self):
        # A read on a directory returns None.
        self.client_write("a", None, dir=True)
        self.assertIsNone(self.driver.read("a"))

    def test_read_fails_on_non_existent_key(self):
        # A read for a non-existent key raises NotFoundError.
        with self.assertRaises(drivers.NotFoundError):
            self.driver.read("nope")

    def test_read_fails_on_malformed_data(self):
        # A read raises BackendError if the value is malformed.
        self.client_write("a/key", "definitely not json")
        with self.assertRaises(drivers.BackendError):
            self.driver.read("a/key")

    def test_write_fails_on_malformed_data(self):
        # An update-write (key exists) raises BackendError if the existing
        # value is malformed.
        self.client_write("a/key", "definitely not json")
        with self.assertRaises(drivers.BackendError):
            self.driver.write("a/key", {})

    def test_write_fails_on_directory(self):
        # A write on a directory raises BackendError.
        self.client_write("a", None, dir=True)
        with self.assertRaises(drivers.BackendError):
            self.driver.write("a", {})

    def test_write_fails_on_non_writable_path(self):
        # A write on a non-writable path (traverses b, which is a node) raises
        # BackendError.
        self.client_write("a/b", "{}")
        with self.assertRaises(drivers.BackendError):
            self.driver.write("a/b/key", {})

    def test_write_fails_on_conflict(self):
        # A write raises BackendError when it encounters a write conflict.
        read = etcd.Client.read

        def read_with_confict(key, **kwdargs):
            try:
                return read(self.client, key, **kwdargs)
            finally:
                # Make a write to the same key that interleaves between the
                # read and subsequent write. The value written is arbitrary.
                self.client.write(key, "{}")

        with mock.patch("etcd.Client.read", wraps=read_with_confict):
            # A write to a non-existent key is atomic, raising BackendError on
            # conflict.
            with self.assertRaises(drivers.BackendError):
                self.driver.write("a/key", {"value": 1})
            # A write to an existing key is atomic, raising BackendError on
            # conflict. Note the key exists due to the previouse conflicting
            # write.
            with self.assertRaises(drivers.BackendError):
                self.driver.write("a/key", {"value": 2})

    def test_delete(self):
        self.client_write("a/key", "{}")
        self.driver.delete("a/key")
        # Confirm that the key is gone.
        with self.assertRaises(etcd.EtcdKeyNotFound):
            self.client.read(self.driver.abspath("a/key"))

    def test_delete_fails_on_non_existent_key(self):
        # A delete on a non-existent key raises NotFoundError.
        with self.assertRaises(drivers.NotFoundError):
            self.driver.delete("nope")

    def test_delete_fails_on_directory(self):
        # A delete on a directory raises BackendError.
        self.client_write("a", None, dir=True)
        with self.assertRaises(drivers.BackendError):
            self.driver.delete("a")

    def test_ls(self):
        def extract_kv_data(listing):
            return [(k, v if v is None else v.data) for k, v in listing]

        # Build a hierarchy of KV pairs.
        self.client_write("a/key", '{"value": 1}')
        self.client_write("a/b/key", '{"value": 2}')
        self.client_write("a/b/c/key", '{"value": 3}')
        # An ls on each level of the hierarchy should return only the immediate
        # children, including child directories.
        self.assertCountEqual(
            extract_kv_data(self.driver.ls("a")),
            [
                ("key", {"value": 1}),
                ("b", None),
            ],
        )
        self.assertCountEqual(
            extract_kv_data(self.driver.ls("a/b")),
            [
                ("key", {"value": 2}),
                ("c", None),
            ],
        )
        self.assertEqual(
            extract_kv_data(self.driver.ls("a/b/c")),
            [
                ("key", {"value": 3}),
            ],
        )

    def test_ls_returns_empty_on_empty_directory(self):
        # An ls on an empty directory returns an empty list.
        self.client_write("a", None, dir=True)
        self.assertEqual(self.driver.ls("a"), [])

    def test_ls_returns_empty_on_non_directory(self):
        # An ls on a non-directory returns an empty list.
        self.client_write("a/key", "{}")
        self.assertEqual(self.driver.ls("a/key"), [])

    def test_ls_fails_on_non_existent_key(self):
        # An ls on a non-existent key raises NotFoundError.
        with self.assertRaises(drivers.NotFoundError):
            self.driver.ls("nope")

    def test_ls_fails_on_malformed_data(self):
        # An ls on a path containing malformed data raises BackendError.
        self.client_write("a/key", "definitely not json")
        with self.assertRaises(drivers.BackendError):
            self.driver.ls("a")

    def test_replace(self):
        # A replace erases existing data and replaces it with the new value.
        self.client_write("a/key", '{"x": 1}')
        new_value = self.driver.replace("a/key", {"y": 2})
        assert new_value.data == {"y": 2}
        # A replace on a non-existent key raises NotFoundError.
        with self.assertRaises(drivers.NotFoundError):
            self.driver.replace("nope", {"z": 3})
        # A replace on a directory raises BackendError.
        with self.assertRaises(drivers.BackendError):
            self.driver.replace("a", {"z": 3})

    def test_compare_and_swap_on_existing_key(self):
        # A compare_and_swap updates the value if the key exists.
        self.client_write("a/key", '{"x": 1}')
        expected_value = self.driver.read("a/key")
        # Compare and swap operates similarly to replace, but only if the
        # expected value matches the current value.
        new_value = self.driver.compare_and_swap("a/key", {"y": 2}, expected_value)
        # If we used .write() instead of .compare_and_swap(), the value would contain "x": 1, "y": 2
        assert new_value.data == {"y": 2}
        # Compare and swap fails when the expected value does not match the current value.
        with self.assertRaises(drivers.ConflictError):
            self.driver.compare_and_swap("a/key", {"z": 3}, expected_value)
        # Compare and swap on an existent key with None expected value fails with ConflictError.
        with self.assertRaises(drivers.ConflictError):
            self.driver.compare_and_swap("a/key", {"z": 3}, None)

    def test_compare_and_swap_on_non_existent_key(self):
        result = self.driver.compare_and_swap("a/key", {"x": 1}, None)
        assert result.data == {"x": 1}
        # A compare_and_swap on a non-existent key raises a NotFoundError.
        with self.assertRaises(drivers.NotFoundError):
            self.driver.compare_and_swap("another/key", {"z": 3}, result)

    def test_compare_and_swap_directory(self):
        # A compare_and_swap on a directory raises BackendError.
        self.client_write("a/key", '{"x": 1}')
        data = self.driver.read("a/key")

        with self.assertRaises(drivers.BackendError):
            self.driver.compare_and_swap("a", {"z": 3}, data)
        with self.assertRaises(drivers.BackendError):
            self.driver.compare_and_swap("a", {"z": 3}, None)
