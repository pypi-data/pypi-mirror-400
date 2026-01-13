"""Data model that defines the data fully qualified name"""

from typing import List, Dict
from opsorchestrator.core.model.data.data_element import DataElement
from opsorchestrator.core.model.data.precondition import Precondition


class DataModel:
    """Data model for output and preconditions"""

    def __init__(self, required_data, output_data, preconditions=None, static_data={}):
        if isinstance(required_data, list):
            for data_element in required_data:
                if not isinstance(data_element, DataElement):
                    raise TypeError("Required data has to contain data elements")
        else:
            raise TypeError("Required data has to be a list")

        if isinstance(output_data, list):
            for data_element in output_data:
                if not isinstance(data_element, DataElement):
                    raise TypeError("Output data has to contain data elements")
        else:
            raise TypeError("Output data has to be a list")

        if isinstance(static_data, dict):
            for data_element in static_data.keys():
                if not isinstance(data_element, DataElement):
                    raise TypeError("Static data has to contain data elements as keys")
        else:
            raise TypeError("Static data has to be a dictionary")

        self._required_data_list = required_data
        self._output_data_list = output_data
        self._preconditions: List[Precondition] = preconditions if preconditions else []
        self._static_data: Dict[DataElement, str] = static_data if static_data else {}

    @property
    def required_data(self) -> List[DataElement]:
        return self._required_data_list

    @property
    def output_data(self) -> List[DataElement]:
        return self._output_data_list

    @property
    def preconditions(self) -> List[Precondition]:
        return self._preconditions

    @property
    def static_data(self) -> Dict[DataElement, str]:
        return self._static_data
