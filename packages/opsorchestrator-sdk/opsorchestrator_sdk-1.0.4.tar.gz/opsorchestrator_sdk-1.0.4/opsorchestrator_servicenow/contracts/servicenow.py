"""Contracts for ServiceNow Technology"""

from opsorchestrator.core.model.technology import Technology
from opsorchestrator.core.model.component import Component


class ServiceNow(Technology):
    pass


class Incident(Component):
    pass


class ChangeRequest(Component):
    pass


class Instance(Component):
    pass
