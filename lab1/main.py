import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from vigenere import vigenere
from gamma import gamma

RUSSIAN_ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
ENGLISH_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_connections()
        
    def load_ui(self):
        ui_file = QFile("mainwindow.ui")
        if not ui_file.open(QIODevice.ReadOnly):
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл UI: {ui_file.errorString()}")
            sys.exit(-1)
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        if not self.ui:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить UI")
            sys.exit(-1)

        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("LR1")
        
    def setup_connections(self):
        self.ui.showResultBtn.clicked.connect(self.process_encryption)
        self.ui.loadFileBtn.clicked.connect(self.load_file)
        self.ui.saveFileBtn.clicked.connect(self.save_file)
        self.ui.encryptRadioBtn.setChecked(True)
        self.ui.languageComboBox.setCurrentIndex(0)
        self.ui.methodComboBox.setCurrentIndex(0)
    
    def get_alphabet(self) -> str:
        current_language = self.ui.languageComboBox.currentText()
        if current_language == "Русский":
            return RUSSIAN_ALPHABET
        elif current_language == "Английский":
            return ENGLISH_ALPHABET
        else:
            return RUSSIAN_ALPHABET
    
    def validate_text_for_alphabet(self, text: str, alphabet: str) -> tuple[bool, str]:
        if not text:
            return True, ""
        
        alphabet_upper = alphabet.upper()
        alphabet_lower = alphabet.lower()
        invalid_chars = []
        
        for char in text:
            if char.isalpha():
                if char.upper() not in alphabet_upper and char.lower() not in alphabet_lower:
                    if char not in invalid_chars:
                        invalid_chars.append(char)
        
        if invalid_chars:
            return False, ", ".join(invalid_chars[:5])
        return True, ""
    
    def process_encryption(self):
        text = self.ui.inputText.toPlainText()
        key = self.ui.keyInputText.toPlainText()
        
        if not text:
            QMessageBox.warning(self, "Предупреждение", "Введите исходный текст")
            return
        
        if not key:
            QMessageBox.warning(self, "Предупреждение", "Введите ключ")
            return
        
        alphabet = self.get_alphabet()
        current_language = self.ui.languageComboBox.currentText()
        mode = 'encrypt' if self.ui.encryptRadioBtn.isChecked() else 'decrypt'
        method = self.ui.methodComboBox.currentText()
            
        is_valid_text, invalid_chars_text = self.validate_text_for_alphabet(text, alphabet)
        is_valid_key, invalid_chars_key = self.validate_text_for_alphabet(key, alphabet)
        
        if not is_valid_text:
            QMessageBox.warning(
                self,
                "Ошибка языка",
                f"В исходном тексте найдены символы, не соответствующие выбранному языку ({current_language}):\n{invalid_chars_text}\n\nПожалуйста, используйте только символы выбранного алфавита."
            )
            return
        
        if not is_valid_key:
            QMessageBox.warning(
                self,
                "Ошибка языка",
                f"В ключе найдены символы, не соответствующие выбранному языку ({current_language}):\n{invalid_chars_key}\n\nПожалуйста, используйте только символы выбранного алфавита."
            )
            return
        
        if method == "Шифр Виженера":
            result = vigenere(text, key, alphabet, mode)
        else:
            result = gamma(text, key, alphabet, mode)
        
        self.ui.resultText.setPlainText(result)
    
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                if len(lines) >= 2:
                    self.ui.inputText.setPlainText(lines[0].rstrip('\n\r'))
                    self.ui.keyInputText.setPlainText(lines[1].rstrip('\n\r'))
                elif len(lines) == 1:
                    self.ui.inputText.setPlainText(lines[0].rstrip('\n\r'))
                    self.ui.keyInputText.setPlainText("")
                else:
                    self.ui.inputText.setPlainText("")
                    self.ui.keyInputText.setPlainText("")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def save_file(self):
        input_text = self.ui.inputText.toPlainText()
        key_text = self.ui.keyInputText.toPlainText()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(input_text + '\n')
                    f.write(key_text + '\n')
                QMessageBox.information(self, "Успех", "Файл успешно сохранен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
