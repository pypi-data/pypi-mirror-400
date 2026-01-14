from .survey_item import SurveyItem

class ItemContainer:

    def __init__(self):
        self.items = []

    def __repr__(self):
        str = "ItemSet:\n"
        for item in self.items:            
           str += f"SurveyItem (code: {item.code}, id: {item.id}, parent_id: {item.parent_id})\n"
        return str

    def get_all(self) -> list[SurveyItem]:
        return self.items

    def add_item(self, item: SurveyItem):
        self.items.append(item)

    def get_item_by_code(self, code: str) -> SurveyItem:
        for q in self.items:
            if q.code == code:
                return q
        return None
    
    def get_item_by_id(self, qid: str) -> SurveyItem:
        for q in self.items:
            if q.qid == qid:
                return q
        return None
    
