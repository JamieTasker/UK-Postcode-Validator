import os, sys, sqlite3, csv
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QDialog
from PyQt5 import QtCore
import files.postcode_logic as postcode_logic
import threading

# Enable support for HiDPI displays in a Windows based OS.
QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

class Application(QMainWindow):

    def __init__(self):
        super().__init__()

        self.parameters = Settings_params()

        try:
            if len([i for i in os.listdir(sys.path[0] + "/files/db/") if i.endswith(".db")]) > 1 \
                    and self.parameters.defaultdb == "False":
                db_window = Db_selector()
                self.db = db_window.db

                if db_window.defaultdb is not None:
                    self.parameters.defaultdb = db_window.defaultdb
                    self.parameters.write_params()

                del db_window

            elif self.parameters.defaultdb != "False":
                # Load the default DB.
                self.db = sys.path[0] + "/files/db/" + self.parameters.defaultdb
            else:
                db_file = [i for i in os.listdir(sys.path[0] + "/files/db/") if i.endswith(".db")][0]
                self.db = sys.path[0] + "/files/db/" + db_file
        except (IndexError, FileNotFoundError):
            QMessageBox.critical(self, "No Postcode Database", 'No Postcode database detected. Please run the Postcode'
                                                               ' database creator to create a new database file.')
            sys.exit()

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

        self.currentdbCombo.addItems([i for i in os.listdir(sys.path[0] + "/files/db/") if i.endswith(".db")])
        combo_index = self.currentdbCombo.findText(os.path.split(self.db)[1])
        self.currentdbCombo.setCurrentIndex(combo_index)
        self.currentdbCombo.currentIndexChanged.connect(self.db_switch)

        # Menu Bar
        self.actionExit.triggered.connect(self.close)
        self.actionSettings.triggered.connect(self.show_settings)
        self.actionAbout.triggered.connect(self.show_about)

    def db_reader(self):

        postcode_db = sqlite3.connect(self.db)
        postcode_cursor = postcode_db.cursor()
        self.valid_postcodes = {i[0]: [i[1], i[2]] for i in postcode_cursor.execute("SELECT * FROM Postcodes")}

    def db_switch(self):

        self.db = sys.path[0] + "/files/db/" + str(self.currentdbCombo.currentText())
        del self.valid_postcodes
        self.db_reader()

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

        if self.csv_location == self.csv_out_location and self.csv_location != "":
            QMessageBox.critical(self, "Duplicate files",
                                 'Error: Input and output files cannot share the same file path.')
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
        settings_window_object = Settings_window(self.parameters)

        del settings_window_object
        self.mainwindow.setEnabled(True)

    def show_about(self):

        self.mainwindow.setEnabled(False)
        about_window_object = About_window()
        del about_window_object
        self.mainwindow.setEnabled(True)

    def postcode_validation(self):

        self.csv_write_object = Csv_manipulation(self.csv_out_location, "w")
        postcode_heading_index = self.headingCombo.currentIndex()
        self.csv_yielder = self.csv_read_object.row_yielder()

        new_headings = ['Postcode Database Match', "Validation Attempt", "Nearest Match", "Nearest Match %",
                        "Easting", "Northing"]
        if self.parameters.autocorrect == "False":
            new_headings.remove("Validation Attempt")
        if self.parameters.fuzzy == "False":
            new_headings.remove("Nearest Match")
            new_headings.remove("Nearest Match %")
        if self.parameters.eastingnorthing == "False":
            new_headings.remove("Easting")
            new_headings.remove("Northing")

        if self.firstHeadingCheck.isChecked():
            self.csv_write_object.write_list(self.headings + new_headings)
            self.csv_read_object.skip_row()

        for row in self.csv_yielder:
        # MESSY CODE - CLEAN UP!!
            existing_row = row
            current_postcode_orig = row[postcode_heading_index]
            current_postcode = row[postcode_heading_index]

            valid_status = False
            if self.parameters.eastingnorthing == "True":
                easting, northing = (0, 0)

            if current_postcode in list(self.valid_postcodes.keys()):
                valid_status = True
                easting, northing = self.valid_postcodes[current_postcode]

            if valid_status is False and self.parameters.autocorrect == "True":
                validate_object = postcode_logic.Postcode(current_postcode)
                try:
                    current_postcode = validate_object.validate_postcode()
                    validated_postcode = current_postcode
                    if current_postcode in list(self.valid_postcodes.keys()):
                        if self.parameters.eastingnorthing == "True":
                            easting, northing = self.valid_postcodes[current_postcode]
                        valid_status = True
                except IndexError:
                    validated_postcode = "Impossible"
                del validate_object
            elif valid_status is True and self.parameters.autocorrect == "True":
                validated_postcode = "Not Needed"

            if valid_status is False and self.parameters.fuzzy == "True":
                fuzzy_object = postcode_logic.Postcode(current_postcode)
                current_postcode, fuzzy_percentage = fuzzy_object.fuzzy_logic(list(self.valid_postcodes.keys()),
                                                                              self.parameters.fuzzytolerance)
                fuzzy_postcode = current_postcode
                if current_postcode != "No Match" and current_postcode in list(self.valid_postcodes.keys()):
                    if self.parameters.eastingnorthing == "True":
                        easting, northing = self.valid_postcodes[current_postcode]
                    valid_status = True
                del fuzzy_object
            elif valid_status is True and self.parameters.autocorrect == "True":
                fuzzy_postcode = "Not Needed"
                fuzzy_percentage = 0

            new_data = [str(valid_status)]
            if self.parameters.autocorrect == "True":
                new_data.append(validated_postcode)
            if self.parameters.fuzzy == "True":
                new_data.append(fuzzy_postcode)
                new_data.append(str(fuzzy_percentage))
            if self.parameters.eastingnorthing == "True":
                new_data.append(str(easting))
                new_data.append(str(northing))

            to_write = existing_row + new_data
            self.csv_write_object.write_list(to_write)

        self.csv_write_object.close_csv()
        self.csv_read_object.go_to_start()
        QMessageBox.information(self, 'Process Complete!', "Process complete. Postcodes were successfully validated.")

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

