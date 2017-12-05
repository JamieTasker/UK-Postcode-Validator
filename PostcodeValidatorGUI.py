import os, sys, sqlite3, csv
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QDialog
from PyQt5 import QtCore
import files.postcode_logic as postcode_logic
import threading

# Enable support for HiDPI displays in a Windows based OS.
QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

class Application(QMainWindow):

    def __init__(self, db):
        super().__init__()

        self.db = db
        self.db_reader()
        self.csv_location = ""
        self.csv_out_location = ""

        self.mainwindow = loadUi(sys.path[0] + "/files/ui/mainwindow.ui", self)
        self.initui()
        self.mainwindow.show()

    def initui(self):

        # Buttons
        self.cancelButton.clicked.connect(self.close)
        self.browseButton.clicked.connect(self.input_file_dialog)
        self.browseOutButton.clicked.connect(self.output_file_dialog)
        self.okButton.clicked.connect(self.postcode_validation)

        # Menu Bar
        self.actionExit.triggered.connect(self.close)
        self.actionSettings.triggered.connect(self.show_settings)

    def db_reader(self):

        if self.db == None:
            QMessageBox.critical(self, "No Postcode Database", "No Postcode database detected. Please run the Postcode"
                                                               " database creator to create a new database file.")
            sys.exit()

        postcode_db = sqlite3.connect(self.db)
        postcode_cursor = postcode_db.cursor()
        self.valid_postcodes = {i[0]: [i[1], i[2]] for i in postcode_cursor.execute("SELECT * FROM Postcodes")}

    def input_file_dialog(self):

        self.csv_location = QFileDialog.getOpenFileName(self, "Select a CSV File", '', "CSV Files (*.CSV)")[0]
        if self.csv_location != "":
           self.inputText.setText(self.csv_location)

           self.csv_read_object = Csv_manipulation(self.csv_location, "r")
           self.headings = self.csv_read_object.get_headings()
           self.headingCombo.clear()
           self.headingCombo.addItems(self.headings)
        else:
            self.inputText.setText("Please select an input file...")

        self.valid_file_check()

    def output_file_dialog(self):

        self.csv_out_location = QFileDialog.getSaveFileName(self, "Select a save location", '', "CSV Files (*.CSV)")[0]
        if self.csv_out_location != "":
            self.outputText.setText(self.csv_out_location)
        else:
            self.outputText.setText("Please select an output location...")

        self.valid_file_check()

    def valid_file_check(self):

        if self.csv_location == self.csv_out_location:
            QMessageBox.critical(self, "Duplicate files", "Error: Input and output files cannot share the same file path.")
            self.csv_out_location = ""
            self.outputText.setText("Please select an output location...")

        if self.csv_location != "":
           self.firstHeadingCheck.setEnabled(True)
           self.headingCombo.setEnabled(True)
           self.outputText.setEnabled(True)
           self.browseOutButton.setEnabled(True)
        else:
           self.firstHeadingCheck.setEnabled(False)
           self.headingCombo.setEnabled(False)
           self.outputText.setEnabled(False)
           self.browseOutButton.setEnabled(False)

        if self.csv_location != "" and self.csv_out_location != "":
            self.okButton.setEnabled(True)
        else:
            self.okButton.setEnabled(False)

    def show_settings(self):

        self.mainwindow.setEnabled(False)
        settings_window_object = Settings_window()
        self.mainwindow.setEnabled(True)

    def postcode_validation(self):

        self.csv_write_object = Csv_manipulation(self.csv_out_location, "w")
        postcode_heading_index = self.headingCombo.currentIndex()
        self.csv_yielder = self.csv_read_object.row_yielder()
        new_headings = ["Postcode Database Match", "Validation Attempt", "Easting", "Northing"]

        if self.firstHeadingCheck.isChecked():
            self.csv_write_object.write_list(self.headings + new_headings)
            self.csv_read_object.skip_row()

        for row in self.csv_yielder:

            existing_row = row
            current_postcode = row[postcode_heading_index]

            if current_postcode not in list(self.valid_postcodes.keys()):
                validate_object = postcode_logic.Postcode(current_postcode)
                try:
                    current_postcode_validated = validate_object.validate_postcode()
                except IndexError:
                    current_postcode_validated = "Impossible"
                if current_postcode_validated in list(self.valid_postcodes.keys()):
                    easting, northing = self.valid_postcodes[current_postcode_validated]
                    valid_status = True
                else:
                    easting, northing = (None, None)
                    valid_status = False
            else:
                easting, northing = self.valid_postcodes[current_postcode]
                valid_status = True
                current_postcode_validated = "Not Needed"

            new_data = [str(valid_status), str(current_postcode_validated), str(easting), str(northing)]
            to_write = existing_row + new_data

            self.csv_write_object.write_list(to_write)
        
        self.csv_write_object.close_csv()
        self.csv_read_object.go_to_start()
        QMessageBox.information(self, "Process Complete!", "Process complete. Postcodes were successfully validated.")

class Csv_manipulation(object):

    def __init__(self, csv_file, mode):
        self.csv_file = open(csv_file, mode)
        if mode == "r":
            self.csv_reader = csv.reader(self.csv_file, delimiter=",", lineterminator="\n")
        elif mode == "w":
            self.csv_writer = csv.writer(self.csv_file, delimiter = ",", lineterminator = "\n")

    def get_headings(self):

        headings = next(self.csv_reader)
        self.go_to_start()

        return headings

    def row_yielder(self):

        for row in self.csv_reader:
            yield row

    def skip_row(self):

        next(self.csv_reader)

    def go_to_start(self):
    	
        self.csv_file.seek(0)

    def write_list(self, list_data):

        self.csv_writer.writerow(list_data)

    def close_csv(self):

        self.csv_file.close()

class Settings_window(QDialog):

    def __init__(self):

        super().__init__()

        self.settings_window = loadUi(sys.path[0] + "/files/ui/settings.ui", self)
        self.initui()
        self.settings_window.show()
        self.exec_()

    def initui(self):

        self.cancelButton.clicked.connect(self.close)
        self.saveButton.clicked.connect(self.close)

        self.defaultCombo.addItems([i for i in os.listdir(sys.path[0] + "/files/db/") if i.endswith("db")])

class Db_selector(QDialog):

    def __init__(self):

        super().__init__()
        self.dbselect = loadUi(sys.path[0] + "/files/ui/dbselect.ui", self)
        self.initui()
        self.dbselect.show()
        self.exec_()

    def initui(self):

        self.dbCombo.addItems([i for i in os.listdir(sys.path[0] + "/files/db/") if i.endswith(".db")])
        self.cancelButton.clicked.connect(sys.exit)
        self.okButton.clicked.connect(self.confirm_selection)

    def confirm_selection(self):

        self.db = sys.path[0] + "/files/db/" + str(self.dbCombo.currentText())
        self.close()

# Main
app = QApplication(sys.argv)
try:
    if len([i for i in os.listdir(sys.path[0] + "/files/db/") if i.endswith(".db")]) > 1:
        db_window = Db_selector()
        db = db_window.db
        del db_window
    else:
        db_file = [i for i in os.listdir(sys.path[0] + "/files/db/") if i.endswith(".db")][0]
        db = sys.path[0] + "/files/db/" + db_file
except (IndexError, FileNotFoundError):
    db = None


ex = Application(db)
sys.exit(app.exec_())