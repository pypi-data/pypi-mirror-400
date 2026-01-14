from .helper import log
from .configuration import WorkerConfigurationDocument
from .worker import start_hero_in_worker
import asyncio
import time
from collections.abc import Callable
from .multiprocess import MultiprocessRPC, POLLING_INTERVAL


class BOSS(MultiprocessRPC):
    hero_config_sources: list

    def __init__(self, name: str, configs: list, loop: asyncio.AbstractEventLoop, realm: str, remote_pipe=None):
        """
        A BOSS object.

        Args:
            name: name of the Boss object
            loop: asyncio event loop that can be used to schedule tasks
            configs: List of WorkerConfigurationDocuments to specify the workers
            realm: Name of the realm the BOSS starts their HEROs in.
        """
        self.name = name
        self.heros: dict = {}
        self.workers: dict = {}
        self.hero_config_sources: list = []
        self._loop = loop
        self.realm = realm

        self.start_all()

        if remote_pipe is not None:
            MultiprocessRPC.__init__(self, loop, remote_pipe)

    def _config_from_name(self, name):
        if name not in self.heros:
            raise NameError(f"HERO with name {name} not run by this BOSS. Available HEROs are {self.heros.keys()}")
        return self.heros[name]["config"]

    def add_hero_source(self, parser: Callable[[str], WorkerConfigurationDocument], target: str):
        """
        Adds a data source to the BOSS from which HERO configurations are loaded.

        Args:
            parser: A function which takes :code:`target` as an argument and returns a
                :py:class:`boss.configuration.WorkerConfigurationDocument` dict with the HERO config information.
            target: Target for the :code:`parser`, for example an URL for
                :py:meth:`boss.configuration.WorkerConfigurationDocument.parse_url`
        """
        self.hero_config_sources.append([parser, target])

    def refresh_hero_sources(self, auto_start: bool = True):
        """
        Refresh the HERO configuration data from the registered sources, updating existing HEROs, adding new ones,
        and removing those that are no longer present in the sources.
        HEROs that were running before are only restarted if their configuration changed. HEROs without configuration
        changes stay untouched.

        Args:
            auto_start: If True, automatically starts a *new* hero source if its configuration is
                       loaded. Defaults to True. Does not influence the behavior of HEROs that are already registered.

        """

        current_heros = list(self.heros.keys())

        def handle_hero_dict(config: dict):
            if config is not None:
                if "rows" in config:
                    for conf_row in config["rows"]:
                        if "doc" in conf_row:
                            handle_hero_dict(conf_row["doc"])
                        else:
                            handle_hero_dict(conf_row)
                elif "_id" in config:
                    name = config["_id"]
                    do_start = False
                    if name in self.heros:
                        new_conf_doc = WorkerConfigurationDocument(config)
                        new_conf_doc.generate_tags(self.name)
                        if self.heros[name]["config"] != new_conf_doc:
                            # config changed, we need to restart
                            if self.heros[name]["status"] == "running":
                                do_start = True  # was running before, auto start with the reloaded config
                                self.stop_hero(name)
                            self.heros[name]["config"] = new_conf_doc
                        current_heros.remove(name)
                    else:
                        do_start = auto_start
                    self.add_hero(config, auto_start=do_start)

        for parser, target in self.hero_config_sources:
            log.info("refreshing HERO source %s", target)
            config = parser(target)
            handle_hero_dict(config)

        for deleted_hero in current_heros:
            # hero not found in reloaded sources, delete
            log.info("Removing HERO %s from BOSS", deleted_hero)
            self.remove_hero(deleted_hero)

    def add_hero(self, config: WorkerConfigurationDocument | dict, auto_start: bool = True):
        """
        Start a new HERO and keep it running. Note that the id of the HERO specified in the config must be unique.

        Args:
            config: configuration for the new HERO. If a dict is given, it is converted into
                a WorkerConfigurationDocument.
            auto_start: If true the new HERO is immediately started after adding
        """

        if not isinstance(config, dict):
            return None
        if not isinstance(config, WorkerConfigurationDocument):
            config = WorkerConfigurationDocument(config)

        name = config["_id"]

        if name not in self.heros:
            self.heros[name] = {"config": config, "object": None, "status": "stopped"}

        if auto_start:
            self.start_hero(name)

    def start_hero(self, name):
        """
        Start HERO with given name.
        """
        config = self._config_from_name(name)
        status = self.heros[name]["status"]

        if status not in "running":
            try:
                self.workers[name] = start_hero_in_worker(config, self.realm, self.name, self._loop)
                log.info(f"creating HERO with name {config['_id']} from class {config['classname']}")

                self.heros[name]["status"] = "running"

            except KeyError as e:
                log.debug("", exc_info=True)
                log.error(f"creating HERO with invalid dict: {config} failed:  {e}")
            except Exception as e:
                log.debug("", exc_info=True)
                log.error(f"creating HERO with name {config['_id']} from class {config['classname']} failed: {e}")

    def stop_hero(self, name: str):
        config = self._config_from_name(name)
        status = self.heros[name]["status"]

        if status == "running":
            log.info(f"destroying HERO with name {config['_id']} from class {config['classname']}")
            
            self.workers[name]["worker"].stop()
            self.workers[name]["process"].join(5)
            self.workers[name]["process"].terminate()
            del self.workers[name]

            self.heros[name]["status"] = "stopped"

    def restart_hero(self, name: str):
        self.stop_hero(name)
        self.start_hero(name)

    def remove_hero(self, name: str):
        self.stop_hero(name)

        if name in self.heros:
            del self.heros[name]

    def start_all(self):
        for hero_name in self.heros.keys():
            self.start_hero(hero_name)

    def stop_all(self):
        for hero_name in self.heros.keys():
            self.stop_hero(hero_name)

    def status(self):
        return self.heros


class BOSSRemote(MultiprocessRPC):
    def __init__(self, *args, **kwargs):
        self._hero_config_sources = []
        super().__init__(*args, **kwargs)

    def send_message(self, message):
        self._pipe.send(message)

    def add_hero_source(self, parser: Callable[[str], WorkerConfigurationDocument], target: str):
        self._rpc("add_hero_source", parser, target)

    def refresh_hero_sources(self, auto_start: bool = True):
        self._rpc("refresh_hero_sources", auto_start)

    def add_hero(self, config: WorkerConfigurationDocument | dict, auto_start: bool = True):
        self._rpc("add_hero", config, auto_start)

    def start_hero(self, name):
        self._rpc("start_hero", name)

    def start_all(self):
        self._rpc("start_all")

    def stop_hero(self, name):
        self._rpc("stop_hero", name)

    def stop_all(self):
        self._rpc("stop_all")

    def status(self):
        self.heros = []
        self._get_attribute("heros")
        time.sleep(3*POLLING_INTERVAL)
        return self.heros

    @property
    def hero_config_sources(self):
        self._get_attribute("hero_config_sources", "_hero_config_sources")
        time.sleep(3*POLLING_INTERVAL)
        return self._hero_config_sources

    @hero_config_sources.setter
    def hero_config_sources(self, value):
        self._set_attribute("hero_config_sources", value)
