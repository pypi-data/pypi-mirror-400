from typing import Union, Tuple, List, Any
import pandas as pd

from .question import Question

class ResponseSet:

    def __init__(self, question: Question):
        self._question = question
        self._items = None
        self._other_items = None
        self._response_objects = None

    @property
    def items(self) -> pd.DataFrame:
        return self._items
    @items.setter
    def items(self, value: pd.DataFrame):
        self._items = value 

    @property
    def other_items(self) -> pd.DataFrame:
        return self._other_items
    @other_items.setter
    def other_items(self, value: pd.DataFrame):
        self._other_items = value

    @property
    def question(self) -> Question:
        return self._question
    @question.setter
    def question(self, value: Question):
        self._question = value

    @property
    def response_objects(self) -> Any:
        return self._response_objects
    @response_objects.setter
    def response_objects(self, value: Any):
        self._response_objects = value