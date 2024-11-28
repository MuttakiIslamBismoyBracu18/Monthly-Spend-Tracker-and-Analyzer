from PyQt5.QtWidgets import QApplication
from model import SpendTrackerModel
from view import SpendTrackerView
from controller import SpendTrackerController
import sys

def main():
    app = QApplication(sys.argv)
    model = SpendTrackerModel()
    view = SpendTrackerView()
    controller = SpendTrackerController(model, view)
    view.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
