from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QLineEdit,
    QComboBox,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

#TODO
class CategoryWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.addCategory = QPushButton("Add Category")
        self.addCategory.clicked.connect(self.addCategoryWindow)

        #TODO: load past categories and colors from database
        self.categories = []
        self.colors = []
        self.categoryButtons = {}

        for i in range(len(self.categories)):
            self.categoryButtons[self.categories[i]] = RoundedButton(self.categories[i], self.colors[i])

        layout = QHBoxLayout()
        layout.addWidget(self.addCategory)
        for button in self.categoryButtons.values():
            layout.addWidget(button)

        self.setLayout(layout)

    def addCategoryWindow(self):
        self.w = AddCategoryWindow()
        self.w.show()
        self.w.categoryInfo.connect(self.addCategoryButton)

    def addCategoryButton(self, info):
        self.w.close()
        self.w = None
        self.categoryButtons[info[0]] = RoundedButton(info[0], info[1])
        self.update()
        

class AddCategoryWindow(QWidget):

    categoryInfo = QtCore.pyqtSignal(object)

    #TODO: maybe make color wheel later
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'gray', 'black']

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        #text field
        self.textField = QLineEdit()
        self.textField.setMaxLength(10)
        self.textField.setPlaceholderText("Category Name")
        self.name = "Default"
        self.textField.editingFinished.connect(self.text_input)

        #color selector
        self.colorSelector = QComboBox()
        self.color = self.colors[0]
        self.colorSelector.currentTextChanged.connect(self.colorChanged)

        #done button
        self.doneButton = QPushButton("Done")
        self.doneButton.clicked.connect(self.returnInfo)

        layout.addWidget(self.textField)
        layout.addWidget(self.colorSelector)
        layout.addWidget(self.doneButton)
        self.setLayout(layout)

    def text_input(self):
        self.name = self.textField.text()

    def colorChanged(self, s):
        self.color = s

    def returnInfo(self):
        self.categoryInfo.emit((self.name, self.color))

#TODO
class RoundedButton(QWidget):
    def __init__(self, text, color):
        super(RoundedButton, self).__init__()
        self.label = text
        self.color = color

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor(self.color))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        painter.drawRoundedRect(10, 10, 20, 10, 5, 5)

    def mousePressEvent(self, e):
        #TODO: add editable task widget to TaskList
        pass

#TODO
class TaskListWidget(QWidget):

    def __init__(self):
        super().__init__()
        #TODO: load all tasks from database
        self.tasks = []

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Task 1"))
        layout.addWidget(QLabel("Task 2"))
        layout.addWidget(QLabel("Task 3"))
        self.setLayout(layout)

#TODO
class TaskWidget(QWidget):
    
    def __init__(self):
        super(TaskWidget, self).__init__()