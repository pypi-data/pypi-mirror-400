from multiprocessing import Process, Pipe, cpu_count
import asyncio
import platform
import signal
from .helper import log
from .multiprocess import MultiprocessRPC


def get_max_workers() -> int:
    """
    Get the maximum number of worker processes to use.

    For Windows systems, caps the worker count at 32.
    For other platforms, returns the total CPU count.

    Returns:
        The maximum number of worker processes to use
    """
    if platform.system() == "Windows":
        return min([int(cpu_count()), 32])
    else:
        return int(cpu_count())


def start_hero_in_worker(config, realm, boss_name, boss_loop):
    """
    This launcher to start a new worker in it's own process
    """
    parent_conn, child_conn = Pipe()
    p = Process(target=launch_worker, args=(config, realm, boss_name, child_conn))
    p.start()
    return {"process": p, "worker": WorkerRemote(boss_loop, parent_conn)}


def launch_worker(config, realm, boss_name, pipe):
    """
    This is the entry point in the worker.
    """
    worker = Worker(config, realm, boss_name, pipe)

    def exit_gracefully(*args):
        log.info(f"Stopping worker for HERO {boss_name}")
        worker.stop()

    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGINT, exit_gracefully)
    # only register SIGHUP if it exists on this platform
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, exit_gracefully)

    worker.run()

    log.info(f"Worker for HERO {config['_id']} finished")


class Worker(MultiprocessRPC):
    def __init__(self, config, realm, boss_name, pipe):
        log.info(f"Worker for HERO {config['_id']} starting")

        # generate asyncio loop to be used by the child HEROs
        self._loop = asyncio.new_event_loop()

        self._obj = config.build_hero_for_worker(boss_name, self, realm)

        MultiprocessRPC.__init__(self, self._loop, pipe)

    def run(self):
        log.debug(f"starting worker main loop for {self._obj}")
        self._loop.run_forever()

    def stop(self):

        if hasattr(self._obj, "_teardown") and callable(getattr(self._obj, "_teardown")):
            self._obj._teardown(self)

        self._obj._destroy_hero()

        del self._obj
        self._rpc_stop()
        self._loop.stop()


class WorkerRemote(MultiprocessRPC):
    def stop(self):
        self._rpc("stop")
