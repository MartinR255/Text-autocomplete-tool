from code.backend import MarkovChain
from code.backend import Parser
from code.frontend import Window


if __name__ == '__main__':
    
    folder_path = './dataset/'
    parsed_data_folder_path = './parsed_data.json'
    column_names = ['previous_utterance', 'free_messages', 'guided_messages']

    parser = Parser()

    '''
    parse and save data into json file
    '''
    # parsed_data = parser.parse_data(folder_path, column_names, parsed_data_folder_path)

    '''
    load parsed data from json file
    '''
    parsed_data = parser.load_parsed_data(parsed_data_folder_path)
    
    markov_chain = MarkovChain(parsed_data)


    w = Window(700, 450)
    w.set_markov_chain(markov_chain)
    w.run()

    