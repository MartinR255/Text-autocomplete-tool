from PyQt6.QtWidgets import QApplication

from code.backend import MarkovChain
from code.backend import Parser
from code.frontend import Window
import sys


def main():
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
    
    # create markov chains in reverse order to get the most complex model first
    max_nth_order = 3
    markov_chains = [MarkovChain(parsed_data, i) for i in range(max_nth_order, 0, -1)]


    app = QApplication(sys.argv)
    window = Window(800, 600)

    window.set_markov_chains(markov_chains)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
