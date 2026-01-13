"""
This module defines the `EventContract` abstract base class and related
components to represent the outcome of operations in the system.

It provides a standardized structure for capturing:
    - Operation details
    - Execution status (success, partial success, failure, pending)
    - Reason for the status
    - Optional reference to the execution unit that produced the event

Components:
    - StatusCodes: Enum representing possible execution states
    - EventContract: Abstract base class for creating event contracts
      associated with operations.
"""

from typing import TYPE_CHECKING, TypedDict
from enum import Enum
from opsorchestrator.support.structures.serialization import Serializable

if TYPE_CHECKING:
    from opsorchestrator.core.execution_unit import ExecutionUnit


class StatusCodes(Enum):
    """
    Enumeration of possible status codes for an operation event.

    Attributes:
        SUCCESS (str): The operation was completed successfully.
        PARTIAL_SUCESS (str): The operation was partially successful.
        FAILURE (str): The operation failed.
        PENDING (str): The operation is still pending.
    """

    START = "START"
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    PENDING = "pending"
    COMPLETED = "completed"
    TERMINATED = "terminated"


class EmittedMessage(TypedDict):
    text: str
    status: StatusCodes


class EventContract(Serializable):
    """
    Abstract base class representing the contract of an operation event.

    Encapsulates the operation, its status, reason for the status, and
    the execution unit (if applicable) responsible for producing the event.

    Attributes:
        _operation (Operation): The operation associated with this event.
        _status (StatusCodes): The current status of the operation.
        _reason (str, optional): Explanation for the status.
        _execution_unit (ExecutionUnit, optional): Execution unit that produced
                                                   the event.
    """

    def __init__(
        self,
        operation_id,
        status: StatusCodes,
        reason: str = None,
        execution_unit: ExecutionUnit = None,
    ):
        """
        Initializes an EventContract instance.

        Args:
            operation (Operation): The operation associated with the event.
            status (StatusCodes): The current status of the operation.
            reason (str, optional): Reason for the current status. Defaults to None.
            execution_unit (ExecutionUnit, optional): Execution unit responsible for
                                                      this event. Defaults to None.
        """
        self._operation_id = operation_id
        self._status = status
        self._reason = reason
        self._execution_unit = execution_unit

    @property
    def data(self):
        """
        Returns a dictionary representation of the event contract.

        Returns:
            dict: A dictionary with keys:
                - "id": operation ID
                - "status": current status (StatusCodes)
                - "reason": reason for the status
                - "execution_unit": name of the execution unit (or None)
        """
        from opsorchestrator.core.operation import Operation

        return {
            "id": (
                self._operation_id
                if not isinstance(self._operation_id, Operation)
                else self._operation_id.id
            ),
            "status": self._status.name,
            "reason": self._reason,
            "execution_unit": (
                self._execution_unit.name if self._execution_unit else None
            ),
        }

    @property
    def encoded_data(self):
        """Use the method of Serializable to encode the data"""
        return self.encode(self.data)

    def __str__(self):
        return str(self.to_dict())

    @property
    def status(self) -> StatusCodes:
        return self._status

    @status.setter
    def status(self, status_code: StatusCodes):
        self._status = status_code

    @property
    def reason(self) -> str:
        return self._reason

    @reason.setter
    def reason(self, _reason: str):
        self._reason = _reason

    @property
    def execution_unit(self) -> ExecutionUnit:
        return self._execution_unit

    @execution_unit.setter
    def execution_unit(self, _execution_unit: ExecutionUnit):
        self._execution_unit = _execution_unit
