from .common import QuestionProperties
from .item_set import ItemContainer
from .answer import Answer
from .survey_item import SurveyItem

from typing import List

class Question(SurveyItem):

    def __init__(self, qid: str, code: str, type: str, has_other_field: bool, is_mandatory: str):
        
        # initialize base class
        super().__init__(qid, code, parent_id=None)

        self.question_type = QuestionProperties.get_question_type_from_string(type)
        self.has_other_field = has_other_field
        self.is_mandatory = is_mandatory

        self.subquestion_container = ItemContainer()
        self.answer_container = ItemContainer()
        self.attributes = {}

    def is_numeric(self) -> bool:
        if self.get_attribute_value('numbers_only') is None:
            return None
        return self.get_attribute_value('numbers_only') in ['Y', 'y', '1', 1, True]

    def add_subquestion_item(self, subitem: SurveyItem):
        self.subquestion_container.add_item(subitem)

    def add_answer_item(self, answeritem: Answer):
        self.answer_container.add_item(answeritem)

    def get_answer_items(self) -> List[SurveyItem]:
        items = self.answer_container.get_all()
        return items
    
    def get_subquestion_items(self) -> List[SurveyItem]:
        items = self.subquestion_container.get_all()
        return items
    
    def get_attribute_value(self, attribute_name: str) -> str:
        if self.attributes is None:
            return None        
        return self.attributes.get(attribute_name, None)

    def __repr__(self):

        # print question identity and labels    
        str = f"Question (code='{self.code}', id='{self.id}', type='{self.get_type().value[1]}')\n"                                
        str += "  - labels:" + "\n"        
        for lang, label in self.label.items():
            str += f"    - {lang} : {label}" + "\n"
        
        # print subquestions, if any        
        str += f"  - subquestions ({len(self.subquestion_container.get_all())}):\n"                        
        for item in self.subquestion_container.get_all():
            str += f"    - code: {item.code}, id: {item.id}" + "\n"
            str += f"    - labels:" + "\n"
            for lang, label in item.label.items():
                str += f"      - {lang}: '{label}'" + "\n"

        # print answer options, if any                        
        str += f"  - answers ({len(self.answer_container.get_all())}):\n"    
        for answer in self.answer_container.get_all():
            str += f"    - answer (code: {answer.code}, id: {answer.id})" + "\n"
            str += f"      - labels:" + "\n"
            for lang, label in answer.label.items():
                str += f"        - {lang}: '{label}'" + "\n"

        str += f"  - other: {self.has_other_field}" + "\n"
        str += f"  - mandatory: {self.is_mandatory}" + "\n"

        return str + "\n" 
    
    def print_details(self, include_attributes: bool = False) -> str:
        print(self)
        if include_attributes:
            print("  - attributes:")
            for attr, value in self.attributes.items():
                print(f"    - {attr}: {value}")
            print("\n")

    def get_type(self) -> QuestionProperties.QuestionType:
        return self.question_type
    