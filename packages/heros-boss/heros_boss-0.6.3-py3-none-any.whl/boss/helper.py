import importlib
import urllib
import urllib.request
import base64
from io import IOBase
import time

from heros import RemoteHERO
from heros.helper import get_logger

log = get_logger("boss")


def get_module(path, relative_path=None):
    module_name = ".".join([relative_path, path]) if relative_path is not None else path
    module = importlib.import_module(module_name)
    return module


def get_class_by_name(name, relative_path=None):
    """
    Resolve class by name

    :param name: (str) "%s.%s" % (module.name, class.name)
    :return: (class)
    """
    assert name is not None

    module_path, class_name = name.rsplit(".", 1)

    module__ = get_module(module_path, relative_path=relative_path)
    class_ = getattr(module__, class_name)
    return class_


def file_from_url(url: str) -> IOBase:
    """
    Load content from a file specified by a URL.

    This can be every type of URL supported by pythons urllib
    (e.g. http://, file://, etc ). Giving the basic auth credentials in the URL in the form
    http://user:password@hostname:port/path is supported.

    Returns:
        file handle on the file
    """
    parsed = urllib.parse.urlparse(url)

    if parsed.username and parsed.password:
        request = urllib.request.Request(parsed._replace(netloc=parsed.netloc.split("@")[1]).geturl())
        base64string = base64.b64encode(bytes("%s:%s" % (parsed.username, parsed.password), "ascii"))
        request.add_header("Authorization", "Basic %s" % base64string.decode("utf-8"))
        f_handle = urllib.request.urlopen(request)
    else:
        f_handle = urllib.request.urlopen(url)

    return f_handle


def extend_none_allowed_list(list1: list | None, list2: list | None) -> list | None:
    """Extend a list with another list which both can be None.

    If one of the lists is None, the other list is returned. If both lists are None, None is returned.

    Args:
        list1: list to extend
        list2: list to extend with
    """
    if list1 is None:
        return list2
    if list2 is None:
        return list1
    return list1 + list2


def get_remote_hero(name: str, realm: str, trials: int = 10, delay: float = 1.0):
    """Try multiple times to get RemoteHERO.

    Args:
        name: name of the remote HERO.
        realm: realm of the remote HERO.
        trials: number of trials before giving up
        delays: time delay between trials in seconds.
    """

    for i in range(trials):
        try:
            return RemoteHERO(name, realm)
        except Exception:
            log.warning(f"Could not get RemoteHERO {name} in trial {i + 1}/{trials}.")
        time.sleep(delay)

    raise NameError(f"Could not get HERO {name} after {trials} trials! Giving up.")
