"""Simple conftool initialization class."""

import logging

from typing import Optional
from conftool import configuration, setup_irc
from conftool.audit import auditlog, add_conftool2git_handler
from conftool.kvobject import Entity
from conftool.loader import Schema


class ObjectTypeError(Exception):
    """
    Exception raised whenever an inexistent object type is raised
    """


class ConftoolClient:
    """Class that simplifies initializing conftool with a schema."""

    def __init__(
        self,
        *,
        configfile: Optional[str] = None,
        config: Optional[configuration.Config] = None,
        schemafile: Optional[str] = None,
        schema: Optional[dict] = None,
        irc_logging: bool = True,
        read_only: bool = False,
    ) -> None:
        """Initialize conftool."""
        if configfile is not None:
            self.configuration = configuration.get(configfile)
        elif config is not None:
            self.configuration = config
        else:
            raise ValueError(
                "Either a configfile or a configuration must be passed to ConftoolClient()"
            )
        # Set up read only before schema is loaded
        if read_only:
            self.configuration.read_only = True
        Entity.setup(self.configuration)

        if schema is not None:
            self.schema = Schema.from_data(schema)
        elif schemafile is not None:
            self.schema = Schema.from_file(schemafile)
        else:
            raise ValueError(
                "Either a configfile or a configuration must be passed to ConftoolClient()"
            )
        if irc_logging:
            setup_irc(self.configuration)

        # Set up a stream handler for the audit log
        add_conftool2git_handler(self.configuration.conftool2git_address)

    def get(self, entity_name: str) -> Entity:
        """Returns the requested conftool object type client.

        Raises:
        """
        try:
            return self.schema.entities[entity_name]
        except KeyError as exc:
            raise ObjectTypeError(entity_name) from exc

    def set_audit_logger(self, logger: logging.Logger) -> None:
        """
        Sets the logger for the audit log.

        Args:
            logger (logging.Logger): The logger to be used for logging audit log entries.
        """
        auditlog.logger = logger
