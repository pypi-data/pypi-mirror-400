import pandas as pd
from typing import Tuple, List
from typing import Tuple, List
import numpy as np
import deep_translator as dptr

from .question import Question
from .survey_item import SurveyItem
from .response_set import ResponseSet

from .common import QuestionProperties

class DataProcessing:

    translator = dptr.GoogleTranslator(source='auto', target='en')
    """Translator support for fields"""
    
    @staticmethod
    def get_response_columns(question: Question, responses: pd.DataFrame, lang: str = "en", drop_missing_values: bool = False) -> List[str]:
        
        items: pd.DataFrame 
        items = None

        if question.get_type() is QuestionProperties.QuestionType.RANKING:
            pass
        
        elif question.get_type() is QuestionProperties.QuestionType.MULTIPLE_CHOICE:
            pass
        
        elif question.get_type() is QuestionProperties.QuestionType.MATRIX:
            pass

        elif question.get_type() is QuestionProperties.QuestionType.LIST:
                
            # determine value counts
            items = responses[question.code].copy()

        elif question.get_type() is QuestionProperties.QuestionType.LONG_FREE_TEXT or question.get_type() is QuestionProperties.QuestionType.SHORT_FREE_TEXT:
            
            items = responses[[question.code]].copy()  
            items.rename(columns={
                question.code : 'value'
            }, inplace=True)

            # drop nan values, if requested
            if drop_missing_values:
                items = items.dropna(subset=['value'])

            # check whether we should treat texts as numbers
            if question.is_numeric():
                items['value'] = pd.to_numeric(items['value'], errors='coerce')
            else:
                # add autotranslation for texts
                items = DataProcessing.get_translations(items, source_col='value', dest_col='value_translated', lang=lang)
            
        return items


    @staticmethod
    def get_translations(df: pd.DataFrame, source_col: str, dest_col: str, lang: str = 'en') -> pd.DataFrame:
        """Get translations

        :param df: DataFrame containing the data to translate.
        :type df: pd.DataFrame
        :param source_col: Column of the dataframe to translate.
        :type source_col: str
        :param dest_col: Column to store the translated values.
        :type dest_col: str
        :param lang: Target language for translation, defaults to 'en'
        :type lang: str, optional
        :return: DataFrame with translated values in the specified destination column.
        :rtype: pd.DataFrame
        """

        # use GTranslate for now
        DataProcessing.translator.target = lang
        translated_df = df.copy()
        translated_df[dest_col] = translated_df[source_col].apply(lambda x: DataProcessing.translator.translate(x) if pd.notna(x) else x)
        return translated_df

    @staticmethod
    def get_responses_for_text_question(question: Question, responses: pd.DataFrame, lang: str = "en", drop_missing_values: bool = True) -> ResponseSet:
        """Get responses for a text question.

        :param question: The question to get responses for.
        :type question: Question
        :param responses: The DataFrame containing all responses.
        :type responses: pd.DataFrame
        :param lang: The language to use for labels, defaults to "en"
        :type lang: str, optional
        :param drop_missing_values: Whether to drop missing values, defaults to True
        :type drop_missing_values: bool, optional
        :return: A DataFrame containing the responses for the text question.
        :rtype: pd.DataFrame
        """

        result = ResponseSet(question)
        items = DataProcessing.get_response_columns(question=question, responses=responses, lang=lang, drop_missing_values=drop_missing_values)        
        result.items = items
        
        return result

    @staticmethod
    def get_other_values(question: Question, responses: pd.DataFrame, lang: str = 'en') -> pd.DataFrame:
        """Get 'other' values for a question.

        :param question: The question to get 'other' values for.
        :type question: Question
        :param responses: The DataFrame containing all responses.
        :type responses: pd.DataFrame
        :param lang: The language to use for labels, defaults to 'en'
        :type lang: str, optional
        :return: A DataFrame containing the 'other' values.
        :rtype: pd.DataFrame
        """
        if not question.has_other_field:
            print(f"No 'other' field for {question.code}")
            return None
        else:
            print(f"Retrieve other values for {question.code}...")
            other_values = responses[[f'{question.code}[other]']].dropna()
            other_values = other_values.rename(columns={f'{question.code}[other]': 'other_value'})
            other_values = DataProcessing.get_translations(other_values, source_col='other_value', dest_col='other_value_translated', lang=lang)
            print(f"Found {len(other_values)} 'other' values for question {question.code}")
            return other_values   

    @staticmethod
    def get_responses_for_list_question(question: Question, responses: pd.DataFrame, lang: str = 'en', drop_missing_values: bool = True) -> ResponseSet:
        """Get responses for a list question.

        :param question: The question to get responses for.
        :type question: Question
        :param responses: The DataFrame containing all responses.
        :type responses: pd.DataFrame
        :param lang: The language to use for labels, defaults to 'en'
        :type lang: str, optional
        :param drop_missing_values: Whether to drop missing values, defaults to True
        :type drop_missing_values: bool, optional
        :return: A DataFrame containing the responses for the list question.
        :rtype: pd.DataFrame
        """

        result = ResponseSet(question)
        items = DataProcessing.get_response_columns(question=question, responses=responses, lang=lang, drop_missing_values=drop_missing_values)        
        
        items = items.value_counts(dropna=drop_missing_values).reset_index().rename(columns={question.code: 'category'})

        # translation support
        DataProcessing.translator.target = lang

        # replace labels into new column
        answers = dict([(item.code, item.get_label(lang)) for item in question.get_answer_items()])
        answers[np.nan] = 'Missing values' if lang == 'en' else DataProcessing.translator.translate('Missing values')   
        answers['-oth-'] = 'Other value' if lang == 'en' else DataProcessing.translator.translate('Other value')
        items.insert(1, 'category_labeled', items['category'].map(answers).fillna(items['category']))

        result.items = items        
        result.other_items = DataProcessing.get_other_values(question=question, responses=responses, lang=lang) # treatment of other field - get 'other' responses
        
        return result


    @staticmethod
    def get_responses_for_matrix_question(question: Question, responses: pd.DataFrame, lang: str = 'en', drop_missing_values: bool = True, drop_response_categories: List[str] = None) -> ResponseSet:
        """Get responses for a matrix question.

        :param question: The question to get responses for.
        :type question: Question
        :param responses: The DataFrame containing all responses.
        :type responses: pd.DataFrame
        :param lang: The language to use for labels, defaults to 'en'
        :type lang: str, optional
        :param drop_missing_values: Whether to drop missing values, defaults to True
        :type drop_missing_values: bool, optional
        :param drop_response_categories: List of response categories to drop from results, defaults to None
        :type drop_response_categories: List[str], optional
        :return: A tuple containing the long format DataFrame and the aggregated DataFrame.
        :rtype: Tuple[ pd.DataFrame, dict]
        """

        result = ResponseSet(question)

        # translation support
        DataProcessing.translator.target = lang
        
        # matrix questions are coded one column per subquestion, with title in the form Question_code[Subquestion_code]
        # Values are the selected answer option codes
        # answers appear in the order of the XML spec file
        response_categories = dict([(item.code, item.get_label(lang)) for item in question.get_answer_items()])
        subquestions = dict([(item.code, item.get_label(lang)) for item in question.get_subquestion_items()])

        # store results 
        items = None

        # iterate over the columns, get the unique values in these columns, and the counts of unique values
        for subquestion_code in subquestions.keys():
            
            # generate the column name required to access relevant data in the pandas DataFrame
            column_name = f"{question.code}[{subquestion_code}]"
            try:
                # get value counts where category is the chosen answer, and count is the number of responses per observed answer 
                vals = responses[column_name].value_counts(dropna=drop_missing_values).reset_index().rename(columns={column_name: 'response'})
                vals.insert(0, 'category', subquestion_code)
                vals['response_count'] = vals['count'].sum()
                items = vals if items is None else pd.concat([items, vals], axis=0)                                
            
            except KeyError:
                print(f"Error fetching {column_name} for question {question.code}")

        # make a default item order
        items = items.sort_values(by=['category', 'response'], na_position='last')        

        if drop_response_categories is not None:
            items = items[~items['response'].isin(drop_response_categories)]

        # add categories for renaming
        # create new columns to replace codes with labels, but retain original codes as well 
        subquestions[np.nan] = 'Missing values' if lang == 'en' else DataProcessing.translator.translate('Missing values')
        if not drop_missing_values:
            response_categories[np.nan] = 'Missing values' if lang == 'en' else DataProcessing.translator.translate('Missing values')

        # remove categories to exclude from response_categories dict (remove the keys)
        if drop_response_categories is not None:
            for rc in drop_response_categories:
                if rc in response_categories:
                    del response_categories[rc]

        items.insert(1, 'category_labeled', items['category'].map(subquestions).fillna(items['category']))        
        items.insert(3, 'response_labeled', items['response'].map(response_categories).fillna(items['response']))

        result.items = items
        result.response_objects = response_categories

        return result

    @staticmethod
    def get_responses_for_ranking_question(question: Question, responses: pd.DataFrame, lang: str = 'en', max_ranked_items: int = None, min_item_count: int = None) -> ResponseSet:
        """Get responses for a ranking question.

        :param question: The ranking question to get responses for.
        :type question: Question
        :param responses: The DataFrame containing survey responses.
        :type responses: pd.DataFrame
        :param lang: The language to use for labels, defaults to 'en'
        :type lang: str, optional
        :return: A tuple containing the aggregated DataFrame and the long format DataFrame with raw ranks.
        :rtype: Tuple[pd.DataFrame, pd.DataFrame]
        """

        result = ResponseSet(question)

        # translation support
        DataProcessing.translator.target = lang

        # get relevant columns for the ranking question
        answer_options = dict([(item.code, item.get_label(lang)) for item in question.get_answer_items()])

        # iterate over the columns, get the unique values in these columns, and the counts of unique values
        # total_items_to_rank = len(answer_options.keys())
        total_items_to_rank = int(question.get_attribute_value('max_subquestions')) if question.get_attribute_value('max_subquestions') is not None else len(answer_options.keys())
        if max_ranked_items is not None:
            total_items_to_rank = min(total_items_to_rank, max_ranked_items)
        
        # iterate over potential ranks, consider offset by +1. Store results temporarily as list
        raw_ranks = []
        response_columns = []
        for rank in range(1, total_items_to_rank+1):

            has_column = True
            try:
                # get column of rank and get the item in the column
                column_name = f"{question.code}[{rank}]"
                vals = responses[column_name].value_counts().reset_index().rename(columns={column_name: 'category'})
                vals['rank'] = rank

                # Create long format: for each category-rank combination, create 'count' number of rows
                for _, row in vals.iterrows():
                    for _ in range(row['count']):
                        raw_ranks.append({
                            'category': row['category'],
                            'rank': row['rank']
                        })
            except:
                has_column = False # we do not have this column

            if has_column:
                response_columns.append(column_name)    

        # determine number of ranked items per respondent
        number_of_ranked_items = responses[response_columns].copy()
        number_of_ranked_items['count'] = number_of_ranked_items.notna().sum(axis=1) 
        number_of_ranked_items = number_of_ranked_items[['count']]
                
        # Convert long_df list to DataFrame
        raw_ranks = pd.DataFrame(raw_ranks)
        
        # extract relevant columns for individual responses
        rank_cols = responses[response_columns].copy()
        # rank_cols.dropna(how='all', inplace=True)
        rank_cols['rank_count'] = rank_cols.count(axis=1)

        def find_column_with_value(row, value):
            matches = row[row == value].index.tolist()
            col_name = matches[0] if matches else None
            if col_name is not None:
                return rank_cols.columns.get_loc(col_name) + 1  # Return rank (1-based index)
            else:
                return None

        for ao in answer_options.keys():
            rank_cols[ao] = rank_cols.apply(find_column_with_value, axis=1, value=ao)

        rank_cols = rank_cols[[key for key in answer_options.keys()] + ['rank_count']]

        # replace values with actual labels in requested language
        answer_options[np.nan] = 'Missing values' if lang == 'en' else DataProcessing.translator.translate('Missing values')
        if question.has_other_field:
            answer_options['other'] = 'Other value' if lang == 'en' else DataProcessing.translator.translate('Other value')
        raw_ranks.insert(1, 'category_labeled', raw_ranks['category'].map(answer_options).fillna(raw_ranks['category']))

        # define custom percentile functions
        def percentile(n):
            def percentile_(x):
                return x.quantile(n)
            percentile_.__name__ = 'percentile_{:02.0f}'.format(n*100)
            return percentile_

        items = raw_ranks.groupby('category').agg({
            'rank': ['mean', 'median', 'count', 'min', 'max', percentile(0.1), percentile(0.25), percentile(0.75), percentile(0.9)]
        })
        items.columns = ['_'.join(gp) for gp in items.columns.values]
        items.reset_index(inplace=True)
        items.rename(columns={
            'rank_count' : 'count'
        }, inplace=True)

        # filter by min item count, if requested
        if min_item_count is not None:
            items = items[items['count'] >= min_item_count]

        items['relative_count'] = items['count'] / items['count'].sum()

        # sort alphabetically by category
        items.sort_values(by="category", inplace=True)
        items.insert(1, 'category_labeled', items['category'].map(answer_options).fillna(items['category']))

        result.items = items
        result.response_objects = [raw_ranks, rank_cols, number_of_ranked_items]

        return result
    
    @staticmethod
    def get_responses_for_multiple_choice_question(question: Question, responses: pd.DataFrame, lang: str = 'en') -> ResponseSet:
        """Get responses for a multiple choice question.

        :param question: The question to get responses for.
        :type question: Question
        :param responses: The DataFrame containing all responses.
        :type responses: pd.DataFrame
        :param lang: The language to use for labels, defaults to 'en'
        :type lang: str, optional
        :return: A DataFrame containing the responses for the specified question.
        :rtype: pd.DataFrame
        """

        result = ResponseSet(question)

        # translation support
        DataProcessing.translator.target = lang

        # MC questions are coded one column per answer option, with title in the form Question_code[answer_option code]
        # Values should be Y/NaN in each column
        answers = dict([(item.code, item.get_label(lang)) for item in question.get_subquestion_items()])   
        if question.has_other_field: 
            answers['other'] = 'Other value' if lang == 'en' else DataProcessing.translator.translate('Other value')
        
        # return dict
        counts = {}

        for answer_code in answers.keys():
            try:
                column_name = f"{question.code}[{answer_code}]"
                counts[answer_code] = responses[column_name].value_counts().get('Y', 0)

            except KeyError:
                print(f"Error fetching {column_name} for question {question.code}")
            
        items = pd.DataFrame.from_dict(counts, orient='index', columns=['count']).reset_index()
        items.rename(columns={'index': 'category'}, inplace=True)        
        items.insert(1, 'category_labeled', items['category'].map(answers).fillna(items['category']))
        
        result.items = items
        result.other_items = DataProcessing.get_other_values(question=question, responses=responses, lang=lang) # treatment of other field - get 'other' responses
        
        return result