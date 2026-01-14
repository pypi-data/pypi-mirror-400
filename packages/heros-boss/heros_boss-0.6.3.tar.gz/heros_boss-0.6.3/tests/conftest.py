import pytest
import os
from unittest import mock
import json
import time
from heros.zenoh import session_manager as default_session_manager


@pytest.fixture()
def default_starter_env():
    boss_config = json.dumps(
        {
            "_id": "test_dev",
            "classname": "boss.dummies.Dummy",
            "arguments": {},
            "tags": ["test_tag"],
        }
    )
    boss_config2 = json.dumps({"_id": "test_dev2", "classname": "boss.dummies.Dummy", "arguments": {}})
    with mock.patch.dict(os.environ, {"BOSS1": boss_config, "BOSS2": boss_config2}):
        yield


@pytest.fixture()
def herosdevices_starter_env():
    boss_config = json.dumps(
        {
            "_id": "camera_dummy",
            "classname": "herosdevices.hardware.dummy.cameras.CameraDummy",
            "arguments": {
                "keep_device_open": True,
                "config_dict": {"default": {"height": 600, "width": 800, "frame_count": 3}},
            },
        }
    )
    with mock.patch.dict(os.environ, {"BOSS1": boss_config, "BOSS_PIP_PKGS": "herosdevices", "BOSS_APT_PKGS": "gcc"}):
        yield


@pytest.fixture()
def decorated_starter_env():
    boss_config = json.dumps(
        {
            "_id": "test_dev_decorated",
            "classname": "boss.dummies.Dummy",
            "arguments": {},
            "extra_decorators": [
                ("read_temp", "heros.event"),
                ("_secret_hello", "heros.inspect.force_remote"),
                ("hello", "heros.inspect.mark_local_only"),
            ],
            "tags": ["test_tag"],
        }
    )
    with mock.patch.dict(os.environ, {"BOSS_DECORATED": boss_config}):
        yield


@pytest.fixture()
def dependent_hero_env():
    config_main = json.dumps(
        {
            "_id": "mainhero",
            "classname": "boss.dummies.Dummy",
            "arguments": {}
        }
    )
    config_sub = json.dumps(
        {
            "_id": "subhero",
            "classname": "boss.dummies.DependentDummy",
            "arguments": {"parent_hero": "$mainhero"}
        }
    )
    with mock.patch.dict(os.environ, {"MAINHERO": config_main, "SUBHERO": config_sub}):
        yield

@pytest.fixture(scope="session")
def cleanup():
    cleanups = {"boss": [], "heros": []}
    yield cleanups
    for hero in cleanups["heros"]:
        hero._destroy_hero()
    for process, boss in cleanups["boss"]:
        try:
            for hero in boss.status():
                boss.stop_hero(hero)
            boss._destroy_hero()
        except Exception:
            print("Error stopping BOSS")
            pass
        process.terminate()
    for process, boss in cleanups["boss"]:
        i = 0
        while process.poll() is None and i < 30:
            time.sleep(0.1)
            i += 1
        process.kill()
    del cleanups
    default_session_manager.force_close()
