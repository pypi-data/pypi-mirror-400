"""
Execution unit interface
with Execution Unit Execution parameters and Validation Result
"""

from typing import List
from abc import ABC, abstractmethod, ABCMeta
from opsorchestrator.core.model.data import DataModel
from opsorchestrator.core.model.intent import IntentElement
from opsorchestrator.core.decorator.class_decorators import classproperty
from opsorchestrator.logger.local import get_console_logger
from opsorchestrator.core.events import EmittedMessage, StatusCodes, EventContract

logger = get_console_logger("ExecutionUnit")


class NoOverrideMeta(ABCMeta):
    def __new__(mcs, name, bases, namespace):
        for base in bases:
            if hasattr(base, "execute_wrapper") and "execute_wrapper" in namespace:
                raise TypeError(f"{name} is not allowed to override 'execute_wrapper'")
            if hasattr(base, "emit") and "emit" in namespace:
                raise TypeError(f"{name} is not allowed to override 'emit'")
        return super().__new__(mcs, name, bases, namespace)


class ExecutionUnit(ABC, metaclass=NoOverrideMeta):
    """
    Execution Unit Interface
    """

    _operation_id = None
    _user_session_id = None
    _operation_name = None

    @classproperty
    def name(cls) -> str:
        """The name of an execution unit"""
        raise NotImplementedError("Name was never defined")

    @classproperty
    def data_model(cls) -> DataModel:
        raise NotImplementedError("Subclasses must define .data_model")

    @classproperty
    def intents(cls) -> List[IntentElement]:
        return []

    @classproperty
    def unique_name(self) -> str:
        return self.__name__ if isinstance(self, type) else self.__class__.__name__

    @classmethod
    def announce(cls, status_code: StatusCodes, message: str):
        cls.emit({"status": status_code, "text": message})

    @classmethod
    def emit(cls, message: EmittedMessage):
        print(message)

    @classmethod
    @abstractmethod
    def execute(
        cls,
        operation_name: str,
        operation_id: str,
        user_session_id: str,
        required_data: dict,
    ):  # to be done; Arguments has to be passed from upper layer not accessed via sub_operation or operation
        """Should provide concrete implementation for execution"""
        raise NotImplementedError("Execution unit has to implement execute method")
