import json

from .helper import file_from_url, log, get_remote_hero
from .factory import HEROFactory, DatasourceHEROFactory, PolledDatasourceHEROFactory


class Document(dict):
    @classmethod
    def parse_string(cls, s: str):
        """
        Parse a document in JSON format from a string.

        Args:
            s: string containing the JSON representation of the config
        """
        try:
            obj = cls()
            obj.update(json.loads(s))
            return obj
        except json.JSONDecodeError as e:
            log.error(f"Error while encoding json: {e}")

    @classmethod
    def parse_url(cls, url: str):
        """
        Parse a document in JSON format from a URL.

        Args:
            url: any URL supported by urllib (e.g. file://local.json or https://user:pass@couch.db/database/my_doc)
        """
        f_handle = file_from_url(url)
        return cls.parse_string(f_handle.read())


class WorkerConfigurationDocument(Document):
    def datasource_config(self):
        if "datasource" in self and isinstance(self["datasource"], dict):
            cfg = {"async": False, "interval": 5.0, "observables": {}}
            cfg.update(self["datasource"])
            return cfg
        else:
            return None

    def generate_tags(self, boss_name):
        """Add boss/configuration specific tags to the HERO."""
        if "tags" not in self:
            self["tags"] = []
        self["tags"].append(f"BOSS: {boss_name}")

    def build_hero_for_worker(self, boss_name: str, worker_object, realm="heros"):
        # replace special string for asyncio loop and multiprocess pool
        self.generate_tags(boss_name)

        for key, val in self["arguments"].items():
            if val == "@_boss_loop":
                self["arguments"][key] = worker_object._loop

            if isinstance(val, str) and val.startswith("$"):
                self["arguments"][key] = get_remote_hero(val[1:], realm=realm)

        base_config = {
            "classname": self["classname"],
            "arg_dict": self.get("arguments", {}),
            "extra_decorators": self.get("extra_decorators", {}),
            "name": self["_id"],
            "realm": realm,
            "tags": self["tags"],
        }

        if (datasource_config := self.datasource_config()) is not None:
            if datasource_config["async"]:
                return DatasourceHEROFactory.build(
                    **base_config,
                    observables=datasource_config["observables"],
                )
            else:
                return PolledDatasourceHEROFactory.build(
                    **base_config,
                    loop=worker_object._loop,
                    interval=datasource_config["interval"],
                    observables=datasource_config["observables"],
                )
        else:
            return HEROFactory.build(**base_config)
