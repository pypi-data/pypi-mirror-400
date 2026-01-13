import contextlib
import inspect
import sys
import uuid
from typing import Any, Iterator, Callable

from .context import current_activity
from .scopes import ActivityScope
from . import tag



@contextlib.contextmanager
def log_activity(
        name: str | None = None,
        message: str | None = None,
        snapshot: dict[str, Any] | None = None,
        tags: set[str] | None = None
) -> Iterator[ActivityScope]:
    """This function logs telemetry for an activity scope. It returns the activity scope that provides additional APIs."""
    from _reusable import Node
    stack = inspect.stack(2)
    frame = stack[2]
    scope = ActivityScope(name=name or frame.function, frame=frame)
    parent = current_activity.get()
    # The UUID needs to be created here,
    # because for some stupid pythonic reason creating a new Node isn't enough.
    token = current_activity.set(Node(value=scope, parent=parent, id=uuid.uuid4()))
    try:
        scope.log_trace(
            name="begin",
            message=message,
            snapshot=snapshot,
            tags=(tags or set()) | {tag.AUTO}
        )
        yield scope
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type is not None:
            scope.log_error(message=f"Unhandled <{exc_type.__name__}> has occurred: <{str(exc_value) or 'N/A'}>", tags={tag.AUTO, tag.UNHANDLED})
        raise
    finally:
        scope.log_end(tags={tag.AUTO})
        current_activity.reset(token)


def log_resource(
        name: str,
        message: str | None = None,
        snapshot: dict[str, Any] | None = None,
        tags: set[str] | None = None
) -> Callable[[], None]:
    """This function logs telemetry for a resource. It returns a function that logs the end of its usage when called."""
    scope = log_activity(name, message, snapshot, (tags or set()) | {tag.RESOURCE})
    scope.__enter__()

    def dispose():
        scope.__exit__(None, None, None)

    return dispose
