# pylint: disable=no-self-argument
"""
Operation Interface
"""
from abc import ABC
from typing import List, Optional, TYPE_CHECKING
import uuid
from opsorchestrator.core.decorator.class_decorators import classproperty
from opsorchestrator.core.operation.result import OperationResult
from opsorchestrator.logger.local import get_console_logger

if TYPE_CHECKING:
    from opsorchestrator.core.model.data import DataModel
    from opsorchestrator.core.model.intent import IntentModel
logger = get_console_logger("Operation")


class Operation(ABC):
    """Abstract base class defining the interface for an Operation."""

    def __init__(
        self,
        data_storage,
        user_session_id: Optional[str] = None,
        queue: Optional[str] = None,
        operation_id: Optional[str] = None,
    ):
        self._id = operation_id or str(uuid.uuid4())
        self._user_session_id = user_session_id
        self._queue = queue
        self._result = OperationResult(self, data_storage)

    @classproperty
    def name(cls) -> str:
        raise NotImplementedError("Subclasses must define .name")

    @classproperty
    def title(cls) -> str:
        raise NotImplementedError("Subclasses must define .title")

    @classproperty
    def description(cls) -> str:
        raise NotImplementedError("Subclasses must define .description")

    @classproperty
    def timeout(cls) -> int:
        raise NotImplementedError("Subclasses must define .timeout")

    @classproperty
    def result_expiration_period(cls) -> int:
        raise NotImplementedError("Subclasses must define .result_expiration_period")

    @classproperty
    def data_model(self) -> DataModel:
        raise NotImplementedError("Subclasses must define .data_model")

    @classproperty
    def intent_model(cls) -> IntentModel:
        return IntentModel([])

    @classproperty
    def unique_name(cls) -> str:
        return cls.__name__

    @property
    def id(
        self,
    ) -> str:  # Justification: id is acceptable name, pylint: disable=invalid-name
        """The Unique Identifier of an Operation"""
        return self._id

    @property
    def user_session_id(self) -> Optional[str]:
        """The Unique Identifier of an Execution"""
        return self._user_session_id

    @property
    def queue(self):
        return None

    @property
    def result(self):
        return self._result
