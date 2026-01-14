import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

from .survey_structure import SurveyStructure
from .survey_item import SurveyItem
from .question import Question
from .item_set import ItemContainer
from .answer import Answer

class LimesurvPyParser:

    @staticmethod
    def get_text(html_text: str) -> str:
        if html_text is None:
            return None
        soup = BeautifulSoup(html_text, 'html.parser')
        return soup.get_text()


    @staticmethod
    def find_matching_elements(root: ET.Element, query_path: str, target_element: str, target_value: str):
        matching_elements = []

        for element in root.findall(query_path): 
            subelement = element.find(target_element)
            if subelement is not None and subelement.text == target_value:
                matching_elements.append(element)
        return matching_elements

    @staticmethod
    def parse(structure_filename: str) -> SurveyStructure:
        """Parse LimeSurvey structure file (lss) from XML format to a SurveyStructure object.

        :param structure_filename: Path to the lss survey structure file.
        :type structure_filename: str
        :return: Parsed SurveyStructure object.
        :rtype: SurveyStructure
        """

        # survey structure object
        survey_structure = SurveyStructure(structure_filename=structure_filename)
        print(f"Parsing {structure_filename}")

        # parse structure XML file and get document root
        xml = ET.parse(structure_filename)
        root = xml.getroot()

        # parse survey titles
        titles = root.findall('.//surveys_languagesettings//rows//row')
        for title in titles:
            lang = title.find('surveyls_language').text
            survey_title = title.find('surveyls_title').text
            survey_structure.add_title(lang, survey_title)

        # parse all questions into target dictionary
        questions = root.findall('.//questions//rows//row')
        
        # iterate over questions and obtain relevant info from subelements
        for question in questions:
            
            qid = question.find('qid').text
            code = question.find('title').text
            type = question.find('type').text
            has_other_field = question.find('other').text
            mandatory = question.find('mandatory').text

            new_question = Question(
                qid = qid,
                code = code,
                type = type,
                has_other_field = has_other_field == 'Y',
                is_mandatory = mandatory
            )

            # find questions attributes
            try:
                attributes = LimesurvPyParser.find_matching_elements(root, ".//question_attributes//rows//row", "qid", qid)
                current_attributes = { q.find('attribute').text : q.find('value').text for q in attributes }
            except Exception as e:
                current_attributes = {}
            new_question.attributes = current_attributes

            # attempt to find labels for current question
            question_labels = LimesurvPyParser.find_matching_elements(root, './/question_l10ns//rows//row', 'qid', qid)
            for label in question_labels:
                lang = label.find('language').text
                label = label.find('question').text
                new_question.add_label(lang, LimesurvPyParser.get_text(label))

            # try to find subquestions, if any, and add to question, if any
            subitems = LimesurvPyParser.find_matching_elements(root, ".//subquestions//rows//row", "parent_qid", qid)
            for subitem in subitems:
                
                subitem_qid = subitem.find('qid').text
                subitem_code = subitem.find('title').text
                
                new_subitem = SurveyItem(
                    id = subitem_qid,
                    code = subitem_code,
                    parent_id=qid
                )
                
                # attempt to find labels for subquestion
                subitem_labels = LimesurvPyParser.find_matching_elements(root, './/question_l10ns//rows//row', 'qid', subitem_qid)
                for label in subitem_labels:
                    lang = label.find('language').text
                    label = label.find('question').text
                    new_subitem.add_label(lang, LimesurvPyParser.get_text(label))

                new_question.add_subquestion_item(new_subitem)

            # try to find answer options, if any
            answer_options = LimesurvPyParser.find_matching_elements(root, ".//answers//rows//row", "qid", qid)
            for answer_option in answer_options:
                
                aid = answer_option.find('aid').text
                code = answer_option.find('code').text
                
                new_answer = Answer(
                    aid = aid,
                    code = code,
                    qid = qid
                )

                # find answer labels
                answer_labels = LimesurvPyParser.find_matching_elements(root, './/answer_l10ns//rows//row', 'aid', aid)
                for answer_label in answer_labels:
                    lang = answer_label.find('language').text
                    label = answer_label.find('answer').text
                    new_answer.add_label(lang, LimesurvPyParser.get_text(label))

                new_question.add_answer_item(new_answer)

            # add question into target list
            survey_structure.add_question(new_question)
       

        return survey_structure