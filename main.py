import pandas as pd
from code.markov_chain import MarkovChain
from code.parser import Parser


if __name__ == '__main__':
    
    folder_path = './dataset/'
    column_names = ['previous_utterance']#, 'free_messages', 'guided_messages']

    parser = Parser()
    parsed_data = parser.parse_data(folder_path, column_names)
    
    