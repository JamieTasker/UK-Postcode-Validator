# codepointopenloader v 1.0
# Returns a nested list containing postcodes, eastings and northings from Ordnance Survey CodePoint Open Data.
# Created by Jamie Tasker on 06/11/2017

import os
import csv

def codepoint_open_load(csv_path):
    """Extract the postcodes, eastings and northings from the OS CodePoint Open data."""
    # csv_path refers to the path containing the individual CSV data supplied by OS.

    # An empty list to hold the data.
    postcode_data = list()
    # Loop through each CSV file.
    for i in os.listdir(csv_path):
        current_csv_path = (csv_path + "/" + i)
        current_csv = open(current_csv_path, "r")
        # Try to open the file using the csv module. If this fails, we can assume that the file is not a valid CSV.
        try:
            current_reader = csv.reader(current_csv, delimiter=",", lineterminator="\n")
            for row in current_reader:
                # The postcode data is always in index position 0.
                postcode = row[0]

                if " " not in list(postcode):
                    # OS CodePoint Open does not have spaces in their postcode data. We thus need to insert them using
                    # by splitting the string and adding them to index position -3.
                    split = [i for i in list(postcode) if i != " "]
                    split.insert(-3, " ")
                    postcode = "".join(split)

                # Eastings and northings are stored in row index 2 and 3 respectively.
                easting = row[2]
                northing = row[3]

                # Append the data back to our list we created at the beginning.
                row_data = [postcode, easting, northing]
                postcode_data.append(row_data)
        except:
            pass

    return postcode_data
