from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, \
                             QComboBox, QGridLayout, QPushButton, \
                             QMainWindow, QTableWidget, QTableWidgetItem, \
                             QDialog, QVBoxLayout, QComboBox, QToolBar,
                             QStatusBar, QMessageBox)

from PyQt6.QtCore import Qt

from PyQt6.QtGui import QAction, QIcon
# QAction allows you to add menu items
# QIcon allows you to add icons to menu items

import sys
import sqlite3

from secretary import details

# QmainWindow is like a more powerfulQWidget where you can put multiple
# widgets in a window

class DatabaseConnection:
    """ because each class contains a separate database connection
    this class has been created in order to handle the connection to
    the database, all classes will refer to this class for the
    database link so that far less lines of code are implemented and
    thus eliminating a duplicate code smell which is essentially
    a coding
    practice of simplifying and increasing efficiency of code
    other code smells include really long methods that need to be
    split into smaller methods, unclear naming conventions,
    inefficient algorithms"""

    def __init__(self, database_file="sqlitedb.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Manager")
        self.setMinimumSize(800, 600)
        # above sets minimum size of window

        # menu items
        file_menu_item = self.menuBar().addMenu("&File")
        # menu bar items are added as above, an "&" is needed
        # before menu item name
        help_menu_item = self.menuBar().addMenu("&Help")

        edit_menu_item = self.menuBar().addMenu("&Edit")
        ##
        # sub menu items

        add_student_action = QAction(QIcon(details()[0]),
                                     "Add Student", self)
        # above is example of a menu item
        add_student_action.triggered.connect(self.insert)
        # above triggers the insert method for the "Add student"
        # QAction above
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        # self will connect the QAction to the MainWindow
        help_menu_item.addAction(about_action)
        # help_menu_item automatically gets a search bar in the menu
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        # without the above line the help menu button won't show
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon(details()[1]),
                                "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)
        # the above triggered line connects the search button
        # in the menu to the search student widget ## important!!
        ##

        self.table = QTableWidget()
        # creates a table widget
        self.table.setColumnCount(4)
        # sets the number of columns in the table
        self.table.setHorizontalHeaderLabels(("Id", "Name",
                                              "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        # above line makes the table header invisible eliminates the
        # default row numbers
        self.setCentralWidget(self.table)
        # sets the CentralWidget in the window as a table widget

        # Toolbar and Toolbar elements

        toolbar = QToolBar()
        # creates a toolbar instance
        toolbar.setMovable(True)
        # makes the toolbar movable
        self.addToolBar(toolbar)
        # adds the toolbar to the window
        toolbar.addAction(add_student_action)
        # add the add_student menu item to the toolbar
        toolbar.addAction(search_action)

        # Status bar and status bar elements

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.table.cellClicked.connect(self.cell_clicked)
        # above can detect when a cell in the table is selected

        hello = QLabel("Options: ")
        self.statusbar.addWidget(hello)
        # above adds a label to the status bar

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)
        # the above lines remove buttons from the status bar
        # that would otherwise be added multiple times everytime
        # a cell is clicked

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        # above is how you can connect to an sql database using the
        # DatabaseConnection class
        cursor = connection.cursor()
        # different to sqlite, mysql requires a cursor object even
        # when youre just reading data
        cursor.execute("SELECT * FROM students")
        # above executes the query "select all from students"
        # above is also different to sqlite using cursor.execute instead
        # of connection.execute
        result = cursor.fetchall()
        # different to sqlite, above fetches all the data from the cursor
        # print(list(result))
        # above will print as a cursor object without the list function
        self.table.setRowCount(0)
        # above line clears the table before reloading it
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                print(row_data)
                self.table.setItem(row_number, column_number,
                                   QTableWidgetItem(str(data)))
        connection.close()

        # above for loop populates the table from left to right
        # and top to bottom

    def insert(self):
        dialog = InsertDialog()
        # dialog is inserted as a pop up window on the screen
        dialog.exec()

    def search(self):
        dialog = SearchStudent()
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
        self.setWindowTitle("About")
        content = """hey wheres the gabagooool!"""

        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        # Get student name from selected row
        index = main_window.table.currentRow()
        # extracts the index of the current row
        student_name = main_window.table.item(index, 1).text()
        # index of the current row and index of the column specified
        # in brackets above, column 1 is the name column. text() extracts
        # the text from the name column

        # Get Id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        # Student name input
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)
        # self will take the student name input and add to database
        # combo box
        course_name = main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        # the above lines set the course name to be the same as in the
        # database for the selected row
        layout.addWidget(self.course_name)

        # mobile input
        mobile = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)
        # the above lines set the mobile number to be the same as in the
        # database for the selected row

        # submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, "
                       "mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(
                            self.course_name.currentIndex()),
                        # above is how to extract data from a combo box
                        self.mobile.text(),
                        self.student_id))
        # above lines update the database with the new data, the above
        # query will find the row where the id is equal to a particular
        # value provided in the () tuple, the values will be entered
        # by the user in the input box
        connection.commit()
        # update and insert are write operations to the database and need
        # a .commit() to be written to the database
        cursor.close()
        connection.close()
        main_window.load_data()
        # above line refreshes the table
"""
    # add student to database
    def add_student(self):
        name = self.student_name.text()
        # takes the text from the student_name input
        course = self.course_name.itemText(self.course_name.currentIndex())
        # itemText() takes the text from the combo box
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students(name, course, mobile) "
                       "VALUES(?, ?, ?)",
                       (name, course, mobile))

        connection.commit()
        # .commit() method is called to apply the sql query to the
        # database
        cursor.close()
        connection.close()
        main_window.load_data()
        # above line refreshes data upon data entry
"""

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # get selected row index and student id from table
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?",
                       (student_id,))
        # the above is not a tuple if ot doesn't have a comma

        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        # QMessageBox is simpler version of a QDialogBox
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


# below class is the data entry widget
class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        # Student name input
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)
        # self will take the student name input and add to database
        # combo box
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)
        self.setLayout(layout)
        # mobile input
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)
        # submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

    # add student to database
    def add_student(self):
        name = self.student_name.text()
        # takes the text from the student_name input
        course = self.course_name.itemText(self.course_name.currentIndex())
        # itemText() takes the text from the combo box
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students(name, course, mobile) "
                       "VALUES(?, ?, ?)",
                       (name, course, mobile))

        connection.commit()
        # .commit() method is called to apply the sql query to the
        # database
        cursor.close()
        connection.close()
        main_window.load_data()
        # above line refreshes data upon data entry


class SearchStudent(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.search_student = QLineEdit()
        self.search_student.setPlaceholderText("Name")
        layout.addWidget(self.search_student)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.search_student.text()
        # takes the text from the search_student input
        connection = DatabaseConnection().connect()
        # connect to student database
        cursor = connection.cursor()
        # create a cursor object
        result = cursor.execute("SELECT * FROM students WHERE name=?",
                                (name,))
        # sql query = select all from students db where
        # search_student name input = name column
        rows = list(result)
        # convert rows to list of tuples
        print(rows)
        items = (main_window.table.findItems(
            name, Qt.MatchFlag.MatchFixedString))
        # above accesses table of main window and allows you to enter a name
        # MatchFlag.MatchFixedString will match the name to a string in the
        # table
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)
            # above will select the name in the main_window table again, item.row()
            # gives the index of the current row, 1 is the index of the column.
            # setSelected() will select the name in the table
            cursor.close()
            connection.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
# will not load any data from the database without this line
sys.exit(app.exec())
