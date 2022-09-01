from functools import partial
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor, QFontMetrics
from PyQt6.QtCore import QSize, Qt, QRectF, QSortFilterProxyModel
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

import faulthandler

faulthandler.enable()

class CategoryWidget(QWidget):

    def __init__(self, model):
        super().__init__()

        #TODO: load past categories and colors from database
        self.categories = []
        self.colors = []
        self.categoryButtons = {}
        self.model = model

        for i in range(len(self.categories)):
            b = RoundedButton(self.categories[i], self.colors[i])
            b.clicked.connect(lambda: self.model.addTask((self.categories[i], self.colors[i])))
            self.categoryButtons[self.categories[i]] = b

        self.layout = QHBoxLayout()
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
        button.clicked.connect(lambda: self.model.addTask(info))
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
        self.textField.textEdited.connect(self.text_input)

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
class TaskListWidget(QWidget):

    def __init__(self, model):
        super().__init__()

        self.taskList = QTableView()

        #due date sorting
        #TODO custom proxy filter model for correct date sorting
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(model)
        self.taskList.setModel(proxyModel)
        self.taskList.setSortingEnabled(True)
        self.taskList.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        self.taskList.reset()

        #aesthetic
        self.taskList.setMinimumSize(100, 100)
        self.taskList.setColumnWidth(0, 30)
        self.taskList.horizontalHeader().setStretchLastSection(True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.taskList)
        self.setLayout(self.layout)
class TaskModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, tasks=None, cols=None, **kwargs):
        super(TaskModel, self).__init__(*args, **kwargs)
        self.tasks = tasks or []
        self.cols = cols

    def data(self, index, role):
        value = self.tasks[index.row()][index.column()]

        if role == Qt.ItemDataRole.DisplayRole:
            if isinstance(value, datetime):
                return value.strftime('%m-%d-%Y')
            
            if isinstance(value, bool):
                return None

            return value
        
        if role == Qt.ItemDataRole.BackgroundRole and index.column() == 3:
            return QtGui.QColor(self.tasks[index.row()][-1])

        if role == Qt.ItemDataRole.CheckStateRole:
            if index.column() == 0:
                if self.tasks[index.row()][0] == True:
                    return Qt.CheckState.Checked
                return Qt.CheckState.Unchecked

    def rowCount(self, index):
        return len(self.tasks)

    def columnCount(self, index):
        return len(self.tasks[0])-1

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if self.cols:
                    return str(self.cols[section])

            if orientation == Qt.Orientation.Vertical:
                return str(section+1)

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            if value == Qt.CheckState.Checked.value:
                self.tasks[index.row()][0] = True
            else:
                self.tasks[index.row()][0] = False
            return True
        if role == Qt.ItemDataRole.EditRole:
            if index.column() == 3:
                self.tasks[index.row()][3] = value
            elif index.column() == 1:
                try: 
                    dt = datetime.strptime(value, "%m-%d-%Y")
                    self.tasks[index.row()][1] = dt
                    return True
                except:
                    return False
        return False

    def refresh(self):
        self.tasks = [t for t in self.tasks if not t[0]]
        self.layoutChanged.emit()

    def addTask(self, info):
        self.tasks.append([False, datetime.today(), info[0], "Task Description", info[1]])
        self.layoutChanged.emit()
        

