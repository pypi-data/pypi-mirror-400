
import sys, os, shutil, argparse
from PyQt6 import QtWidgets, QtGui, QtCore

__version__ = "0.0.1"

class _DownBar:
    def __init__(self, p): self.p = p
    def colorwnyz(self, c): self.p.bar_color = c

class _Downloader:
    def __init__(self, p): self.p = p
    def download(self, f): self.p.files.append(f)

class PYSetupCore:
    def __init__(self):
        self.title_text = "PYSetup Installer"
        self.doc_text = ""
        self.bar_color = "blue"
        self.clues = []
        self.logo_path = None
        self.files = []

    def egui(self):
        app = QtWidgets.QApplication(sys.argv)
        w = QtWidgets.QWidget()
        w.setWindowTitle(self.title_text)
        w.setFixedSize(500, 360)
        v = QtWidgets.QVBoxLayout()

        if self.logo_path and os.path.exists(self.logo_path):
            l = QtWidgets.QLabel()
            p = QtGui.QPixmap(self.logo_path)
            if not p.isNull():
                l.setPixmap(p.scaled(
                    96, 96,
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation
                ))
                l.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                v.addWidget(l)

        t = QtWidgets.QLabel(self.title_text)
        t.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        t.setStyleSheet("font-size:18px;font-weight:bold")
        v.addWidget(t)

        d = QtWidgets.QLabel(self.doc_text)
        d.setWordWrap(True)
        d.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        v.addWidget(d)

        self.bar = QtWidgets.QProgressBar()
        self.bar.setStyleSheet(
            f"QProgressBar::chunk{{background:{self.bar_color};}}"
        )
        v.addWidget(self.bar)

        b = QtWidgets.QPushButton("Kur")
        b.clicked.connect(self.install)
        v.addWidget(b)

        w.setLayout(v)
        w.show()
        sys.exit(app.exec())

    def install(self):
        target = QtWidgets.QFileDialog.getExistingDirectory(
            None, "Kurulum Dizini Seç"
        )
        if not target:
            return

        self.bar.setMaximum(len(self.files))
        for i, f in enumerate(self.files, 1):
            shutil.copy2(f, os.path.join(target, os.path.basename(f)))
            self.bar.setValue(i)

        QtWidgets.QMessageBox.information(
            None, "Bitti", "Kurulum tamamlandı"
        )

    def __call__(self, name): return _Downloader(self)
    def title__(self, t): self.title_text = t
    def document__(self, d): self.doc_text = d
    def downbar(self): return _DownBar(self)
    def clue__(self, *c): self.clues = list(c)
    def logo__(self, p): self.logo_path = p

    def info(self, log=True):
        path = os.path.join(
            os.path.expanduser("~"),
            "Desktop",
            f"{self.title_text}.exe"
        )
        if log:
            print(f"File Location: {path}")
        return path

pysetup = PYSetupCore()

def _cli():
    p = argparse.ArgumentParser()
    p.add_argument("--setup.me", dest="setup_me")
    p.add_argument("--EmbeddedLogo", dest="logo")
    a = p.parse_args()
    if a.logo:
        pysetup.logo__(a.logo)
    pysetup.egui()

if __name__ == "__main__":
    _cli()
