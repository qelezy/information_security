import sys
import secrets
import string
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from des import des


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
        self.setWindowTitle("LR2")
        
    def setup_connections(self):
        self.ui.showResultBtn.clicked.connect(self.process_encryption)
        self.ui.loadFileBtn.clicked.connect(self.load_file)
        self.ui.saveFileBtn.clicked.connect(self.save_file)
        self.ui.formKeyBtn.clicked.connect(self.generate_key)
        self.ui.encryptRadioBtn.setChecked(True)
    
    def generate_key(self):
        try:
            chars = string.ascii_letters + string.digits
            key_text = ''.join(secrets.choice(chars) for _ in range(8))
            self.ui.keyText.setPlainText(key_text)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сгенерировать ключ:\n{str(e)}")
    
    def get_key_from_input(self) -> str:
        key_text = self.ui.keyText.toPlainText().strip()
        
        if not key_text:
            QMessageBox.warning(
                self,
                "Ключ не задан",
                "Пожалуйста, введите ключ вручную или нажмите кнопку 'Сформировать ключ' для автоматической генерации."
            )
            return None
        
        try:
            key_bytes = key_text.encode("utf-8")
            if len(key_bytes) != 8:
                raise ValueError(
                    f"Ключ DES должен кодироваться в ровно 8 байт (64 бита), "
                    f"сейчас {len(key_bytes)} байт.\n\n"
                )
            return key_text
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Ошибка ключа",
                f"Неверный формат ключа:\n{str(e)}"
            )
            return None
    
    def process_encryption(self):
        input_text = self.ui.inputText.toPlainText()
        
        if not input_text:
            QMessageBox.warning(self, "Предупреждение", "Введите исходный текст")
            return
        
        key_text = self.get_key_from_input()
        if key_text is None:
            return
        
        is_encrypt = self.ui.encryptRadioBtn.isChecked()
        mode = "encrypt" if is_encrypt else "decrypt"
        
        try:
            result = des(input_text, key_text, mode)
            self.ui.resultText.setPlainText(result)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обработке данных:\n{str(e)}")
    
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
                    self.ui.keyText.setPlainText(lines[1].rstrip('\n\r'))
                elif len(lines) == 1:
                    self.ui.inputText.setPlainText(lines[0].rstrip('\n\r'))
                    self.ui.keyText.setPlainText("")
                else:
                    self.ui.inputText.setPlainText("")
                    self.ui.keyText.setPlainText("")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def save_file(self):
        input_text = self.ui.inputText.toPlainText()
        key_text = self.ui.keyText.toPlainText()
        
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
