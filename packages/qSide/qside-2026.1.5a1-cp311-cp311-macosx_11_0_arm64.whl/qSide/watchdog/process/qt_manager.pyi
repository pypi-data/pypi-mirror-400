from . import watchdog as watchdog
from _typeshed import Incomplete
from enum import Enum
from qSide.jsonrpc_zmq import QJsonRpcPeer as QJsonRpcPeer
from qSide.qt import QObject as QObject, QProcess as QProcess, Signal as Signal

class WatchdogManager(QObject):
    class Status(Enum):
        NotRunning = 0
        Starting = 1
        Running = 2
    errorOccurred: Incomplete
    def __init__(self, zmq_addr: str, log_file: str | None = None, parent=None) -> None: ...
    def start(self, parent_pid: int): ...
    def status(self) -> Status: ...
    def stop(self) -> None: ...
