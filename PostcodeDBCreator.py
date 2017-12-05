# PostcodeDBCreator v x.x
# Create a SQLite3 database that can be read by the UK Postcode Validator tool.
# Created by Jamie Tasker on DATE

import sys, os, sqlite3

def database_creator(postcode_data):
    """Create the SQLite3 postcode database, populate it with data and get the user to name the output file."""
    # First of all, we need to get the user to specify the name of the database.

    # Generate a tuple of banned characters that cannot be in the filename.
    banned = ("/", "\\", "!", '"', " ")
    db_name = input("Please enter a name for this Postcode database: ")
    # If the name the user enters contains a banned character or is blank, a while loop is called that cannot be
    # broken until the user enters a valid file name.
    if [i for i in list(db_name) if i in banned] or db_name == "":
        valid = False
        while not valid:
            print("Illegal character detected. Please enter a valid file name containing only letters and numbers.")
            db_name = input("Please enter a name for this Postcode database: ")
            if [i for i in list(db_name) if i in banned] or db_name == "":
                valid = False
            else:
                valid = True

    # Now we move onto creating the sqlite3 database.
    print("\nCreating database...")
    # Create the database in the /files/db/ directory.
    masterdb = sqlite3.connect(sys.path[0] + "/files/db/" + db_name + ".db")
    c = masterdb.cursor()
    # The Postcodes table is removed if it already exists.
    try:
        c.execute("DROP TABLE Postcodes")
    except:
        pass
    # We create the Postcodes table with three fields - Postcode, Easting and Northing.
    c.execute("CREATE TABLE Postcodes (Postcode varchar(8), Easting integer, Northing integer);")
    for i in postcode_data:
        # Insert the postcode data into the table.
        c.execute("INSERT INTO Postcodes VALUES ('" + i[0] + "', " + i[1] + ", " + i[2] + ");")

    # Save the changes.
    masterdb.commit()

def easting_northing_present_check():
    coords_present =  input("\nDoes your CSV file contain Easting and Northing data?(y/n): ")
    if coords_present.upper() != "Y" or coords_present.upper() != "N":
        while coords_present.upper() != "Y" and coords_present.upper() != "N":
            print("Error: Please enter y or n.")
            coords_present = input("\nDoes your CSV file contain Easting and Northing data?(y/n): ")
    if coords_present.upper() == "Y":
        return True
    else:
        return False

def heading_check():
    first_row_headings =  input("\nDoes your first row contain headings?(y/n): ")
    if first_row_headings.upper() != "Y" or first_row_headings.upper() != "N":
        while first_row_headings.upper() != "Y" and first_row_headings.upper() != "N":
            print("Error: Please enter y or n.")
            first_row_headings = input("\nDoes your first row contain headings?(y/n): ")
    if first_row_headings.upper() == "Y":
        return True
    else:
        return False

# Main
print("Welcome to the Postcode Database Creator.")
print("This tool will allow you to build a SQLite3 database for use in the UK Postcode Validator application.")

print("\nIn order to begin, please select what postcode data you are using.")
print("""Option 1: OS Codepoint Open
Option 2: Static data file containing postcode information (CSV, XLSX, TAB, SHP)""")

choice = input("\nPlease enter either option 1 or 2: ")
while choice != "1" and choice != "2":
    print("Error: Please enter either 1 or 2. ")
    choice = input("\nPlease enter either option 1 or 2: ")

if choice == "1":
    # CODEPOINT OPEN SECTION

    from files.codepointopenloader import codepoint_open_load

    print("\nYour Codepoint Open download should have come in directory containing over 100 individual CSV files.")
    csv_path = input("\nPlease enter the file path to the folder containing these CSV files: ")
    while not os.path.exists(csv_path):
        print("Error: File path not valid")
        csv_path = input("\nPlease enter the file path to the folder containing these CSV files: ")
    print("Folder valid. Gathering CodePoint Open Data...\n")
    postcode_data = codepoint_open_load(csv_path)

    database_creator(postcode_data)

elif choice == "2":
    print("""\nPlease select the file format your postcode data is stored in
1: Comma-separated Values (.CSV)
2: Microsoft Excel (.XLSX) using openpyxl
3: OGR supported Vector Format (.SHP, .TAB) using OSGeo Python Bindings""")
    choice = input("\nPlease enter an option: ")
    while choice != "1" and choice != "2" and choice != "3":
        print("Error: Please enter either 1, 2 or 3. ")
        choice = input("\nPlease enter an option: ")

    if choice == "1":

        # CSV SECTION
        from files.csvloader import csv_load, get_first_row, valid_csv_test

        csv_path = input("\nPlease enter the file path to your CSV file: ")
        if valid_csv_test(csv_path) == False:
            while not valid_csv_test(csv_path):
                print ("Error: The file you have specified is not valid. Please try again.")
                csv_path = input("\nPlease enter the file path to your CSV file: ")
        print("File valid.\n")

        coords_present = easting_northing_present_check()

        first_row, valid_length = get_first_row(csv_path)
        print ("\nHere is a preview of your CSV data: \n")
        print (first_row)

        postcode_col_no =  input("\nPlease enter the column number containing postcode data: ")
        if int(postcode_col_no) > valid_length or postcode_col_no == "0":
            while int(postcode_col_no) > valid_length or postcode_col_no == "0":
                print("Error: The column number specified does not exist")
                postcode_col_no = input("\nPlease enter the column number containing postcode data: ")
        postcode_col_no = int(postcode_col_no) - 1

        if coords_present == True:
            easting_col_no =  input("Please enter the column number containing easting data: ")
            if int(postcode_col_no) > valid_length or easting_col_no == "0":
                while int(postcode_col_no) > valid_length or easting_col_no == "0":
                    print("Error: The column number specified does not exist")
                    easting_col_no = input("Please enter the column number containing easting data: ")
            easting_col_no = int(easting_col_no) - 1

            northing_col_no =  input("Please enter the column number containing northing data: ")
            if int(postcode_col_no) > valid_length or northing_col_no == "0":
                while int(postcode_col_no) > valid_length or northing_col_no == "0":
                    print("Error: The column number specified does not exist")
                    northing_col_no = input("Please enter the column number containing northing data: ")
            northing_col_no = int(northing_col_no) - 1
        else:
            easting_col_no = None
            northing_col_no = None

        first_row_headings = heading_check()

        postcode_data = csv_load(csv_path, postcode_col_no, easting_col_no, northing_col_no, first_row_headings, coords_present)
        database_creator(postcode_data)

    else:
        input("Thanks for trying this, but it's not quite ready yet. Press enter to continue.")

print("\n\nProcess complete.")
