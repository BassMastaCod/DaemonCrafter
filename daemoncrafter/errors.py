from typing import Optional


class DaemonError(Exception):
    def __init__(self, message: Optional[str] = None, service_name: Optional[str] = None):
        super().__init__(message)
        self.service_name = service_name


class ServiceMissing(DaemonError):
    pass


class ServiceNotRunning(DaemonError):
    pass


class ServiceAlreadyRunning(DaemonError):
    pass
