import asyncio
import uuid
from heros.helper import log

POLLING_INTERVAL = 0.01


class Message:
    fields = ["id", "type"]

    def __init__(self, *args, **kwargs):
        super().__init__()
        if hasattr(super().__thisclass__, "fields"):
            self.fields += super().__thisclass__.fields

        kwargs["type"] = self.TYPE
        if "id" not in kwargs:
            kwargs["id"] = int(uuid.uuid4())

        for field in self.fields:
            value = kwargs[field] if field in kwargs else None
            setattr(self, field, value)

    def _decode(self, raw_message):
        if raw_message["type"] != self.TYPE:
            raise ValueError
        for field in self.fields:
            setattr(self, field, raw_message[field])

    def encode(self):
        return {key: getattr(self, key) for key in self.fields}

    @staticmethod
    def parse(raw_message):
        for cls in [MethodCallMessage, ResultMessage, ErrorMessage, AttributeGetMessage, AttributeSetMessage]:
            try:
                message = cls()
                message._decode(raw_message)
                return message
            except ValueError:
                pass


class MethodCallMessage(Message):
    TYPE = "c"
    fields = ["method", "args", "kwargs"]


class AttributeGetMessage(Message):
    TYPE = "g"
    fields = ["name"]


class AttributeSetMessage(Message):
    TYPE = "s"
    fields = ["name", "value"]


class ResultMessage(Message):
    TYPE = "r"
    fields = ["payload"]


class ErrorMessage(Message):
    TYPE = "e"
    fields = ["error"]


class MultiprocessRPC:
    """
    Use the communication between two processes via a pipe to implement RPC.

    In BOSS this is used to communicate between the BOSS object in the main process and the BOSSRemote
    running in a separate process. This becomes necessary since zenoh/rust/pyO3 does not allow to run
    in the main process and in dynamically generated processes.
    """
    def __init__(self, loop, pipe):
        self._loop = loop
        self._pipe = pipe

        self._pending_results = {}
        self._shutdown = False

        self._communicatation_task = self._loop.create_task(self._communicate())

    async def _communicate(self):
        while not self._shutdown:
            if self._pipe.poll():
                try:
                    self._handle_message(self._pipe.recv())
                except EOFError:
                    pass

            await asyncio.sleep(POLLING_INTERVAL)

    def _send_message(self, message):
        try:
            self._pipe.send(message.encode())
        except BrokenPipeError:
            pass

    def _handle_message(self, message):
        msg = Message.parse(message)

        if isinstance(msg, MethodCallMessage):
            try:
                result = getattr(self, msg.method)(*msg.args, **msg.kwargs)
                self._send_message(ResultMessage(id=msg.id, payload=result))
            except Exception as e:
                log.error(f"Error {e}")
                self._send_message(ErrorMessage(id=msg.id, error=e))

        if isinstance(msg, ResultMessage):
            if msg.id in self._pending_results:
                self._pending_results[msg.id](msg.payload)
                del self._pending_results[msg.id]

        if isinstance(msg, AttributeGetMessage):
            if hasattr(self, msg.name):
                self._send_message(ResultMessage(id=msg.id, payload=getattr(self, msg.name)))

        if isinstance(msg, AttributeSetMessage):
            setattr(self, msg.name, msg.value)

        if isinstance(msg, ErrorMessage):
            raise msg.error

    def _rpc(self, method_name, *args, _cb=None, **kwargs):
        msg = MethodCallMessage(method=method_name, args=args, kwargs=kwargs)

        if _cb is None: 
            def _cb(payload):
                pass

        self._pending_results.update({msg.id: _cb})
        self._send_message(msg)

    def _get_attribute(self, name: str, local_name: str | None = None):
        if local_name is None:
            local_name = name

        def _update_attribute(payload):
            setattr(self, local_name, payload)

        msg = AttributeGetMessage(name=name)
        self._pending_results.update({msg.id: _update_attribute})
        self._send_message(msg)

    def _set_attribute(self, name: str, value: object):
        self._send_message(AttributeSetMessage(name=name, value=value))

    def _rpc_stop(self):
        self._communicatation_task.cancel()
        self._shutdown = True
