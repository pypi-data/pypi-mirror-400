from .item_set import ItemContainer
from .question import Question

from typing import List

class SurveyStructure:

    def __init__(self, structure_filename: str):
        self.structure_filename = structure_filename
        self.question_set = ItemContainer()
        self.survey_title = {}


    def add_question(self, question: Question):
        self.question_set.add_item(question)

    def add_title(self, lang: str, title: str):
        self.survey_title[lang] = title

    def get_title(self, lang: str) -> str:
        if lang in self.survey_title:
            return self.survey_title[lang]
        return None
    
    def get_titles(self) -> dict:
        return self.survey_title

    def get_question_by_id(self, qid: str) -> Question:
        q: Question
        for q in self.question_set.get_all():
            if q.id == qid:
                return q
        return None
    
    def get_question_by_code(self, code: str) -> Question:
        q : Question
        for q in self.question_set.get_all():
            if q.code == code:
                return q
        return None

    def get_questions(self) -> List[Question]:
        return self.question_set.get_all()
    

