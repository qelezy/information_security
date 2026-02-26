import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QFileDialog,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice

from rsa import generate_keys, encrypt_text, decrypt_text


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_connections()

    def load_ui(self):
        ui_file = QFile("mainwindow.ui")
        if not ui_file.open(QIODevice.ReadOnly):
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось открыть файл UI: {ui_file.errorString()}",
            )
            sys.exit(-1)

        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        if not self.ui:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить UI")
            sys.exit(-1)

        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("LR3 - RSA")

    def setup_connections(self):
        self.ui.encryptRadioBtn.setChecked(True)
        self.ui.showResultBtn.clicked.connect(self.process_action)
        self.ui.generateKeysBtn.clicked.connect(self.generate_keys_clicked)
        self.ui.loadFileBtn.clicked.connect(self.load_from_file)
        self.ui.saveFileBtn.clicked.connect(self.save_to_file)

    def _get_int_from_line_edit(self, line_edit, name: str) -> int:
        text = line_edit.text().strip()
        if not text:
            raise ValueError(f"Поле '{name}' пустое")
        try:
            value = int(text)
        except ValueError as exc:
            raise ValueError(f"Поле '{name}' должно быть целым числом") from exc
        if value <= 0:
            raise ValueError(f"Поле '{name}' должно быть положительным")
        return value

    def generate_keys_clicked(self):
        try:
            public_key, private_key = generate_keys(512)
            e, n = public_key
            d, _ = private_key
            self.ui.eValueLineEdit.setText(str(e))
            self.ui.dValueLineEdit.setText(str(d))
            self.ui.nValueLineEdit.setText(str(n))
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка генерации ключей",
                f"Не удалось сформировать ключи:\n{str(e)}",
            )

    def process_action(self):
        input_text = self.ui.inputTextEdit.toPlainText()
        if not input_text:
            QMessageBox.warning(self, "Предупреждение", "Введите текст для обработки")
            return

        try:
            n = self._get_int_from_line_edit(self.ui.nValueLineEdit, "n")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ключа", str(e))
            return

        try:
            if self.ui.encryptRadioBtn.isChecked():
                e_value = self._get_int_from_line_edit(
                    self.ui.eValueLineEdit, "e"
                )
                result = encrypt_text(input_text, e_value, n)
            else:
                d_value = self._get_int_from_line_edit(
                    self.ui.dValueLineEdit, "d"
                )
                result = decrypt_text(input_text, d_value, n)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка обработки",
                f"Произошла ошибка при обработке данных:\n{str(e)}",
            )
            return

        self.ui.resultTextEdit.setPlainText(result)

    def load_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить ключи и текст",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)",
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка чтения файла",
                f"Не удалось загрузить файл:\n{str(e)}",
            )
            return

        try:
            e_val = lines[0].strip() if len(lines) > 0 else ""
            d_val = lines[1].strip() if len(lines) > 1 else ""
            n_val = lines[2].strip() if len(lines) > 2 else ""
            text_part = "".join(lines[3:]) if len(lines) > 3 else ""

            self.ui.eValueLineEdit.setText(e_val)
            self.ui.dValueLineEdit.setText(d_val)
            self.ui.nValueLineEdit.setText(n_val)
            self.ui.inputTextEdit.setPlainText(text_part)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка разбора файла",
                f"Некорректный формат файла:\n{str(e)}",
            )

    def save_to_file(self):
        e_val = self.ui.eValueLineEdit.text().strip()
        d_val = self.ui.dValueLineEdit.text().strip()
        n_val = self.ui.nValueLineEdit.text().strip()
        text_val = self.ui.inputTextEdit.toPlainText()

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить ключи и текст",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)",
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(e_val + "\n")
                f.write(d_val + "\n")
                f.write(n_val + "\n")
                f.write(text_val)
            QMessageBox.information(self, "Успех", "Данные успешно сохранены")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка сохранения файла",
                f"Не удалось сохранить файл:\n{str(e)}",
            )


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
