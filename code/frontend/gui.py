import sys
import os
import re

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (
    QMainWindow,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QVBoxLayout,
    QSizePolicy
)

from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor, QPalette
from PyQt6.QtCore import Qt

from code.backend import MarkovChain
from code.backend import Parser


class Window(QMainWindow):

    def __init__(self, width, height):
        super().__init__()

        self._initialize_attributes()
        self._load_style()
        self._setup_ui(width, height)


    '''
    Desc: Initializes class attributes
    Params: None
    Returns: None
    '''
    def _initialize_attributes(self):
        self._markov_chains = None
        self._current_state = ''
        self._prefix_length = 0
        self._word_ending_length = 0
        self._last_text_length = 0
        self._cursor_locked = False

    
    '''
    Desc: Loads and applies the style
    Params: None
    Returns: None
    '''
    def _load_style(self):
        style_path = os.path.join(os.getcwd(), 'code', 'frontend', 'style.qss')
        if os.path.exists(style_path):
            with open(style_path, "r") as file:
                self.setStyleSheet(file.read())
        else:
            print(f"Style file not found at: {style_path}")


    '''
    Desc: Sets up the user interface
    Params:
        width: int - The width of the window
        height: int - The height of the window
    Returns: None
    '''
    def _setup_ui(self, width, height):
        # Set up the main window
        self.setWindowTitle('text-autocomplete-tool')
        self.setGeometry(100, 100, width, height)

        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Add a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        # Create buttons 
        self._buttons = [QPushButton('') for _ in range(3)]
        for button in self._buttons:
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            button.clicked.connect(lambda checked, b=button: self._replace_or_add_word(b.text()))
            button_layout.addWidget(button)

        self._text_edit = CustomTextEdit(self)
        main_layout.addWidget(self._text_edit)

        self._text_edit.textChanged.connect(self._complete_word)

        
    '''
    Desc: Sets the Markov chain for text prediction
    Params:
        markov_chain: MarkovChain - The Markov chain object
    Returns: None
    '''
    def set_markov_chains(self, markov_chains):
        self._markov_chains = markov_chains


    '''
    Desc: Colors a specified text range
    Params:
        start_index: int - The starting index of the text to color
        length: int - The length of the text to color
    Returns: None
    '''
    def _color_text(self, start_index, length):
        self._text_edit.blockSignals(True)
        cursor = self._text_edit.textCursor()
        text = self._text_edit.toPlainText()
        self._text_edit.clear()
    
        for i, char in enumerate(text):
            text_color = self._text_edit.palette().color(QPalette.ColorRole.Text)
            highlighted_text_color = self._text_edit.palette().color(QPalette.ColorRole.Text)
            highlighted_text_color.setAlpha(140)
            
            color = highlighted_text_color if start_index <= i < start_index + length else text_color
            self._set_text_color(cursor, char, color)

        self._text_edit.blockSignals(False)


    '''
    Desc: Sets the color for a specific text
    Params:
        cursor: QTextCursor - The cursor object
        text: str - The text to color
        color: QColor - The color to apply
    Returns: None
    '''
    def _set_text_color(self, cursor, text, color):
        char_format = QTextCharFormat()
        char_format.setForeground(color)
        cursor.setCharFormat(char_format)
        cursor.insertText(text)


    '''
    Desc: Sets the current state prefix lenght and length of word end after prefix
    Params:
        current_state: str - The current state
        prefix_length: int - The length of the prefix
        word_ending_length: int - The length of the word ending
    Returns: None
    '''
    def _set_states(self, current_state='', prefix_length=0, word_ending_length=0):
        self._current_state = current_state
        self._prefix_length = prefix_length
        self._word_ending_length = word_ending_length


    '''
    Desc: Sets the text for a specific button
    Params:
        button_index: int - The index of the button
        text: str - The text to set
    Returns: None
    '''
    def _set_button_text(self, button_index, text):
        self._buttons[button_index].setText(text)


    '''
    Desc: Clears the text of all buttons
    Params: None
    Returns: None
    '''
    def _clear_buttons_text(self):
        for btn_index in range(len(self._buttons)):
            self._set_button_text(btn_index, '')


    '''
    Desc: Sets the text in the text edit widget
    Params:
        text: str - The text to set
    Returns: None
    '''
    def _set_text(self, text):
        self._text_edit.blockSignals(True)
        self._text_edit.setPlainText(text)
        self._text_edit.blockSignals(False)


    '''
    Desc: Gets the current cursor position
    Params: None
    Returns: int - The current cursor position
    '''
    def _get_cursor_position(self):
        cursor = self._text_edit.textCursor()
        return cursor.position()


    '''
    Desc: Sets the cursor position
    Params:
        position: int - The position to set the cursor
    Returns: None
    '''
    def _set_cursor_position(self, position):
        cursor = self._text_edit.textCursor()
        cursor.setPosition(position)
        self._text_edit.setTextCursor(cursor)


    '''
    Desc: Updates the button texts with prefix endings
    Params:
        prefix: str - The prefix to add to the button text
        prefix_endings: list - The list of prefix endings
    Returns: None
    '''
    def _update_buttons(self, prefix, prefix_endings):
        for i, end in enumerate(prefix_endings):
            self._set_button_text(i, prefix + end)


    '''
    Desc: Updates the state after a tab key press
    Params: None
    Returns: None
    '''
    def _update_after_tab(self):
        cursor_pos = self._get_cursor_position()
        text = self._text_edit.toPlainText()[:cursor_pos + self._word_ending_length]

        words = text.split()
        if words:
            self._cursor_locked = True
            self._set_cursor_position(cursor_pos + self._word_ending_length)
            self._set_states(words[-1])

        
    '''
    Desc: Removes text from the text edit widget
    Params:
        cursor_pos: int - The cursor position
        offset: int - The offset for text removal
        text_edit_plaint_text: str - The current text in the widget
    Returns: None
    '''
    def _remove_text(self, cursor_pos, offset, text_edit_plaint_text):
        self._set_text(
            text_edit_plaint_text[:cursor_pos] + 
            text_edit_plaint_text[cursor_pos + offset:]
        )


    '''
    Desc: Updates the state after a cursor change
    Params:
        previous_cursor_position: int - The previous cursor position
    Returns: None
    '''
    def _update_after_cursor_change(self, previous_cursor_position):
        
        if not self._cursor_locked:
            self._cursor_locked = True
            cursor_pos = self._get_cursor_position() 
            text_edit_plaint_text = self._text_edit.toPlainText()

            if len(text_edit_plaint_text) > self._last_text_length:
                self._remove_text(
                    cursor_pos, 
                    self._word_ending_length ,
                    text_edit_plaint_text
                )
            elif len(text_edit_plaint_text) < self._last_text_length: 
                self._remove_text(
                    cursor_pos, 
                    self._word_ending_length, 
                    text_edit_plaint_text
                )
            else:
                self._remove_text(
                    previous_cursor_position, 
                    self._word_ending_length, 
                    text_edit_plaint_text
                )

            self._set_states()
            self._set_cursor_position(0)

            current_text_length = len(self._text_edit.toPlainText())
            self._color_text(current_text_length, current_text_length)

            if cursor_pos >= current_text_length:
                self._set_cursor_position(current_text_length)
            else:
                self._set_cursor_position(cursor_pos)


    '''
    Desc: Checks if the text ends with a sentence-ending character
    Params:
        text: str - The text to check
    Returns: bool - True if the text ends with a sentence-ending character, False otherwise
    '''
    def _match_sentence_end(self, text):
        return bool(re.search(r'[.!?\s]$', text))

    
    '''
    Desc: Updates the text in the text edit widget
    Params:
        text: str - The new text to set
        cursor_pos: int - The new cursor position
    Returns: None
    '''
    def _update_text(self, text, cursor_pos):
        self._set_text(text)
        self._color_text(cursor_pos, self._word_ending_length)
        self._set_cursor_position(cursor_pos)
        self._last_text_length = len(self._text_edit.toPlainText())


    '''
    Desc: Processes the end of a word in a text
    Params:
        words: list - The list of words in the text
    Returns: None
    '''
    def _process_word_end(self, words):
        if words:
            self._set_states(words[-len(self._markov_chains):], self._prefix_length, self._word_ending_length)
            
            words = []
            for i, markov_chain in enumerate(reversed(self._markov_chains)):
                top_three_words = markov_chain.get_words(tuple(self._current_state[-(len(self._markov_chains) - i):]))
                words.extend(top_three_words)

            print(f'current state : {self._current_state}')
            print(f'end words : {words}')
            words = words[:3]

            next_states = [val[0] for val in words]
            self._update_buttons(prefix='', prefix_endings=next_states)
    

    '''
    Desc: Processes a word for auto-completion
    Params:
        words: list - The list of words in the text
    Returns: str - The new text with the processed word
    '''
    def _process_word(self, words):
        last_word = words[-1]
        last_words = words[-len(self._markov_chains):]
        # prefix_words = self._markov_chain.get_words_with_prefix(last_word)


        


        prefix_words = []
        for i, markov_chain in enumerate(reversed(self._markov_chains)):
            top_three_words = markov_chain.get_words_with_prefix(tuple(last_words[-(len(self._markov_chains) - i):]))
            prefix_words.extend(top_three_words)

        print(f'last words : {last_words}')
        print(f'prefix words : {prefix_words}')

        prefix_words = prefix_words[:3]
        next_prefix_states = [val[0] for val in prefix_words]
        word_ending = next_prefix_states[0] if next_prefix_states else ''

        self._update_buttons(last_word, next_prefix_states)
        self._set_states(self._current_state, len(last_word), len(word_ending))

        completed_word = last_word + word_ending
        words[-1] = completed_word
        new_text = ' '.join(words)

        return new_text


    '''
    Desc: Processes the text for auto-completion
    Params:
        text: str - The text to process
    Returns: str - The processed text
    '''
    def _process_text(self, text):
        new_text = text
        words = text.split()

        if self._match_sentence_end(text):
            self._process_word_end(words)
        elif words:
            new_text = self._process_word(words)
        
        return new_text


    '''
    Desc: Completes the current word
    Params: None
    Returns: None
    '''
    def _complete_word(self):
        self._cursor_locked = False
        cursor_pos = self._get_cursor_position()
        text_edit_plaint_text = self._text_edit.toPlainText()

        text_until_cursor = text_edit_plaint_text[:cursor_pos]
        text_after_cursor = text_edit_plaint_text[cursor_pos:]
        
        words = text_until_cursor.split()

        self._clear_buttons_text()

        new_text = self._process_text(text_until_cursor)
        self._update_text(new_text + text_after_cursor, cursor_pos)


    '''
    Desc: Replaces or adds a word in the text
    Params:
        new_word: str - The new word to add or replace with
    Returns: None
    '''
    def _replace_or_add_word(self, new_word):
        if not new_word:
            return

        self._cursor_locked = True
        cursor_pos = self._get_cursor_position()
        text = self._text_edit.toPlainText()

        text_until_word_in_crusor_range = text[:cursor_pos - self._prefix_length]
        text_after_word_in_crusor_range = text[cursor_pos + self._word_ending_length:]

        self._clear_buttons_text()

        new_cursor_pos = len(text_until_word_in_crusor_range) + len(new_word)
        new_text = text_until_word_in_crusor_range + new_word + text_after_word_in_crusor_range
        self._update_text(new_text, new_cursor_pos)
       


class CustomTextEdit(QTextEdit):
   
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent

        self._last_cursor_position = self.textCursor().position()
        self.cursorPositionChanged.connect(self.on_cursor_position_changed)


    '''
    Desc: Handles cursor position changes
    Params: None
    Returns: None
    '''
    def on_cursor_position_changed(self):
        current_cursor_position = self.textCursor().position()

        if current_cursor_position != self._last_cursor_position:
            self._parent._update_after_cursor_change(self._last_cursor_position)
            self._last_cursor_position = current_cursor_position


    '''
    Desc: Handles key press events
    Params:
        event: QKeyEvent - The key event
    Returns: None
    '''
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            if self._parent:
                self._parent._update_after_tab()
                self._parent._complete_word()

            return
        super().keyPressEvent(event)

