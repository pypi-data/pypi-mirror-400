import json
import sys

from conftool.drivers import NotFoundError
from conftool.cli.tool import ToolCliBase
from conftool.extensions.dbconfig.action import ActionResult
from conftool.extensions.dbconfig.config import DbConfig
from conftool.extensions.dbconfig.entities import Instance, Section


ALL_SELECTOR = "all"


class DbConfigCli(ToolCliBase):
    """
    CLI for dbconfig.
    """

    def __init__(self, args):
        super().__init__(args)
        schema = self.client.schema
        self.db_config = DbConfig(
            schema, Instance(schema), Section(schema), self.client.configuration.dbctl()
        )
        self.instance = Instance(schema, self.db_config.check_instance)
        self.section = Section(schema, self.db_config.check_section)

    def run_action(self) -> int:
        """
        This is the entrypoint for cli execution. We overload the original cli
        behaviour by selecting which sub-cli to use based on args.object_name
        """
        # TODO: the below uses a Golang-ish idiom
        result = getattr(self, "_run_on_{}".format(self.args.object_name))()
        if not result.success:
            print("Execution FAILED\nReported errors:", file=sys.stderr)
        if result.messages:
            print("\n".join(result.messages), file=sys.stderr)

        if result.announce_message:
            self.irc.warning(result.announce_message)

        return result.exit_code

    def _run_on_instance(self) -> ActionResult:
        name = self.args.instance_name
        cmd = self.args.command
        datacenter = self.args.scope
        if cmd == "get":
            if name == ALL_SELECTOR:
                for instance in self.instance.filter(dc=datacenter):
                    print(json.dumps(instance))
                return ActionResult(True, 0)

            try:
                res = self.instance.get(name, datacenter)
            except Exception as e:
                return ActionResult(False, 1, messages=["Unexpected error:", str(e)])
            if res is None:
                return ActionResult(False, 2, messages=["DB instance '{}' not found".format(name)])
            else:
                print(json.dumps(res.asdict(), indent=4, sort_keys=True))
                return ActionResult(True, 0)
        elif cmd == "edit":
            return self.instance.edit(name, datacenter=datacenter)
        elif cmd == "depool":
            return self.instance.depool(name, self.args.section, self.args.group)
        elif cmd == "pool":
            return self.instance.pool(
                name, self.args.percentage, self.args.section, self.args.group
            )
        elif cmd == "set-weight":
            return self.instance.weight(name, self.args.weight, self.args.section, self.args.group)
        elif cmd == "set-candidate-master":
            return self.instance.candidate_master(name, self.args.status, self.args.section)
        elif cmd == "set-note":
            return self.instance.note(name, self.args.note)
        else:
            raise ValueError(f"Invalid cmd '{cmd}'")

    def _run_on_section(self) -> ActionResult:
        name = self.args.section_name
        cmd = self.args.command
        datacenter = self.args.scope
        if cmd == "get":
            if name == ALL_SELECTOR:
                for section in self.section.filter(dc=datacenter):
                    print(json.dumps(section))
                return ActionResult(True, 0)

            try:
                res = self.section.get(name, datacenter)
            except ValueError as e:
                return ActionResult(False, 1, messages=[str(e)])
            except NotFoundError:
                return ActionResult(
                    False, 2, messages=["DB section '{}/{}' not found".format(datacenter, name)]
                )

            if res is None:
                return ActionResult(False, 2, messages=["DB section '{}' not found".format(name)])
            else:
                print(json.dumps(res.asdict(), indent=4, sort_keys=True))
                return ActionResult(True, 0)
        elif cmd == "set-master":
            instance_name = self.args.instance_name
            new_master = self.instance.get(instance_name, dc=self.args.scope)
            if new_master is None:
                return ActionResult(
                    False, 2, messages=["DB instance '{}' not found".format(instance_name)]
                )

            return self.section.set_master(name, datacenter, new_master)
        elif cmd == "edit":
            return self.section.edit(name, datacenter)
        elif cmd == "ro":
            return self.section.set_readonly(name, datacenter, True, self.args.reason)
        elif cmd == "rw":
            return self.section.set_readonly(name, datacenter, False)
        else:
            raise ValueError(f"Invalid cmd '{cmd}'")

    def _run_on_config(self) -> ActionResult:
        cmd = self.args.command
        dc = self.args.scope
        if cmd == "commit":
            return self.db_config.commit(
                batch=self.args.batch, datacenter=dc, comment=self.args.message
            )
        elif cmd == "restore":
            return self.db_config.restore(self.args.file, datacenter=dc)
        elif cmd == "diff":
            result, diff = self.db_config.diff(datacenter=dc, force_unified=self.args.unified)

            if result.success and result.exit_code == 1 and not self.args.quiet:
                sys.stdout.writelines(diff)

            return result
        elif cmd == "generate":
            result, config = self.db_config.generate(datacenter=dc)
            if config:
                print(json.dumps(config, indent=4, sort_keys=True))
            return result
        elif cmd == "get":
            config = self.db_config.live_config
            if dc is not None:
                if dc not in config:
                    messages = ["Datacenter {} not found in live configuration".format(dc)]
                    return ActionResult(False, 2, messages=messages)

                config = config[dc]

            print(json.dumps(config, indent=4, sort_keys=True))
            return ActionResult(True, 0)

        else:
            raise ValueError(f"Invalid cmd '{cmd}'")
