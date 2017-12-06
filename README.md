# UK Postcode Validator
Tool to read a CSV file containing UK postcodes and check whether or not they are valid.
Each postcode is checked against a database of valid postcodes that the user specifies. A separate tool is included that allows for easy creation of the database.
The tool also attempts to fix common postcode errors and appends eastings and northings to the data if the postcode is valid.
Check
This is a very very early release, so expect many bugs and lots of unusable features!

# What works?
- Create a postcode database using OS CodePoint Open data.
- Create a postcode database using a user specified CSV file.
- Support for multiple Postcode Databases (For example, you could validate postcodes against OS CodePoint Open or an address gazetteer).
- Read in and validate CSV files containing postcodes
- Attempt to fix common user input errors associated with postcodes
- Append Eastings and Northings to the output data.

# What does not work?
- Setting a default postcode database.
- Disabling functionality to automatically correct postcodes.
- Disabling functionality to automatically append eastings and northings.
- The entire settings window is broken.
- Creating a postcode database using an Excel Spreadsheet in XLSX format.
- Creating a postcode database using an OGR supported GIS vector format (e.g. ESRI SHP or MapInfo TAB).

# Bugs
There's a lot of them. Chances are I know about the majority, but feel free to file any reports.

# Planned Features
- Support for XLSX input/output files.
- Multi-threading.
- GUI enhancements (e.g. progress bar).
- Support arguments to allow for automated database creation and postcode validation.
- Create a postcode database using OS CodePoint data.

# Technical Info
The application is written in Python using PyQt5 as a GUI toolkit. It was developed on Kubuntu Linux and tested on Windows 10. I have not tried to run it on MacOS, but I see no reason why it should not work. 

In order to run from the Python source code, you must install the following libraries:
- PyQt5

It is also useful (but not crucial) that you install these libraries too:
- openpyxl
- osgeo GDAL Python bindings

# GPL
PyQt5 is property of Riverbank Computing Limited and is used under the GNU General Public Licence v3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
