from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from widgets import *
import json
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task Tracker")
        self.setFixedSize(QSize(500, 400))

        self.load()
        self.model.layoutChanged.connect(self.save)

        layout = QVBoxLayout()
        layout.addWidget(TaskListWidget(self.model))
        hlayout = QHBoxLayout()
        self.catwidget = CategoryWidget(self.model, self.categories, self.colors)
        refresh = RoundedButton("Save", "green")
        refresh.clicked.connect(self.model.save)
        hlayout.addWidget(refresh)
        addCategory = RoundedButton("Add Category", 'gray')
        addCategory.clicked.connect(self.catwidget.addCategoryWindow)
        addCategory.clicked.connect(self.model.save)
        hlayout.addWidget(addCategory)
        layout.addLayout(hlayout)
        layout.addWidget(self.catwidget)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def load(self):
        try:
            with open ('data.json') as f:
                data = json.load(f)
                self.categories = data['categories']
                self.colors = data['colors']
                tasks = data['tasks']
                for t in tasks:
                    t[1] = datetime.strptime(t[1][:10], "%Y-%m-%d")
                self.model = TaskModel(tasks=tasks, cols=['', 'Due Date', 'Category', 'Description', 'Color'])
        except:
            self.model = TaskModel(tasks=[], cols=['', 'Due Date', 'Category', 'Description', 'Color'])
            self.categories = []
            self.colors = []

    def save(self):
        with open('data.json', 'w') as f:
            jsondata = {'tasks': self.model.tasks, 'categories': self.catwidget.categories, 'colors': self.catwidget.colors}
            json.dump(jsondata, f, default=str)

app = QApplication([])

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec()
