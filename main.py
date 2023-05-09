import sys
import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox, QToolBar, QStatusBar, \
    QMessageBox
from PyQt6.QtGui import QAction, QIcon
import mysql.connector


class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password="pythoncourse", database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user, password=self.password,
                                             database=self.database)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Adding toolbar

        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Adding StatusBar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click

        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Every cell click would create edit and delete buttons in the status bar.
        # To avoid that we find children and if they exist, we remove buttons widgets and create new

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")

        self.table.setRowCount(0)

        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Very important info")
        message = """
I made this app while learning PyQt6.
Feel free to do whatever you want with this.
Very important info, isn't it? =)
"""
        self.setText(message)


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setFixedWidth(200)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # add name widget
        self.name = QLineEdit()
        self.name.setPlaceholderText("Name")
        layout.addWidget(self.name)

        # Add course combo box
        self.course_name = QComboBox()
        courses = ["Astronomy", "Biology", "Math", "Physics", ]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add submit button
        submit = QPushButton("Submit")
        submit.clicked.connect(self.add_student)
        layout.addWidget(submit)

        # Add cancel button
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.closing)
        layout.addWidget(cancel)

        self.setLayout(layout)

    def add_student(self):
        name = self.name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        if name != "" and mobile != "":
            connection = DatabaseConnection().connect()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                           (name, course, mobile))
            connection.commit()
            cursor.close()
            connection.close()
            project.load_data()
            self.closing()  # close after submit

    # close Dialog window
    def closing(self):
        self.accept()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search Student")
        self.setFixedHeight(100)
        self.setFixedWidth(250)

        # layout = QVBoxLayout()
        grid = QGridLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        # layout.addWidget(self.student_name)
        grid.addWidget(self.student_name, 0, 0, 1, 2)

        search_button = QPushButton("Search")
        # layout.addWidget(search_button)
        search_button.clicked.connect(self.search)
        grid.addWidget(search_button, 1, 0)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        grid.addWidget(close_button, 1, 1)
        # layout.addWidget(close_button)

        self.setLayout(grid)
        # self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        # Search in DB to print in the screen

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)
        print(rows)

        # Search in the GUI table
        items = project.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            project.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Management System")
        self.setFixedWidth(200)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from selected row
        index = project.table.currentRow()
        print(index)

        # add name widget
        student_name = project.table.item(index, 1).text()  # (row_index, column)
        self.name = QLineEdit(student_name)
        self.name.setPlaceholderText("Name")
        layout.addWidget(self.name)

        # get id from selected row
        self.student_id = project.table.item(index, 0).text()

        # Add course combo box
        course = project.table.item(index, 2).text()  # extracting course name from selected row
        self.course_name = QComboBox()
        courses = ["Astronomy", "Biology", "Math", "Physics", ]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course)  # Select current course

        layout.addWidget(self.course_name)

        # Add mobile widget
        mobile = project.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add update button
        submit = QPushButton("Update")
        submit.clicked.connect(self.update_student)
        layout.addWidget(submit)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))

        # don't forget to commit :D
        connection.commit()
        cursor.close()
        connection.close()

        # to refresh the table data, calling load_data()
        project.load_data()
        self.accept()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Management System")

        layout = QGridLayout()
        confirmation_message = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation_message, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.accept)

    def delete_student(self):
        # get selected row's index and student id
        index = project.table.currentRow()
        student_id = project.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()

        # Making sure to add a comma in the tuple, because if there is no a single comma, it won't be read as tuple
        cursor.execute("DELETE from students WHERE id = ?", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()

        # Refreshing table
        project.load_data()

        self.close()

        confirmation_message = QMessageBox()
        confirmation_message.setWindowTitle("Success")
        confirmation_message.setText("The record was deleted successfully")
        confirmation_message.exec()


app = QApplication(sys.argv)
project = MainWindow()
project.load_data()
project.show()
sys.exit(app.exec())
