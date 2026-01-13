import functools
import os

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from conftool import configuration


class BackendError(Exception):
    """The backend operation failed."""

    pass


class NotFoundError(BackendError):
    """The provided key does not exist in the kv store."""

    pass


class ConflictError(BackendError):
    """The backend operation failed due to a conflict."""

    pass


@dataclass
class ObjectWireMetadata:
    """Represents the metadata of an object coming from the wire."""

    # The revision id of the object. The default value is a negative integer to
    # indicate that the revision id is not available.
    revision_id: int = -1


@dataclass
class ObjectWireRepresentation:
    """Represents an object coming from the wire."""

    data: dict
    metadata: ObjectWireMetadata

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data


class BaseDriver:
    def __init__(self, config: configuration.Config) -> None:
        self.base_path = os.path.join(config.namespace, config.api_version)

    def abspath(self, path: str) -> str:
        """Get the absolute path for a given key.

        Arguments:
            path (str): the key path (which may already be absolute).

        Returns:
            An absolute path for the key.
        """
        if path.startswith("/"):
            return path
        else:
            return os.path.join(self.base_path, path)

    def is_dir(self, path: str) -> bool:
        """Check whether a given path is a directory.

        Arguments:
            path (str): the key path to check.

        Returns:
            Whether the path is a directory in the kv-store. It is not an error
            to provide a path that does not exist (returns False).
        """
        raise NotImplementedError("Here to abide by mypy")

    def all_keys(self, path: str) -> List[List[str]]:
        """Find all nodes beneath a given path.

        Given a path, returns all nodes beneath it as a list [tag1,...,name] of
        key-path segments relative to path (e.g., if a/b/c/d is a node and path
        is a/b, [c,d] is returned).

        This can be used to enumerate all objects, and then construct the
        object:

        for args in objclass.backend.driver.all_keys(path):
            yield objclass(*args)

        Arguments:
            path (str): the parent key path below which to find all nodes.

        Returns:
            A list of lists, containing key path segments. If the path is in
            fact not a directory, an empty list is returned.

        Raises:
            BackendError: if the underlying read operation failed.
            NotFoundError: if the provided directory does not exist.
        """
        raise NotImplementedError("Here to abide by mypy")

    def all_data(self, path: str) -> List[Tuple[str, Dict]]:
        """Read all nodes data beneath a given path.

        Given a path, return a list of tuples for all the objects under that
        path in the form [(relative_path1, data1), (relative_path2, data2), ...]

        Arguments:
            path (str): the parent key path below which to find all nodes.

        Returns:
            A list of tuples, containing node key path (relative to path) and
            data content (dict). If the path is in fact not a directory, an
            empty list is returned.

        Raises:
            BackendError: if the underlying read operation failed or returns
                malformed data.
            NotFoundError: if the provided directory does not exist.
        """
        raise NotImplementedError("Here to abide by mypy")

    def all_objects(self, path: str) -> List[Tuple[str, ObjectWireRepresentation]]:
        """Read all nodes objects beneath a given path.

        Given a path, return a list of tuples for all the objects under that
        path in the form [(relative_path1, object1), (relative_path2, object2), ...]

        Arguments:
            path (str): the parent key path below which to find all nodes.

        Returns:
            A list of tuples, containing node key path (relative to path) and
            the wire representation of the object. If the path
            is in fact not a directory, an empty list is returned.

        Raises:
            BackendError: if the underlying read operation failed or returns
                malformed data.
            NotFoundError: if the provided directory does not exist.
        """
        raise NotImplementedError("Here to abide by mypy")

    def write(self, key: str, value: Dict) -> Optional[ObjectWireRepresentation]:
        """Insert / update the value `value` to key `key`.

        If the key already exists in the kv-store, the new value is merged into
        the existing value (i.e., via update) and written back. If the key does
        not exist, the new value is simply written.

        Insert / update behavior is atomic, in that a conflicting write to the
        same key will cause it to abort.

        Arguments:
            key (str): the key path to which to write.
            value (dict): the value to write (or update the existing value).

        Returns:
            If the key already exists, the merged value written back to the
            store is returned (dict within an ObjectWireRepresentation),
            otherwise None.

        Raises:
            BackendError: if the underlying operations failed, including the
                case of a conflicting write to the same key, or if the initial
                read returns malformed data or encounters a key that is in fact
                a directory.
        """

    def compare_and_swap(
        self, key: str, value: Dict, expected: Optional[ObjectWireRepresentation] = None
    ) -> ObjectWireRepresentation:
        """Compare and swap the value at `key` with `value`.

        If the key exists and its value matches `expected`, the value is
        replaced with `value`. If its value does not match `expected`, the
        operation fails. If the key does not exist, and the `expected` value
        is not None, the operation fails.

        How the value is compared depends on the backend, but generally it is preferred
        to compare the content of the key on the backend rather than its metadata.

        Arguments:
            key (str): the key path to which to write.
            value (dict): the value to write.
            expected (Optional[ObjectWireRepresentation]): the expected value
                to match against.

        Returns:
            The value written to the store (dict within an
            ObjectWireRepresentation).

        Raises:
            BackendError: if the underlying operations failed, or the backend object
                is in fact a directory.
            ConflictError: if `expected` does not match the value at `key`. This includes
                the case where `expected` is None and the key exists
            NotFoundError: if `expected` is not None and the key does not exist.
        """
        raise NotImplementedError("Here to abide by mypy")

    def replace(self, key: str, value: Dict) -> ObjectWireRepresentation:
        """Replace the value at `key` with `value`.

        If the key exists, its value is replaced with the new value.
        BEWARE: this operation is dangerous, as it does not merge the new value
        with the existing value, nor checks the existing value before replacing it.
        It is mostly useful for schema upgrade operations where the existing object
        is not relevant anymore.

        Arguments:
            key (str): the key path to which to write.
            value (dict): the value to write.

        Returns:
            The value written to the store (dict within an
            ObjectWireRepresentation).

        Raises:
            BackendError: if the underlying operations failed, or encounters a
                key that is in fact a directory.
            NotFoundError: if the key does not exist.
        """
        raise NotImplementedError("Here to abide by mypy")

    def delete(self, key: str) -> None:
        """Delete the key at `key`.

        Arguments:
            key (str): the key path to delete.

        Raises:
            BackendError: if the underlying delete operation failed or the key
                is in fact a directory.
            NotFoundError: if the key does not exist.
        """

    def read(self, key: str) -> Optional[ObjectWireRepresentation]:
        """Read the value at `key`.

        Arguments:
            key (str): the key path to read.

        Returns:
            The value associated with the key, as a dict, within an
            ObjectWireRepresentation. If the key exists, but is in fact a
            directory, returns None.

        Raises:
            BackendError: if the underlying read operation failed or returns
                malformed data.
            NotFoundError: if the key does not exist.
        """

    def ls(self, path: str) -> List[Tuple[str, Optional[ObjectWireRepresentation]]]:
        """List the contents of a path in the kv-store.

        Given a path that's a directory in the kv-store, returns a list of (key,
        None | value) tuples, one for each direct child, where None is returned
        for a child directory (otherwise the child value is returned).

        Arguments:
            path (str): the key path to list.

        Returns:
            A list of tuples, each containing node key path (relative to path)
            and data content (dict within an ObjectWireRepresentation). If the
            path is in fact not a directory, an empty list is returned.

        Raises:
            BackendError: if the underlying read operation failed or returns
                malformed data.
            NotFoundError: if the provided directory does not exist.
        """
        raise NotImplementedError("Here to abide by mypy")

    @property
    def actor(self) -> str:
        """Represents the driver's notion of the actor performing the action.

        For example, this may be the username of the actor when authenticating
        to the kv-store.
        """
        raise NotImplementedError("Here to abide by mypy")


def wrap_exception(exc):
    """Wrap exceptions from the backend with BackendError.

    Arguments:
        exc (Exception): The exception class to wrap.
    """

    def actual_wrapper(fn):
        @functools.wraps(fn)
        def _wrapper(*args, **kwdargs):
            try:
                return fn(*args, **kwdargs)
            except exc as e:
                raise BackendError(f"Backend error: {e}") from e

        return _wrapper

    return actual_wrapper
