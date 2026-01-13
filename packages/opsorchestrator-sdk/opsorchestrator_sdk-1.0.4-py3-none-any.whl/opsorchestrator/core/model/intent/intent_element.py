from opsorchestrator.core.model.component import Component
from opsorchestrator.core.model.element import Element
from opsorchestrator.core.model.technology import Technology


class IntentElement(Element):
    def __init__(
        self, name: str, technology: Technology, component: Component, rank: int = 0
    ):
        super().__init__(name, technology, component)
        self._rank = rank

    @property
    def rank(self):
        return self._rank
