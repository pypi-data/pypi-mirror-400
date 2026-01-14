import subprocess
import time

from heros import RemoteHERO
from heros.event import RemoteEventHandler


def test_decorate(decorated_starter_env, cleanup):
    _boss_processes = [
        subprocess.Popen(
            [
                "python",
                "-m",
                "boss.starter",
                "-e",
                "BOSS_DECORATED",
                "--log=debug",
            ],
            decorated_starter_env,
        ),
    ]
    time.sleep(2)

    hero = RemoteHERO("test_dev_decorated")
    cleanup["heros"].append(hero)

    assert isinstance(hero.read_temp, RemoteEventHandler)
    assert hasattr(hero, "_secret_hello")
    assert not hasattr(hero, "hello")
