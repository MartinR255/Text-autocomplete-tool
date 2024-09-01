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
    
    markov_chain = MarkovChain(parsed_data)

    app = QApplication(sys.argv)

    # Load and apply the stylesheet 
    style_file = QFile("code/frontend/style.qss")
    if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())

    window = Window(800, 600)

    window.set_markov_chain(markov_chain)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
