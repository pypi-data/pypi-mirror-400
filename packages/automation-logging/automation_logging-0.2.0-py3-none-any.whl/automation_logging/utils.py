import logging
import inspect
import os
from typing import Any


def _is_automation_logging(frame_path: str) -> bool:
    frame_module = os.path.basename(os.path.dirname(frame_path))
    frame_filename = os.path.basename(frame_path)
    return "automation_logging" in frame_module and "profiler" not in frame_filename


def get_frame_info() -> str:
    """Get frame info from the last frame before entering automation_logging modules"""

    frame = inspect.currentframe()
    if frame is None:
        return "-"

    target_frame = frame
    try:
        while frame:
            if _is_automation_logging(inspect.getfile(frame)):
                target_frame = frame
            frame = frame.f_back
        target_frame = target_frame.f_back
        frame_data: dict[str, Any] = {"module": "_", "function": "_", "lineno": "_"}
        if target_frame is not None:
            frame_data["module"] = inspect.getmodulename(inspect.getfile(target_frame))
            frame_data["lineno"] = inspect.getlineno(target_frame)
            frame_data["function"] = target_frame.f_code.co_name
    finally:
        del frame
        del target_frame

    if len(frame_data) == 0:
        return "-"
    return f"{frame_data['module']}.{frame_data['function']}:{frame_data['lineno']}"


def add_logging_level(levelName: str, levelNum: int, methodName: str | None = None) -> None:
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    Parameters
    ----------
    levelName : str
        Name of the new logging level.

    levelNum : int
        Numeric value assigned to the new logging level.

    methodName : str, optional
        Name of the convenience method for the new logging level. If not specified,
        `levelName.lower()` is used.

    Returns
    -------
    None

    Examples
    --------
    >>> add_logging_level('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    Notes
    -----
    This method was extracted from:
    https://stackoverflow.com/q/2183233/35804945#35804945
    The behavior was modified to return None if the level is already defined
    instead of throwing an exception, allowing re-initialization of the log.
    """
    if not methodName:
        methodName = levelName.lower()

    if (
        hasattr(logging, levelName)
        or hasattr(logging, methodName)
        or hasattr(logging.getLoggerClass(), methodName)
    ):
        return None

    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)
