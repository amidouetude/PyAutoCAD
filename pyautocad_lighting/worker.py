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
    def __init__(self) -> None:
        self._tasks: "queue.Queue[Optional[WorkerTask]]" = queue.Queue()
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
        self._tasks.put(None)
        self._thread.join(timeout=1)

    def _run(self) -> None:
        pythoncom = None
        try:
            import pythoncom as imported_pythoncom

            pythoncom = imported_pythoncom
            pythoncom.CoInitialize()
        except ImportError:
            pythoncom = None

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
