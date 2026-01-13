import asyncio
import json
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Awaitable, Callable
from logging import Logger

from aiohttp import web
from typing_extensions import override

from raphson_mp.server.vars import CLOSE_RESPONSES


class ProgressMonitor(ABC):
    @abstractmethod
    def task_start(self, task: str): ...

    @abstractmethod
    def task_done(self, task: str): ...

    @abstractmethod
    def task_error(self, task: str): ...

    @abstractmethod
    def state_stopped(self): ...

    @abstractmethod
    def state_running(self): ...


class LoggerProgressMonitor(ProgressMonitor):
    start_time: dict[str, int] = {}
    logger: Logger

    def __init__(self, logger: Logger):
        self.logger = logger

    @override
    def task_start(self, task: str):
        self.start_time[task] = time.time_ns()
        self.logger.info("start: %s", task)

    @override
    def task_done(self, task: str):
        duration = (time.time_ns() - self.start_time[task]) // 1_000_000
        del self.start_time[task]
        self.logger.info("done: %s (%sms)", task, duration)

    @override
    def task_error(self, task: str):
        del self.start_time[task]
        self.logger.warning("error: %s", task, exc_info=True)

    @override
    def state_stopped(self):
        pass

    @override
    def state_running(self):
        pass


class WebProgressMonitor(ProgressMonitor):
    queue: asyncio.Queue[str]

    def __init__(self):
        self.queue = asyncio.Queue()

    @override
    def task_start(self, task: str):
        self.queue.put_nowait(json.dumps({"task": task, "state": "start"}) + "\n")

    @override
    def task_done(self, task: str):
        self.queue.put_nowait(json.dumps({"task": task, "state": "done"}) + "\n")

    @override
    def task_error(self, task: str):
        self.queue.put_nowait(json.dumps({"task": task, "state": "error"}) + "\n")

    @override
    def state_stopped(self):
        self.queue.put_nowait(json.dumps({"state": "stopped"}) + "\n")

    @override
    def state_running(self):
        self.queue.put_nowait(json.dumps({"state": "running"}) + "\n")

    async def _response_bytes(self) -> AsyncIterator[bytes]:
        while True:
            yield (await self.queue.get()).encode()

    def response(self, request: web.Request) -> web.Response:
        response = web.Response(body=self._response_bytes())
        request.config_dict[CLOSE_RESPONSES].add(response)
        return response


class RelayProgressMonitor(ProgressMonitor):
    _monitors: list[ProgressMonitor]

    def __init__(self, monitors: list[ProgressMonitor]):
        self._monitors = monitors

    @override
    def task_start(self, task: str):
        for monitor in self._monitors:
            monitor.task_start(task)

    @override
    def task_done(self, task: str):
        for monitor in self._monitors:
            monitor.task_done(task)

    @override
    def task_error(self, task: str):
        for monitor in self._monitors:
            monitor.task_error(task)

    @override
    def state_stopped(self):
        for monitor in self._monitors:
            monitor.state_stopped()

    @override
    def state_running(self):
        for monitor in self._monitors:
            monitor.state_running()


class BackgroundTask:
    _logger: Logger
    _func: Callable[[ProgressMonitor], Awaitable[None]]
    _monitors: list[ProgressMonitor]
    _progress: RelayProgressMonitor

    _task: asyncio.Task[None] | None = None

    def __init__(self, func: Callable[[ProgressMonitor], Awaitable[None]], logger: Logger):
        self._logger = logger
        self._monitors = [LoggerProgressMonitor(logger)]
        self._progress = RelayProgressMonitor(self._monitors)
        self._func = func

    def attach_monitor(self, monitor: ProgressMonitor):
        self._monitors.append(monitor)
        if self._task and not self._task.done():
            monitor.state_running()
        else:
            monitor.state_stopped()

    def start(self):
        if self._task and not self._task.done():
            return

        async def _wrapper():
            self._progress.state_running()
            try:
                await self._func(self._progress)
            except Exception:
                self._logger.exception("error in background task")
            finally:
                self._progress.state_stopped()

        self._task = asyncio.create_task(_wrapper())

    def stop(self):
        if self._task:
            self._task.cancel()
            self._task = None
            self._progress.state_stopped()
