"""Preconditions for a certain data-model to be fullfilled"""

from typing import List
from opsorchestrator.support.structures.serialization import Serializable
from opsorchestrator.core.model.data.data_element import DataElement
from opsorchestrator.logger.local import get_console_logger

logger = get_console_logger("Precondition")


class Precondition(Serializable):
    """Precondition to check whether the data model provider is actually the right one for the use case"""

    def __init__(self, method, parameter_list):
        if not isinstance(parameter_list, list):
            for data_element in parameter_list:
                if not isinstance(data_element, DataElement):
                    raise TypeError("Preconditions has to contain data elements")
        for elem in parameter_list:
            if not isinstance(elem, DataElement):
                raise TypeError("parameter list has to be list of data elements")
        self._parameter_list: List[DataElement] = parameter_list
        self._method = method
