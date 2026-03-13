import os
import re
import sys

from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from rsa import generate_keys
from signature import sign_file, verify_file


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._load_ui()
        self._connect()

    def _load_ui(self) -> None:
        ui_file = QFile("mainwindow.ui")
        if not ui_file.open(QIODevice.ReadOnly):
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть UI: {ui_file.errorString()}")
            sys.exit(-1)

        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        if not self.ui:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить UI")
            sys.exit(-1)

        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("LR4 - ЭЦП")

    def _connect(self) -> None:
        self.ui.generateKeysBtn.clicked.connect(self._generate_keys)
        self.ui.savePublicKeyBtn.clicked.connect(self._save_public_key_clicked)
        self.ui.savePrivateKeyBtn.clicked.connect(self._save_private_key_clicked)

        self.ui.chooseSignFileBtn.clicked.connect(self._choose_sign_file)
        self.ui.loadPrivateKeyBtn.clicked.connect(self._choose_private_key)
        self.ui.signFileBtn.clicked.connect(self._sign_file)

        self.ui.chooseVerifyFileBtn.clicked.connect(self._choose_verify_file)
        self.ui.chooseSignatureFileBtn.clicked.connect(self._choose_verify_sig)
        self.ui.loadPublicKeyBtn.clicked.connect(self._choose_public_key)
        self.ui.verifyBtn.clicked.connect(self._verify)
    
    def load_key_values(self, path: str) -> dict[str, int]:
        _KEY_LINE_RE = re.compile(r"^\s*([ned])\s*=\s*([0-9]+)\s*$", re.IGNORECASE)
        values: dict[str, int] = {}
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                m = _KEY_LINE_RE.match(line)
                if not m:
                    continue
                k = m.group(1).lower()
                v = int(m.group(2))
                values[k] = v
        return values


    def load_public_key(self, path: str) -> tuple[int, int]:
        values = self.load_key_values(path)
        if "n" not in values or "e" not in values:
            raise ValueError("Некорректный формат открытого ключа (нужны n и e)")
        return values["n"], values["e"]


    def load_private_key(self, path: str) -> tuple[int, int]:
        values = self.load_key_values(path)
        if "n" not in values or "d" not in values:
            raise ValueError("Некорректный формат закрытого ключа (нужны n и d)")
        return values["n"], values["d"]


    def save_public_key(self, path: str, n: int, e: int) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"n={n}\n")
            f.write(f"e={e}\n")


    def save_private_key(self, path: str, n: int, d: int) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"n={n}\n")
            f.write(f"d={d}\n")

    def _generate_keys(self) -> None:
        try:
            public_key, private_key = generate_keys()
            e, n = public_key
            d, _ = private_key
            self.ui.nLineEdit.setText(str(n))
            self.ui.eLineEdit.setText(str(e))
            self.ui.dLineEdit.setText(str(d))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка генерации ключей", str(exc))

    def _save_public_key_clicked(self) -> None:
        n = self.ui.nLineEdit.text().strip()
        e = self.ui.eLineEdit.text().strip()
        if not n or not e:
            QMessageBox.warning(self, "Нет данных", "Сначала сгенерируйте ключи.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить открытый ключ",
            "",
            "Key (*.key);;All files (*)",
        )
        if not path:
            return
        try:
            self.save_public_key(path, int(n), int(e))
            QMessageBox.information(self, "Готово", f"Открытый ключ сохранён:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def _save_private_key_clicked(self) -> None:
        n = self.ui.nLineEdit.text().strip()
        d = self.ui.dLineEdit.text().strip()
        if not n or not d:
            QMessageBox.warning(self, "Нет данных", "Сначала сгенерируйте ключи.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить закрытый ключ",
            "",
            "Key (*.key);;All files (*)",
        )
        if not path:
            return
        try:
            self.save_private_key(path, int(n), int(d))
            QMessageBox.information(self, "Готово", f"Закрытый ключ сохранён:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def _choose_sign_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Выбрать файл для подписи", "", "All files (*)")
        if not path:
            return
        self.ui.signFileLineEdit.setText(path)

    def _choose_private_key(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить закрытый ключ",
            "",
            "Key (*.key);;All files (*)",
        )
        if not path:
            return
        self.ui.privateKeyLineEdit.setText(path)

    def _sign_file(self) -> None:
        file_path = self.ui.signFileLineEdit.text().strip()
        key_path = self.ui.privateKeyLineEdit.text().strip()

        if not file_path:
            QMessageBox.warning(self, "Нет файла", "Выберите файл для подписи.")
            return
        if not key_path:
            QMessageBox.warning(self, "Нет ключа", "Загрузите закрытый ключ.")
            return

        sig_path = file_path + ".sig"

        try:
            n, d = self.load_private_key(key_path)
            sign_file(file_path, sig_path, n, d)
            QMessageBox.information(self, "Готово", f"Подпись создана:\n{sig_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка подписи", str(exc))

    def _choose_verify_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Выбрать исходный файл", "", "All files (*)")
        if not path:
            return
        self.ui.verifyFileLineEdit.setText(path)
        if not self.ui.signatureFileLineEdit.text().strip():
            auto_sig = path + ".sig"
            if os.path.exists(auto_sig):
                self.ui.signatureFileLineEdit.setText(auto_sig)

    def _choose_verify_sig(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать файл подписи",
            "",
            "Signature (*.sig);;All files (*)",
        )
        if not path:
            return
        self.ui.signatureFileLineEdit.setText(path)

    def _choose_public_key(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить открытый ключ",
            "",
            "Key (*.key);;All files (*)",
        )
        if not path:
            return
        self.ui.publicKeyLineEdit.setText(path)

    def _verify(self) -> None:
        file_path = self.ui.verifyFileLineEdit.text().strip()
        sig_path = self.ui.signatureFileLineEdit.text().strip()
        key_path = self.ui.publicKeyLineEdit.text().strip()

        if not file_path:
            QMessageBox.warning(self, "Нет файла", "Выберите исходный файл.")
            return
        if not sig_path:
            QMessageBox.warning(self, "Нет подписи", "Выберите файл подписи.")
            return
        if not key_path:
            QMessageBox.warning(self, "Нет ключа", "Загрузите открытый ключ.")
            return

        try:
            n, e = self.load_public_key(key_path)
            ok = verify_file(file_path, sig_path, n, e)
        except Exception as exc:
            self.ui.verifyResultLabel.setText("Результат: ошибка")
            QMessageBox.critical(self, "Ошибка проверки", str(exc))
            return

        if ok:
            self.ui.verifyResultLabel.setText("Результат: подпись корректна")
            QMessageBox.information(self, "Проверка", "Подпись корректна.")
        else:
            self.ui.verifyResultLabel.setText("Результат: подпись НЕ корректна")
            QMessageBox.warning(self, "Проверка", "Подпись НЕ корректна.")


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

