"""nc4_tools._logging - Add TRACE logging level and trace() logging function."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# monkey patch TRACE level into logging
TRACE = 5
logging._levelToName[TRACE] = "TRACE"
logging._nameToLevel["TRACE"] = TRACE

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import TracebackType
    from typing import Union

    from typing_extensions import TypeAlias

    # pulled from typeshed
    _SysExcInfoType: TypeAlias = Union[
        tuple[type[BaseException], BaseException, TracebackType], tuple[None, None, None]
    ]
    _ExcInfoType: TypeAlias = Union[None, bool, _SysExcInfoType, BaseException]

    def trace(
        logger: logging.Logger,
        msg: object,
        *args: object,
        exc_info: _ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        """Log 'msg % args' with severity 'TRACE'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "very specific problem", exc_info=1)
        """
else:

    def trace(logger, msg, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if logger.isEnabledFor(TRACE):
            logger._log(TRACE, msg, args, **kwargs)
