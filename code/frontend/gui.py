import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtGui import QTextCharFormat, QTextCursor, QColor, QFont


class Window:

    def __init__(self, width, height):
        self._markov_chain = None
        self._current_state = ''

        # Initialize the QApplication
        self._app = QApplication(sys.argv)

        # Load the external style file
        with open(f'{os.getcwd().replace('\\', '/')}/code/frontend/style.qss', "r") as file:
            self._app.setStyleSheet(file.read())

        # Create the main window
        self._window = QMainWindow()
        self._window.setWindowTitle('text-autocomplete-tool')
        self._window.setGeometry(100, 100, width, height)

        # Create the central widget and layout
        central_widget = QWidget(self._window)
        self._window.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Add a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        # Create buttons 
        self._buttons = [QPushButton('') for _ in range(3)]
        for button in self._buttons:
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            button.clicked.connect(lambda _, b=button: self._replace_or_add_word(b.text()))

        # Add buttons to the layout
        for btn in self._buttons:
            button_layout.addWidget(btn)

        # Add a QTextEdit below the buttons
        self._text_edit = QTextEdit(self._window)
        main_layout.addWidget(self._text_edit) 

        # Add event listeners to QTextEdit
        self._text_edit.textChanged.connect(self._update_buttons_with_last_word)  
        self._text_edit.textChanged.connect(self._color_text)


    def _color_text(self):
        ...


    def _set_text_color(self, cursor, text, color):
        char_format = QTextCharFormat()
        char_format.setForeground(color)
        
        cursor.setCharFormat(char_format)
        cursor.insertText(text)


    def _set_button_text(self, button_index, text):
        self._buttons[button_index].setText(text)


    def _clear_buttons_text(self):
        for btn_index in range(len(self._buttons)):
            self._set_button_text(btn_index, '')


    def _update_buttons_with_last_word(self):
        cursor = self._text_edit.textCursor()
        cursor_pos = cursor.position() 
        text = self._text_edit.toPlainText()[:cursor_pos]

        if text:
            words = text.split()

            top_three_next_states = ['', '', '']
            if text[-1].isspace():
                self._current_state = words[-1] if words else ''
                top_three_next_states = [val[0] for val in self._markov_chain.get_word(self._current_state)]

            for i, word in enumerate(top_three_next_states):
                self._set_button_text(i, word)


    def _replace_or_add_word(self, new_word):
        cursor = self._text_edit.textCursor()
        cursor_pos = cursor.position()
        text = self._text_edit.toPlainText()[:cursor_pos]

        new_text = text
        self._current_state = new_word
        
        if text and text[-1].isspace():
            new_text += new_word
        else:
            words = text.split()
            if words and new_word:
                words[-1] = new_word 
                new_text = ' '.join(words)

        self._clear_buttons_text()
        self._text_edit.blockSignals(True)
        self._text_edit.setPlainText(new_text + self._text_edit.toPlainText()[cursor_pos:])
        self._text_edit.blockSignals(False)
        cursor.setPosition(len(new_text))
        self._text_edit.setTextCursor(cursor)


    def set_markov_chain(self, markov_chain):
        self._markov_chain = markov_chain


    def run(self):
        self._window.show()
        sys.exit(self._app.exec())
        
