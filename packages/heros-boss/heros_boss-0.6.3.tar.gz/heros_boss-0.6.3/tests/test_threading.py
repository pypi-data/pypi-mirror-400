import subprocess
from threading import Thread
import time

from heros import RemoteHERO


def test_threading_blocking(default_starter_env, cleanup):
    boss_processes = [
        subprocess.Popen(
            [
                "python",
                "-m",
                "boss.starter",
                "-e",
                "BOSS1",
                "-e",
                "BOSS2",
                "--expose",
                "--log=debug",
                "--name=test_boss",
            ],
        )
    ]
    time.sleep(3)
    boss = RemoteHERO("test_boss")
    boss.start_all()
    time.sleep(1)
    cleanup["boss"].append([boss_processes[0], boss])

    def make_blocking_call_in_thread(test_dev):
        # Makes a blocking call. Since this call is synchronous, it will block our client side too and we better
        # run it in a thread.

        test_dev.blocking_call(8)

    test_dev = RemoteHERO("test_dev")
    test_dev2 = RemoteHERO("test_dev2")
    cleanup["heros"] += [test_dev, test_dev2]

    thread = Thread(target=make_blocking_call_in_thread, args=(test_dev, ))
    thread.start()

    time.sleep(1)
    assert test_dev2.hello() == "world"

    thread.join()


def test_dependent_heros(dependent_hero_env, cleanup):
    boss_processes = [
        subprocess.Popen(
            [
                "python",
                "-m",
                "boss.starter",
                "-e",
                "MAINHERO",
                "-e",
                "SUBHERO",
                "--expose",
                "--log=debug",
                "--name=test_boss",
            ],
        )
    ]
    time.sleep(3)
    boss = RemoteHERO("test_boss")
    boss.start_all()
    time.sleep(1)
    cleanup["boss"].append([boss_processes[0], boss])


    mainhero = RemoteHERO("mainhero")
    subhero = RemoteHERO("subhero")
    cleanup["heros"] += [mainhero, subhero]

    subhero.update_parent_testme(42)
    assert mainhero.testme == 42
