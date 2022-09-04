from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QPen, QColor, QAction
from PyQt6.QtCore import Qt, QRectF, QEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QTableView,
    QColorDialog,
    QMenu
)
from datetime import datetime

class CategoryWidget(QWidget):

    def __init__(self, model, categories=[], colors=[]):
        super().__init__()
        
        self.model = model
        self.categories = categories
        self.colors = colors
        self.buttons = []
        self.globalLayout = QVBoxLayout()
        self.setLayout(self.globalLayout)  
        self.updateLayouts()      

    def addCategoryWindow(self):
        self.w = AddCategoryWindow()
        self.w.show()
        self.w.categoryInfo.connect(self.addCategoryButton)
    
    def addCategoryButton(self, info):
        #close window
        self.w.close()
        self.w = None
        #make button
        button = RoundedButton(info[0], info[1])
        button.clicked.connect(button.emit)
        button.infoSignal.connect(self.model.addTask)
        button.installEventFilter(self)

        # append info to relevant trackers
        self.categories.append(info[0])
        self.colors.append(info[1])
        self.buttons.append(button)

        #update layout
        if len(self.layouts) == 0 or self.layouts[-1].count() >= 3:
            layout = QHBoxLayout()
            layout.addWidget(button)
            self.globalLayout.addLayout(layout)
            self.layouts.append(layout)
        self.layouts[-1].addWidget(button)

        #update view
        self.update()       

    def removeCategoryButton(self, button):
        if button in self.buttons:
            idx = self.buttons.index(button)
            self.model.removeCategory(self.categories[idx])
            self.buttons[idx].deleteLater()
            del self.buttons[idx]
            del self.categories[idx]
            del self.colors[idx]
            self.model.layoutChanged.emit()
            self.updateLayouts()

    def updateLayouts(self):
        self.clearLayout()
        self.layouts = []
        layout = None
        for i in range(len(self.categories)):
            if i % 3 == 0:
                if layout is not None:
                    self.layouts.append(layout)
                layout = QHBoxLayout()

            if i <= len(self.buttons):
                self.buttons.append(RoundedButton(self.categories[i], self.colors[i]))
                self.buttons[i].clicked.connect(self.buttons[i].emit)
                self.buttons[i].infoSignal.connect(self.model.addTask)
                self.buttons[i].installEventFilter(self)
            
            layout.addWidget(self.buttons[i])

        if layout is not None:
            self.layouts.append(layout)    

        for layout in self.layouts:
            self.globalLayout.addLayout(layout)

    def clearLayout(self):
        while self.globalLayout.count():
            child = self.globalLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            else:
                while child.count():
                    grandchild = child.takeAt(0)
                    if grandchild.widget():
                        child.removeWidget(grandchild.widget())
     
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.ContextMenu and source in self.buttons:
            menu = QMenu()

            removeAction = QAction("Remove category", self)
            removeAction.setStatusTip("Remove this button and the corresponding category")
            removeAction.triggered.connect(lambda: self.removeCategoryButton(source))
            menu.addAction(removeAction)

            menu.exec(event.globalPos())

        return super().eventFilter(source, event)
class AddCategoryWindow(QWidget):

    categoryInfo = QtCore.pyqtSignal(object)

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
        self.dialog = QColorDialog()
        self.color = 'black'
        self.colorSelector = QPushButton("Select Color")
        self.colorSelector.clicked.connect(self.showColorDialog)

        #done button
        self.doneButton = QPushButton("Done")
        self.doneButton.clicked.connect(self.returnInfo)

        layout.addWidget(self.textField)
        layout.addWidget(self.colorSelector)
        layout.addWidget(self.doneButton)
        self.setLayout(layout)

    def showColorDialog(self):
        color = self.dialog.getColor()
        self.color = color.name()

    def text_input(self):
        self.name = self.textField.text()

    def returnInfo(self):
        self.categoryInfo.emit((self.name, self.color))
class RoundedButton(QPushButton):

    infoSignal = QtCore.pyqtSignal(object)

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

    def emit(self):
        self.infoSignal.emit((self.label, self.color))
class TaskListWidget(QWidget):

    def __init__(self, model):
        super().__init__()

        self.taskList = QTableView()

        #due date sorting
        self.taskList.setSortingEnabled(True)
        self.taskList.setModel(model)

        #aesthetic
        self.taskList.setMinimumSize(100, 50)
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
        if self.tasks:
            return len(self.tasks[0])-1
        return 4

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

    def save(self):
        self.tasks = [t for t in self.tasks if not t[0]]    
        self.layoutChanged.emit()

    def removeCategory(self, category):
        i = 0
        while i < len(self.tasks):
            if self.tasks[i][2] == category:
                del self.tasks[i]
            else:
                i += 1

    def addTask(self, info):
        self.tasks.append([False, datetime.today(), info[0], "Task Description", info[1]])
        self.layoutChanged.emit()

    def sort(self, col, order):
        if col == 1:
            if order == Qt.SortOrder.AscendingOrder:
                self.tasks.sort(key = lambda x: x[1])
            elif order == Qt.SortOrder.DescendingOrder:
                self.tasks.sort(key = lambda x: x[1], reverse = True)
            self.layoutChanged.emit()
        

