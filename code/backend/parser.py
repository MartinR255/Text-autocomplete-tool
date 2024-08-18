import os
import re
import json
import pandas as pd
from nltk.tokenize import sent_tokenize, word_tokenize 


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


    def _tokenize_text(self, dataframe):
        parsed_sentences = []
        for text in dataframe['sentences']:
            sentences = re.split(r'(?<=[.!?]) +', text)
    
            for sentence in sentences:
                tokens = word_tokenize(sentence)
                words = [word.strip().lower() for word in tokens if word.isalpha()]
                parsed_sentences.append(words)
        
        return parsed_sentences


    def _parse_csv_file(self, file_path, column_names):
        df = pd.read_csv(file_path, usecols=column_names)
        combined_dataframe = self._combine_columns(df, column_names)

        return self._tokenize_text(combined_dataframe)
    

    def _save_parsed_data(self, data, filename):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)


    def load_parsed_data(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        return data


    def parse_data(self, folder_path, column_names, save_parsed_data_path=None):
        parsed_data = []
        for file_name in os.listdir(folder_path): 
            if file_name.endswith('.csv'):
                file_path = os.path.join(folder_path, file_name)
                
                parsed_data.extend(self._parse_csv_file(file_path, column_names))

        if save_parsed_data_path:
            self._save_parsed_data(parsed_data, save_parsed_data_path)

        return parsed_data
