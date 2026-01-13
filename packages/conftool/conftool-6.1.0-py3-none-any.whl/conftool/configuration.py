from dataclasses import dataclass, field
from typing import List

from conftool import yaml_safe_load


class ConfigurationError(Exception):
    """Exception raised when we fail to load the configuration."""


def get(configfile: str) -> "Config":
    """
    Loads the config from file
    """
    try:
        config = yaml_safe_load(configfile, default={})
        return Config(**config)
    except Exception as exc:
        raise ConfigurationError(exc) from exc


class ReqConfiguration:
    """Container for configuration of requestctl"""

    def __init__(self, **kwargs) -> None:
        if "haproxy_path" in kwargs:
            self.haproxy_path = kwargs["haproxy_path"]
        else:
            self.haproxy_path = "/etc/haproxy/"

        self.haproxy_reserved_slots: List[int] = kwargs.get("haproxy_reserved_slots", [0])
        self.haproxy_concurrency_slots: int = kwargs.get("haproxy_concurrency_slots", 10)
        self.haproxy_ring_name: str = kwargs.get("haproxy_ring_name", "reqctl-ring")
        self.varnish_acl_ipblocks: List[str] = kwargs.get("varnish_acl_ipblocks", ["abuse"])


class DbCtlConfiguration:
    """Container for configuration for dbctl."""

    def __init__(self, **kwargs) -> None:
        self.parsercache_min_pooled_sections: int = kwargs.get("parsercache_min_pooled_sections", 2)


class ExtensionsConfig:
    """Container for configuration of extensions"""

    def __init__(self, **kwargs) -> None:
        self.reqconfig = ReqConfiguration(**kwargs.get("reqconfig", {}))
        self.dbctlconfig = DbCtlConfiguration(**kwargs.get("dbctlconfig", {}))


@dataclass
class Config:
    driver: str = "etcd"
    hosts: List[str] = field(default_factory=lambda: ["http://localhost:2379"])
    namespace: str = "/conftool"
    api_version: str = "v1"
    pools_path: str = "pools"
    driver_options: dict = field(default_factory=dict)
    tcpircbot_host: str = ""
    tcpircbot_port: int = 0
    cache_path: str = "/var/cache/conftool"
    read_only: bool = False
    conftool2git_address: str = ""
    extensions_config: ExtensionsConfig = field(default_factory=ExtensionsConfig)

    def __post_init__(self):
        if self.pools_path.startswith("/"):
            raise ValueError("pools_path must be a relative path.")
        if not isinstance(self.extensions_config, ExtensionsConfig):
            self.extensions_config = ExtensionsConfig(**self.extensions_config)

    def requestctl(self) -> ReqConfiguration:
        """Get the configuration for requestctl."""
        return self.extensions_config.reqconfig

    def dbctl(self) -> DbCtlConfiguration:
        """Get the configuration for dbctl."""
        return self.extensions_config.dbctlconfig
