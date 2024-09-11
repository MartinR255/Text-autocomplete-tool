from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile, QTextStream

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
    
    max_nth_order = 3
    markov_chains = [MarkovChain(parsed_data, i) for i in range(1, max_nth_order + 1)]


    app = QApplication(sys.argv)
    window = Window(800, 600)

    window.set_markov_chains(markov_chains)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
