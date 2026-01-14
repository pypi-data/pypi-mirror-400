from enum import Enum
from typing import List

class QuestionProperties:

    class QuestionType(Enum):

        MULTIPLE_CHOICE = 'M', 'Multiple choice'
        LIST = 'L', 'List'
        RANKING = 'R', 'Ranking'
        LONG_FREE_TEXT = 'T', 'Long free text'
        NUMERICAL_INPUT = 'N', 'Numerical input'
        MATRIX = 'F', 'Matrix'
        SHORT_FREE_TEXT = 'S', 'Short free text'

    @staticmethod
    def get_question_type_from_string(type: str):
        for qt in QuestionProperties.QuestionType:
            if qt.value[0] == type:
                return qt
        return None