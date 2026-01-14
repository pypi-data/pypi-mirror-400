from heros import LocalHERO, RemoteHERO, LocalDatasourceHERO, PolledLocalDatasourceHERO
from heros.inspect import force_remote
from .helper import get_class_by_name, log, extend_none_allowed_list

import asyncio
from abc import abstractmethod
from typing import Any, Callable


class BOSSObject:
    def __init__(self):
        # calling setup hook if it exists
        if hasattr(self, "_setup") and callable(getattr(self, "_setup")):
            self._setup()

    @force_remote
    def _stop(self, boss: RemoteHERO):
        # calling teardown hook if it exists
        if hasattr(self, "_teardown") and callable(getattr(self, "_teardown")):
            self._teardown()

        self._destroy_hero()
        del self


class Factory:
    @classmethod
    def _build(
        cls,
        classname: str,
        name: str,
        arg_dict: dict | None = None,
        extra_decorators: dict | None = None,
        realm="heros",
        session_manager=None,
        tags: list | None = None,
    ):
        arg_dict = arg_dict or {}
        extra_decorators = extra_decorators or {}
        log.debug(f"building object of class {classname}")

        # if mixin classes are defined, we have to generate a modified class with the mixins
        tmp_classname = f"{classname}_HERO"
        log.debug(f"adding LocalHERO mixin to {classname} -> {tmp_classname}")

        # apply custom decortors to methods of the source class
        # how this is done is up to the mixin-class specific implementations
        source_class = get_class_by_name(classname)
        source_class = cls._decorate_methods(source_class, extra_decorators)

        target_class = type(
            tmp_classname,
            (
                source_class,
                cls._mixin_class,
                BOSSObject
            ),
            {},
        )

        # we need to replace the constructor to call the constructor of all super classes
        target_class.__init__ = cls._get_init_replacement(classname, name, realm, session_manager, tags)

        return target_class(**arg_dict)

    @classmethod
    @abstractmethod
    def _get_init_replacement(
        cls, classname: str, name: str, realm: str, session_manager, tags: list | None
    ) -> Callable:
        return lambda x: x

    @staticmethod
    def _decorate_methods(source_class: Any, extra_decorators: list[tuple[str, str]]) -> Any:
        """
        Wrap methods on the class before instantiation.
        """
        for method_name, decorator_path in extra_decorators:
            log.debug(f"Decorating {source_class}.{method_name} with {decorator_path}")
            module, _, _decorator_name = decorator_path.rpartition(".")
            if not module:
                log.error(f"Invalid decorator path: '{decorator_path}' — must include module and name!")
                continue
            try:
                deco = get_class_by_name(decorator_path)
            except (ImportError, AttributeError):
                log.exception(f"Could not load module {decorator_path} for decoration!")
                continue
            method = getattr(source_class, method_name, None)
            if method is None:
                log.error(f"Could not decorate! {method_name} is no method of {source_class}!")
                continue
            setattr(source_class, method_name, deco(method))
        return source_class


class HEROFactory(Factory):
    _mixin_class = LocalHERO

    @classmethod
    def build(
        cls,
        classname: str,
        name: str,
        arg_dict: dict | None = None,
        extra_decorators: dict | None = None,
        realm="heros",
        session_manager=None,
        tags: list | None = None,
    ):
        arg_dict = arg_dict or {}
        extra_decorators = extra_decorators or {}
        return cls._build(classname, name, arg_dict, extra_decorators, realm, session_manager, tags)

    @classmethod
    def _get_init_replacement(
        cls, classname: str, name: str, realm: str, session_manager, tags: list | None
    ) -> Callable:
        def _init_replacement(
            self, *args, _realm=realm, _session_manager=session_manager, _tags: list | None = None, **kwargs
        ):
            get_class_by_name(classname).__init__(self, *args, **kwargs)
            _tags = extend_none_allowed_list(_tags, tags)
            cls._mixin_class.__init__(self, name, realm=_realm, session_manager=_session_manager, tags=_tags)
            BOSSObject.__init__(self)

        return _init_replacement


class DatasourceHEROFactory(HEROFactory):
    _mixin_class = LocalDatasourceHERO

    @classmethod
    def build(
        cls,
        classname: str,
        name: str,
        arg_dict: dict | None = None,
        extra_decorators: dict | None = None,
        observables: dict | None = None,
        realm="heros",
        session_manager=None,
        tags: list | None = None,
    ):
        arg_dict = arg_dict or {}
        extra_decorators = extra_decorators or {}
        observables = observables or {}
        cls._observables = observables
        return cls._build(classname, name, arg_dict, extra_decorators, realm, session_manager, tags)

    @classmethod
    def _get_init_replacement(
        cls, classname: str, name: str, realm: str, session_manager, tags: list | None
    ) -> Callable:
        def _init_replacement(
            self, *args, _realm=realm, _session_manager=session_manager, _tags: list | None = None, **kwargs
        ):
            get_class_by_name(classname).__init__(self, *args, **kwargs)
            _tags = extend_none_allowed_list(_tags, tags)
            cls._mixin_class.__init__(
                self, name, realm=_realm, session_manager=_session_manager, tags=_tags, observables=cls._observables
            )
            BOSSObject.__init__(self)

        return _init_replacement


class PolledDatasourceHEROFactory(Factory):
    _mixin_class = PolledLocalDatasourceHERO

    @classmethod
    def build(
        cls,
        classname: str,
        name: str,
        arg_dict: dict | None = None,
        extra_decorators: dict | None = None,
        loop: asyncio.AbstractEventLoop = asyncio.new_event_loop(),
        interval: float = 5,
        observables: dict | None = None,
        realm="heros",
        session_manager=None,
        tags: list | None = None,
    ):
        arg_dict = arg_dict or {}
        extra_decorators = extra_decorators or {}
        observables = observables or {}
        cls._loop = loop
        cls._interval = interval
        cls._observables = observables
        return cls._build(classname, name, arg_dict, extra_decorators, realm, session_manager, tags)

    @classmethod
    def _get_init_replacement(
        cls, classname: str, name: str, realm: str, session_manager, tags: list | None
    ) -> Callable:
        def _init_replacement(
            self, *args, _realm=realm, _session_manager=session_manager, _tags: list | None = None, **kwargs
        ):
            get_class_by_name(classname).__init__(self, *args, **kwargs)
            _tags = extend_none_allowed_list(_tags, tags)
            cls._mixin_class.__init__(
                self,
                name,
                realm=_realm,
                loop=cls._loop,
                interval=cls._interval,
                session_manager=_session_manager,
                observables=cls._observables,
                tags=_tags,
            )
            BOSSObject.__init__(self)

        return _init_replacement
