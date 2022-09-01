from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QPalette, QColor
from widgets import *
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task Tracker")
        self.setFixedSize(QSize(500, 400))

        #TODO: load all tasks from database
        tasks = [[False, datetime(2019, 5, 4), 'class 1', 'task 1', 'red'],
                 [False, datetime(2022, 5, 4), 'class 2', 'task 2', 'blue']]
        self.model = TaskModel(tasks=tasks, cols=['', 'Due Date', 'Category', 'Description', 'Color'])

        layout = QVBoxLayout()
        layout.addWidget(TaskListWidget(self.model))
        hlayout = QHBoxLayout()
        catwidget = CategoryWidget()
        refresh = RoundedButton("Refresh", "red")
        refresh.clicked.connect(self.model.refresh)
        hlayout.addWidget(refresh)
        addCategory = RoundedButton("Add Category", 'gray')
        addCategory.clicked.connect(catwidget.addCategoryWindow)
        hlayout.addWidget(addCategory)
        layout.addLayout(hlayout)
        layout.addWidget(catwidget)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

app = QApplication([])

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec()