class Settings_params(object):

    def __init__(self):

        try:
            self.settings_file = open(sys.path[0] + "/files/config.cfg", "r")
        except FileNotFoundError:
            self.settings_file = open(sys.path[0] + "/files/config.cfg", "w")
            self.settings_file.writelines(
                "autocorrect=True\n"
                "fuzzy=False\n"
                "fuzzytolerance=75\n"
                "eastingnorthing=True\n"
                "defaultdb=False")
            self.settings_file.close()
            self.settings_file = open(sys.path[0] + "/files/config.cfg", "r")

        self.autocorrect = self.settings_file.readline().split("=")[1].replace("\n", "")
        self.fuzzy = self.settings_file.readline().split("=")[1].replace("\n", "")
        self.fuzzytolerance = int(self.settings_file.readline().split("=")[1].replace("\n", ""))
        self.eastingnorthing = self.settings_file.readline().split("=")[1].replace("\n", "")
        self.defaultdb = self.settings_file.readline().split("=")[1].replace("\n", "")

    def write_params(self):

        self.settings_file.close()
        self.settings_file = open(sys.path[0] + "/files/config.cfg", "w")

        self.settings_file.write("autocorrect=" + self.autocorrect + "\n")
        self.settings_file.write("fuzzy=" + self.fuzzy + "\n")
        self.settings_file.write("fuzzytolerance=" + str(self.fuzzytolerance) + "\n")
        self.settings_file.write("eastingnorthing=" + self.eastingnorthing + "\n")
        self.settings_file.write("defaultdb=" + self.defaultdb + "\n")

        self.settings_file.close()

class Settings_window(QDialog):

    def __init__(self, settings_object):

        super().__init__()

        self.settings_object = settings_object

        self.settings_window = loadUi(sys.path[0] + "/files/ui/settings.ui", self)
        self.initui()
        self.settings_window.show()
        self.exec_()

    def initui(self):

        self.cancelButton.clicked.connect(self.close)
        self.saveButton.clicked.connect(self.re_write_settings)
        self.fuzzyCheck.clicked.connect(self.fuzzy_toggle)
        self.fuzzySlider.valueChanged.connect(lambda: self.fuzzySpin.setValue(self.fuzzySlider.value()))
        self.fuzzySpin.valueChanged.connect(lambda: self.fuzzySlider.setValue(self.fuzzySpin.value()))
        self.defaultCheck.stateChanged.connect(self.default_toggle)

        self.defaultCombo.addItems([i for i in os.listdir(sys.path[0] + "/files/db/") if i.endswith("db")])
        if self.settings_object.defaultdb != "False":
            self.defaultCheck.setChecked(True)
            combo_index = self.defaultCombo.findText(self.settings_object.defaultdb)
            self.defaultCombo.setCurrentIndex(combo_index)
        else:
            self.defaultCombo.setEnabled(False)

        if self.settings_object.autocorrect == "True":
            self.correctinvalidCheck.setChecked(True)

        if self.settings_object.fuzzy == "True":
            self.fuzzyCheck.setChecked(True)
            self.fuzzy_toggle()

        self.fuzzySlider.setValue(self.settings_object.fuzzytolerance)
        self.fuzzySpin.setValue(self.settings_object.fuzzytolerance)

        if self.settings_object.eastingnorthing == "True":
            self.appendcoordsCheck.setChecked(True)

    def fuzzy_toggle(self):

        if self.fuzzyCheck.isChecked():
            self.fuzzytoleranceLabel.setEnabled(True)
            self.fuzzySlider.setEnabled(True)
            self.fuzzySpin.setEnabled(True)
        else:
            self.fuzzytoleranceLabel.setEnabled(False)
            self.fuzzySlider.setEnabled(False)
            self.fuzzySpin.setEnabled(False)

    def default_toggle(self):

        if self.defaultCheck.isChecked():
            self.defaultCombo.setEnabled(True)
        else:
            self.defaultCombo.setEnabled(False)

    def re_write_settings(self):

        if self.correctinvalidCheck.isChecked():
            self.settings_object.autocorrect = "True"
        else:
            self.settings_object.autocorrect = "False"

        if self.fuzzyCheck.isChecked():
            self.settings_object.fuzzy = "True"
        else:
            self.settings_object.fuzzy = "False"

        self.settings_object.fuzzytolerance = self.fuzzySpin.value()

        if self.appendcoordsCheck.isChecked():
            self.settings_object.eastingnorthing = "True"
        else:
            self.settings_object.eastingnorthing = "False"

        if self.defaultCheck.isChecked():
            self.settings_object.defaultdb = str(self.defaultCombo.currentText())
        else:
            self.settings_object.defaultdb = "False"

        self.settings_object.write_params()
        self.close()

class About_window(QDialog):

    def __init__(self):

        super().__init__()

        self.about_window = loadUi(sys.path[0] + "/files/ui/about.ui", self)
        self.initui()
        self.about_window.show()
        self.exec_()

    def initui(self):

        self.doneButton.clicked.connect(self.close)

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

        if self.defaultCheck.isChecked():
            self.defaultdb = str(self.dbCombo.currentText())
        else:
            self.defaultdb = None

        self.close()

# Main
app = QApplication(sys.argv)
ex = Application()
sys.exit(app.exec_())