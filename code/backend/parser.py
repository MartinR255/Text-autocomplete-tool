import os
import re
import json
import pandas as pd
from nltk.tokenize import word_tokenize 


class Parser:

    def __init__(self):
        self._contractions = {
            "n't": " not",
            "'re": " are",
            "'s": " is",
            "'d": " would",
            "'ll": " will",
            "'ve": " have",
            "'m": " am",
            #"i": "I",
        }


    '''
    Desc: Combines specified columns, applies contractions, and removes non-alphabetic characters
    Params:
        df: pandas.DataFrame - The input dataframe
        column_names: list - Names of columns to combine
    Returns: pandas.DataFrame - Combined dataframe with processed text
    '''
    def _combine_columns(self, df, column_names):
        column_df_to_concat = []
        for name in column_names:
            pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in self._contractions.keys()) + r')\b') 
            df[name] = df[name].apply(lambda text: pattern.sub(lambda x: self._contractions[x.group()], text))
            df[name] = df[name].apply(lambda text: re.sub(r'[^a-zA-Z .?!]', '', text))
            column_df_to_concat.append(df[name])
        
        combined_columns = pd.concat(column_df_to_concat, axis=0).reset_index(drop=True)
        combined_dataframe = pd.DataFrame({'sentences': combined_columns})

        return combined_dataframe


    '''
    Desc: Tokenizes the text in the dataframe into words
    Params:
        dataframe: pandas.DataFrame - The input dataframe
    Returns: list - List of tokenized sentences
    '''
    def _tokenize_text(self, dataframe):
        parsed_sentences = []
        for text in dataframe['sentences']:
            sentences = re.split(r'(?<=[.!?]) +', text)
    
            for sentence in sentences:
                tokens = word_tokenize(sentence)
                words = [word.strip().lower() for word in tokens if word.isalpha()]
                parsed_sentences.append(words)
        
        return parsed_sentences


    '''
    Desc: Parses a CSV file, combines specified columns, and tokenizes the text
    Params:
        file_path: str - Path to the CSV file
        column_names: list - Names of columns to parse
    Returns: list - List of tokenized sentences from the CSV file
    '''
    def _parse_csv_file(self, file_path, column_names):
        df = pd.read_csv(file_path, usecols=column_names)
        combined_dataframe = self._combine_columns(df, column_names)

        return self._tokenize_text(combined_dataframe)
    

    '''
    Desc: Saves parsed data to a JSON file
    Params:
        data: list - The parsed data to save
        file_path: str - File path to file to save the data
    Returns: None
    '''
    def _save_parsed_data(self, data, file_path):
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)


    '''
    Desc: Loads parsed data from a JSON file
    Params:
        file_path: str - File path to load the data from
    Returns: list - The loaded parsed data
    '''
    def load_parsed_data(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data


    '''
    Desc: Parses all CSV files in a folder and optionally saves the parsed data
    Params:
        folder_path: str - Path to the folder containing CSV files
        column_names: list - Names of columns to parse
        save_parsed_data_path: str - Path to save the parsed data (optional)
    Returns: list - The parsed data from all CSV files
    '''
    def parse_data(self, folder_path, column_names, save_parsed_data_path=None):
        parsed_data = []
        for file_name in os.listdir(folder_path): 
            if file_name.endswith('.csv'):
                file_path = os.path.join(folder_path, file_name)
                
                parsed_data.extend(self._parse_csv_file(file_path, column_names))

        if save_parsed_data_path:
            self._save_parsed_data(parsed_data, save_parsed_data_path)

        return parsed_data
