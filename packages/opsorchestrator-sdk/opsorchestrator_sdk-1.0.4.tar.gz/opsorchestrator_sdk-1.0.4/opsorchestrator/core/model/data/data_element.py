"""Data model element"""

from typing import Optional
from opsorchestrator.core.model.element import Element
from opsorchestrator.core.data_source import DataSourceScope
from opsorchestrator.core.model.component import Component
from opsorchestrator.core.model.technology import Technology


class DataElement(Element):
    """Data element interface to define a key within a component"""

    def __init__(
        self,
        name: str,
        technology: Technology,
        component: Component,
        element_type: type,
        is_auth: bool = False,
        is_optional: bool = False,
        scope: DataSourceScope = DataSourceScope.OPERATION,
        expiration_period=None,
        skip_execution_if_not_found=False,
        alias_data_element: Optional[DataElement] = None,
    ):  # Justification: Already imported via TYPE_CHECKING, pylint: disable=used-before-assignment
        super().__init__(name, technology, component)
        self._element_type = element_type
        self._is_auth = is_auth
        self._scope = scope
        self._is_optional = is_optional
        self._expiration_period = (
            expiration_period
            if expiration_period or scope != DataSourceScope.OPERATION
            else 3600
        )
        self._skip_execution_if_not_found = skip_execution_if_not_found
        self._alias_data_element = alias_data_element

    @property
    def element_type(self):
        return self._element_type

    @property
    def is_authentication_element(self):
        return self._is_auth

    @property
    def is_optional(self):
        return self._is_optional

    @property
    def scope(self) -> DataSourceScope:
        return self._scope

    @scope.setter
    def scope(self, scope):
        self._scope = scope

    @property
    def expiration_period(self):
        return self._expiration_period

    @property
    def skip_execution(self):
        """Skip execution of that execution unit if data is absent."""
        return self._skip_execution_if_not_found

    @property
    def alias_data_element(self):
        return self._alias_data_element
