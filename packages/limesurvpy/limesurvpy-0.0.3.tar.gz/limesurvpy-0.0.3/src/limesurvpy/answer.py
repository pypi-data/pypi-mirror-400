from .survey_item import SurveyItem

class Answer(SurveyItem):

    def __init__(self, aid: str, code: str, qid: str):
        super().__init__(aid, code, parent_id=qid)



