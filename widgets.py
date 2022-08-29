from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor, QFontMetrics
from PyQt6.QtCore import QSize, Qt, QRectF
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
    QListView,
    QTableView
)
from datetime import datetime

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

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.addCategory)
        for button in self.categoryButtons.values():
            self.layout.addWidget(button)

        self.setLayout(self.layout)        

    def addCategoryWindow(self):
        self.w = AddCategoryWindow()
        self.w.show()
        self.w.categoryInfo.connect(self.addCategoryButton)

    def addCategoryButton(self, info):
        self.w.close()
        self.w = None
        button = RoundedButton(info[0], info[1])
        self.categoryButtons[info[0]] = button
        self.layout.addWidget(button)
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
        self.colorSelector.addItems(self.colors)
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
class RoundedButton(QPushButton):
    def __init__(self, text, color):
        super(RoundedButton, self).__init__()
        self.label = text
        self.setText(self.label)
        self.color = color
        self.bordersize = 10
        self.font = QtGui.QFont()
        self.font.setFamily('Times')
        self.font.setBold(True)

    def paintEvent(self, e):
        painter = QPainter(self)
        pen = QtGui.QPen()
        path = QPainterPath()
        pen = QPen(QColor(self.color))
        painter.setPen(pen)
        brush = QBrush(QColor(self.color))
        painter.setBrush(brush)
        
        #rounded rect
        rect = QRectF(e.rect())
        rect.adjust(self.bordersize/2, self.bordersize/2, -self.bordersize/2, -self.bordersize/2)
        path.addRoundedRect(rect, 10, 10)
        painter.setClipPath(path)
        painter.fillPath(path, painter.brush())
        painter.strokePath(path, painter.pen())

        #text
        painter.setPen(QPen(QColor('white')))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.label)
        painter.end()

    def mousePressEvent(self, e):
        #TODO: add editable task widget to TaskList
        print("Clicked %s" % self.label)

#TODO
class TaskListWidget(QWidget):

    def __init__(self, model):
        super().__init__()

        self.taskList = QTableView()
        self.taskList.setModel(model)
        self.taskList.setMinimumSize(100, 100)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.taskList)
        self.setLayout(self.layout)

#TODO
class TaskWidget(QWidget):
    
    def __init__(self):
        super(TaskWidget, self).__init__()

class TaskModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, tasks=None, **kwargs):
        super(TaskModel, self).__init__(*args, **kwargs)
        self.tasks = tasks or []

    def data(self, index, role):
        value = self.tasks[index.row()][index.column()]

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return None

            if isinstance(value, datetime):
                return value.strftime('%d-%m-%Y')

            return value
        
        if role == Qt.ItemDataRole.DecorationRole:
            if isinstance(value, bool):
                if value:
                    return QtGui.QIcon('tick.png')
        
        #if role == Qt.ItemDataRole.BackgroundRole:
        #    return QtGui.QColor(self.tasks[index.row()][-1])

    def rowCount(self, index):
        return len(self.tasks)

    def columnCount(self, index):
        return 5