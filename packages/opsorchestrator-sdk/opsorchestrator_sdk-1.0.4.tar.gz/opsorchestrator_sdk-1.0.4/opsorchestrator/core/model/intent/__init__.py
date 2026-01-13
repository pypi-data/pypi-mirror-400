from typing import List, Optional
from opsorchestrator.core.model.intent.intent_element import IntentElement


class IntentModel:
    def __init__(
        self,
        intent_elements: List[IntentElement],
        on_success_intent_element: Optional[IntentElement] = None,
        on_failure_intent_element: Optional[IntentElement] = None,
    ) -> None:
        if isinstance(intent_elements, list):
            for intent_element in intent_elements:
                if not isinstance(intent_element, IntentElement):
                    raise TypeError("Intent elements have to be of type IntentElement")
        else:
            raise TypeError("Intent elements have to be a list")

        if on_success_intent_element and not isinstance(
            on_success_intent_element, IntentElement
        ):
            raise TypeError("On success intent element has to be of Type IntentElement")
        if on_failure_intent_element and not isinstance(
            on_failure_intent_element, IntentElement
        ):
            raise TypeError("On success intent element has to be of Type IntentElement")

        self._intent_elements = intent_elements
        self._on_success_intent_element = on_success_intent_element
        self._on_failure_intent_element = on_failure_intent_element

    @property
    def on_success(self):
        return self._on_success_intent_element

    @property
    def on_failure(self):
        return self._on_failure_intent_element

    @property
    def elements(self):
        return self._intent_elements
