import pandas as pd
import os
from typing import Union, Tuple, List, Literal

from .common import QuestionProperties
from .parser import LimesurvPyParser
from .response_set import ResponseSet
from .survey_structure import SurveyStructure
from .data_processing import DataProcessing
from .charting import Charting, ChartType
from .question import Question

class Survey:

    def __init__(self, structure: SurveyStructure):
        # set some default values and intialize class members as needed
        self.structure = structure
        self.survey_responses = None
        
    def __repr__(self):
        str = f"Survey (structure file: '{os.path.basename(self.structure.structure_filename)}')\n"
        str += "  - titles:\n"
        for lang, title in self.structure.get_titles().items():
            str += f"    - {lang}: '{title}'\n"
        str += f"  - questions ({len(self.structure.question_set.get_all())}):\n"
        return str

    def summary(self):
        print(self)

    def get_questions(self) -> List[Question]:
        return self.structure.get_questions()

    @staticmethod
    def from_lss(structure_filename: str) -> 'Survey':
        """Import survey structure from an Limesurvey lss file that is in XML format.

        :param structure_filename: Path to the lss survey structure file.
        :type structure_filename: str
        """
        structure = LimesurvPyParser.parse(structure_filename=structure_filename)
        survey = Survey(structure=structure)
        return survey

    def list_questions(self, list_labels: bool = True):
        """List all questions in the survey."""
        print("- Questions:")
        for q in self.structure.get_questions():
            print(f"  - code: {q.code}, id: {q.id}, type: {q.get_type().value[1]}")
            if list_labels:
                for lang, label in q.label.items():
                    print(f"    - {lang} : {label}")

    def print_details(self, question_code: str = None, qid: str = None, include_attributes: bool = False):
        """Print details on a question, including subquestions and answer options. Provide either question code or question ID, code takes precedence.
        Attributes of questions will be printed at request, if available.
        
        :param question_code: Code of the question to print details for. Defaults to None.
        :type question_code: str, optional
        :param question_id: ID of the question to print details for. Defaults to None.
        :type question_id: str, optional
        """
        if question_code is None and qid is None:
            print("Please provide either question code or question ID.")
            return
        
        if question_code is None:
            question = self.structure.get_question_by_id(qid)
        else:
            question = self.structure.get_question_by_code(question_code)

        if question is None:
            print(f"Question with code '{question_code}' not found.")
            return
        
        question.print_details(include_attributes=include_attributes)

    def import_responses(self, responses_filename: str, sep: str = ','):
        """Import survey responses from a CSV file. The file should have both variables (column names) and responses (row values) coded.

        :param responses_filename: Path to the CSV file with survey responses.
        :type responses_filename: str
        :param sep: Separator used in the responses file, defaults to ','
        :type sep: str, optional
        """
        self.responses_filename = responses_filename
        print(f"Importing responses from {os.path.basename(self.responses_filename)}")
        self.raw_responses = pd.read_csv(self.responses_filename, sep=sep)
        self.survey_responses = None

    def get_responses(self) -> pd.DataFrame:
        return self.survey_responses if self.survey_responses is not None else self.raw_responses   

    @property 
    def responses(self) -> pd.DataFrame:
        return self.get_responses()
    @responses.setter
    def responses(self, df: pd.DataFrame):
        self.survey_responses = df

    def export_questions(self, questions: List[Question] = None, lang: str = "en", drop_missing_values: bool = False, target: Literal['csv', 'xlsx'] = 'xlsx', path: str = None, sep: str = ',', index: bool = False):

        # include all questions of survey, if none are provided
        if questions is None:
            questions = self.get_questions()

        # gather response sets
        response_sets = []
        for question in questions:
            rs = self.describe(question_code=question.code, lang=lang, drop_missing_values=drop_missing_values, plot=False)
            response_sets.append(rs)

        # export gathered response sets
        Survey.export(
            responses=response_sets,
            target=target,
            path=path,
            sep=sep,
            index=index
        )



    @staticmethod
    def export(responses: Union[ResponseSet, List[ResponseSet]], target: Literal['csv', 'xlsx'] = 'xlsx', path: str = None, sep: str = ',', index: bool = False):
        """Export responses of one or more questions to disk.

        :param responses: ResponseSet or list of ResponseSets to export.
        :type responses: Union[ResponseSet, List[ResponseSet]]
        :param target: File format to export to, defaults to 'xlsx'
        :type target: Literal['csv', 'xlsx'], optional
        :param path: Path of excel file to write, or to folder to write csv files into, defaults to None
        :type path: str, optional
        :param sep: Separator to use in the CSV file(s), defaults to ','
        :type sep: str, optional
        :param index: Whether to include the dataframe index in the exports, defaults to False
        :type index: bool, optional
        """

        if target == 'xlsx':
            
            if path is None:
                raise ValueError("Please provide path for Excel filename to export to.")
           
            with pd.ExcelWriter(path) as writer:
                if isinstance(responses, ResponseSet):
                    # export as single excel file
                    responses : ResponseSet
                    sheet_name = f'Sheet_{responses.question.code}'
                    df = responses.items
                    df.to_excel(writer, sheet_name=sheet_name, index=index)

                    if responses.other_items is not None:
                        other_sheet_name = f'Sheet_{responses.question.code}_other'
                        responses.other_items.to_excel(writer, sheet_name=other_sheet_name, index=True)

                else:
                    rs: ResponseSet
                    for i, rs in enumerate(responses):
                        df = rs.items            
                        sheet_name = f'Sheet_{rs.question.code}'
                        # add as sheet to existing excel file
                        df.to_excel(writer, sheet_name=sheet_name, index=index)

                        if rs.other_items is not None:
                            other_sheet_name = f'Sheet_{rs.question.code}_other'
                            rs.other_items.to_excel(writer, sheet_name=other_sheet_name, index=True)
                
                print(f"Exported responses to '{path}'")

        
        elif target == 'csv':
            
            if path is None:
                path = os.path.abspath(__file__)
                print(f"Exporting to directory: {path}")
            
            if isinstance(responses, ResponseSet):
                responses : ResponseSet
                df = responses.items
                filename = f'{responses.question.code}.csv'
                df.to_csv(os.path.join(path, filename), sep=sep, index=index)

                if responses.other_items is not None:
                    other_filename = f'{responses.question.code}_other.csv'
                    responses.other_items.to_csv(os.path.join(path, other_filename), sep=sep, index=True)
            
            else:
                rs: ResponseSet
                for i, rs in enumerate(responses):
                    df = rs.items
                    filename = f'{rs.question.code}.csv'
                    df.to_csv(os.path.join(path, filename), sep=sep, index=index)

                    if rs.other_items is not None:
                        other_filename = f'{rs.question.code}_other.csv'
                        rs.other_items.to_csv(os.path.join(path, other_filename), sep=sep, index=True)

            print(f"Exported responses to '{path}'")

        else:
            raise ValueError(f"Unsupported export target: {target}")



    def describe(self, question_code: str, responses: pd.DataFrame = None, lang='en', drop_response_codes: List[str] = None, drop_missing_values: bool = False, title = None, plot_labels: bool = True, include_question_code_in_title: bool = False, plot: bool = True, **kwargs) -> ResponseSet:
        """Extract responses for a given question, and plot responses if desired.

        :param question_code: The code of the question to describe.
        :type question_code: str
        :param responses: The DataFrame with survey responses. If None, uses the survey's responses, defaults to None.
        :type responses: pd.DataFrame, optional
        :param lang: The language to use for labels, defaults to 'en'
        :type lang: str, optional
        :param drop_missing_values: Whether to drop missing values, defaults to False
        :type drop_missing_values: bool, optional
        :param title: The title to use for the description, defaults to None
        :type title: str, optional
        :param plot_labels: Whether to plot labels or question codes, defaults to True
        :type plot_labels: bool, optional
        :param include_question_code_in_title: Whether to include the question code in the title, defaults to False
        :type include_question_code_in_title: bool, optional
        :param plot: Whether to plot the results, defaults to True
        :type plot: bool, optional
        :raises ValueError: If the question code is not found
        :raises ValueError: If the question type is not supported
        :raises ValueError: If the chart type is not supported
        :return: A ResponseSet containing the responses and associated question.
        :rtype: ResponseSet
        """

        if responses is None:
            responses = self.responses

        current_question = self.structure.get_question_by_code(question_code)   


        title = current_question.get_label(lang) if title is None else title
        if include_question_code_in_title:
            title = f"{title} ({current_question.code})"

        # select method to obtain result from type of question
        result = None
        
        if current_question.get_type() is QuestionProperties.QuestionType.RANKING:
            # consider only ranks up to a specific rank?            
            max_rank = kwargs.get('max_rank', None)
            min_count = kwargs.get('min_count', None)

            result = DataProcessing.get_responses_for_ranking_question(current_question, self.responses, lang=lang, max_ranked_items=max_rank, min_item_count=min_count)                                    

            # auto-generate sensible plots
            if plot:
                charttype_summary = kwargs.get('charttype_summary', ChartType.BAR)
                if not charttype_summary in [ChartType.BAR, ChartType.PIE]:
                    raise ValueError(f"Chart type {charttype_summary} not supported for LIST questions.")
                Charting.plot_chart(charttype_summary, current_question, result.items, title=title, lang=lang, plot_labels=plot_labels, **kwargs)
                Charting.plot_chart(ChartType.BOXPLOT, current_question, result.response_objects[2], title=title, lang=lang, plot_labels=plot_labels, **kwargs)
                Charting.plot_chart(ChartType.RANKS, current_question, result.items, title=title, lang=lang, plot_labels=plot_labels, **kwargs)
                        

        elif current_question.get_type() is QuestionProperties.QuestionType.MULTIPLE_CHOICE:
            result = DataProcessing.get_responses_for_multiple_choice_question(current_question, responses, lang=lang)
            # auto-generate sensible plots  
            if plot:
                charttype = kwargs.get('charttype', ChartType.BAR)
                if not charttype in [ChartType.BAR, ChartType.PIE]:
                    raise ValueError(f"Chart type {charttype} not supported for LIST questions.")          
                Charting.plot_chart(charttype, current_question, result.items, title=title, lang=lang, plot_labels=plot_labels, **kwargs)
            

        elif current_question.get_type() is QuestionProperties.QuestionType.MATRIX:
            result = DataProcessing.get_responses_for_matrix_question(current_question, responses, lang=lang, drop_missing_values=drop_missing_values, drop_response_categories=drop_response_codes)   
              
            # auto-generate sensible plots   
            if plot:         
                Charting.plot_chart(ChartType.STACKED_MATRIX, current_question, result.items, title=title, lang=lang, plot_labels=plot_labels, response_categories=result.response_objects, **kwargs)
            

        elif current_question.get_type() is QuestionProperties.QuestionType.LIST:
            result = DataProcessing.get_responses_for_list_question(current_question, responses, lang=lang, drop_missing_values=drop_missing_values)
            
            # auto-generate sensible plots 
            if plot:
                charttype = kwargs.get('charttype', ChartType.BAR)
                if not charttype in [ChartType.BAR, ChartType.PIE]:
                    raise ValueError(f"Chart type {charttype} not supported for LIST questions.")
                Charting.plot_chart(charttype, current_question, result.items, title=title, lang=lang, plot_labels=plot_labels, **kwargs)
            

        elif current_question.get_type() is QuestionProperties.QuestionType.LONG_FREE_TEXT or current_question.get_type() is QuestionProperties.QuestionType.SHORT_FREE_TEXT:
            result = DataProcessing.get_responses_for_text_question(current_question, responses, lang=lang, drop_missing_values=drop_missing_values)
            # auto-generate sensible plots     
            if plot:       
                if current_question.is_numeric():
                    Charting.plot_chart(ChartType.HISTOGRAM, current_question, result.items, title=title, lang=lang, **kwargs)
            

        # return resultset    
        return result




















    def filter_incomplete(self, status_column: str = 'submitdate'):
        # filter responses that were started but not submitted.
        self.survey_responses = self.raw_responses[self.raw_responses[status_column].notna()]
    
    


