# this is the base class for survey items, including questions, subquestions, and answer options
class SurveyItem:
    
    def __init__(self, id: str, code: str, parent_id: str = None):
        self.id = id
        self.code = code
        self.parent_id = parent_id
        self.label = {}

    def add_label(self, lang: str, text: str):
        self.label[lang] = text

    def get_label(self, lang: str) -> str:
        return self.label.get(lang, self.code)
