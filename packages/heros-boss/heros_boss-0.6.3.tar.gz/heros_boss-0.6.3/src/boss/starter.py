import argparse
import sys
import os
import asyncio
import platform
import uuid
import signal
from multiprocessing import Pipe

from .helper import log
from .worker import start_hero_in_worker
from .boss import BOSS
from .configuration import WorkerConfigurationDocument
from .container import is_in_container, prepare_container


def create_unique_instance_name() -> str:
    """
    Creates a unique instance identifier consisting of the hostname and an UUID.

    Returns:
        A unique identifier.
    """
    short_uuid = str(uuid.uuid4()).split("-")[0]
    hostname = platform.node()
    return f"{hostname}_{short_uuid}"


def run(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="info", help="loglevel: spam < debug < info")
    parser.add_argument("--expose", action="store_true", help="whether the BOSS object should expose itself as HERO")
    parser.add_argument("--realm", default="heros", help="Realm under which the HEROs should be exposed")
    parser.add_argument("--no-autostart", action="store_true", help="turn off autostart")
    parser.add_argument(
        "--name",
        default=create_unique_instance_name(),
        help="name of the BOSS instance. This needs to be unique of the BOSS object is exposed",
    )
    parser.add_argument(
        "-u", "--url", action="append", default=[], help="Path to configuration file or url of database"
    )
    parser.add_argument(
        "-e",
        "--env",
        action="append",
        default=["BOSS"],
        help="name of the environment variable storing the configuration",
    )

    if is_in_container():
        if prepare_container():
            os.execl(sys.executable, sys.executable, "-m", __spec__.name, *sys.argv[1:])

    args = parser.parse_args(args)
    log.setLevel(args.log)

    if not (args.url or args.env):
        parser.error("Either --url or --env have to be specified")

    # generate asyncio loop and process pool executor
    # both can be passed to the child HEROs
    loop = asyncio.new_event_loop()

    parent_conn = None
    # create BOSS object
    if args.expose:
        parent_conn, child_conn = Pipe()
        config = WorkerConfigurationDocument()
        config.update({
            "_id": args.name,
            "classname": "boss.boss.BOSSRemote",
            "arguments": {"loop": '@_boss_loop', 'pipe': child_conn},
        })

        boss_remote = start_hero_in_worker(config, args.realm, args.name, loop)

    boss = BOSS(name=args.name, configs=[], loop=loop, realm=args.realm, remote_pipe=parent_conn)

    if len(args.url) > 0:
        log.info("Reading device(s) from %s ", args.url)
        for url in args.url:
            boss.add_hero_source(WorkerConfigurationDocument.parse_url, url)

    if len(args.env) > 0:
        for var in args.env:
            if var in os.environ:
                boss.add_hero_source(WorkerConfigurationDocument.parse_string, os.environ[var])

    boss.refresh_hero_sources(auto_start=not args.no_autostart)

    # to set the loggers of the started objects we have to set them globally
    log.setLevel(args.log, globally=True)

    log.info("Starting BOSS")

    def exit_gracefully(*arguments):
        log.info("Stopping BOSS...")
        if args.expose:
            boss_remote["worker"].stop()
            boss_remote["process"].join(5)
            boss_remote["process"].terminate()

        boss.stop_all()
        loop.stop()

        log.info("Exited BOSS")
        sys.exit()

    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGINT, exit_gracefully)
    # only register SIGHUP if it exists on this platform
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, exit_gracefully)

    # start asyncio mainloop
    loop.run_forever()


if __name__ == "__main__":
    run()
