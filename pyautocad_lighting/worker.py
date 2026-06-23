import queue
import threading
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class WorkerTask:
    action: Callable[..., Any]
    args: tuple
    kwargs: dict
    on_success: Optional[Callable[[Any], None]]
    on_error: Optional[Callable[[Exception], None]]


class COMWorker:
    def __init__(self, shutdown_timeout: float = 1.0) -> None:
        self._tasks: "queue.Queue[Optional[WorkerTask]]" = queue.Queue()
        self._shutdown_timeout = shutdown_timeout
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def submit(
        self,
        action: Callable[..., Any],
        *args: Any,
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        **kwargs: Any,
    ) -> None:
        self._tasks.put(
            WorkerTask(
                action=action,
                args=args,
                kwargs=kwargs,
                on_success=on_success,
                on_error=on_error,
            )
        )

    def shutdown(self) -> None:
        """Wait briefly for the worker thread to stop after the current task completes."""
        self._tasks.put(None)
        self._thread.join(timeout=self._shutdown_timeout)

    def _run(self) -> None:
        pythoncom = None
        try:
            import pythoncom as imported_pythoncom

            pythoncom = imported_pythoncom
            pythoncom.CoInitialize()
        except ImportError:
            pass

        while True:
            task = self._tasks.get()
            if task is None:
                break
            try:
                result = task.action(*task.args, **task.kwargs)
            except Exception as exc:
                if task.on_error is not None:
                    task.on_error(exc)
            else:
                if task.on_success is not None:
                    task.on_success(result)

        if pythoncom is not None:
            pythoncom.CoUninitialize()
