# csvloader v 1.0
# Returns a nested list containing postcodes, eastings and northings from a csv file containing Postcode information.
# Created by Jamie Tasker on 25/11/2017

import csv
import os

# The csv_load function returns the postcode information necessary to create a postcode database. 
# The user will specify the index the position of the columns containing the postcodes, eastings and northings.
def csv_load(csv_path, postcode_col, easting_col, northing_col, headings=True, coords_present=True):

	with open(csv_path, "r") as csv_file:
		csv_reader = csv.reader(csv_file, delimiter = ",", lineterminator = "\n")
		# If the user says that the CSV file contains headings, the first row of the file is skipped.
		if headings == True:
			next(csv_reader)

		# Create an empty list that the postcode data will be saved within.
		postcode_data = list()
		for row in csv_reader:
			# Save the postcode information contained within postcode_col to a variable simply called 'postcode'.
			postcode = row[postcode_col]

			# Add a space to the postcode if it does not already exist.
			if " " not in postcode:
				# Split the postcode into a list and add a " " into index position -3.
				split = [i for i in list(postcode) if i != " "]
				split.insert(-3, " ")
				postcode = "".join(split)

			# Save easting and northing data.
			if coords_present == True:
				easting = row[easting_col]
				northing = row[northing_col]
			else:
				easting = "0"
				northing = "0"

			# Append the data back to our list we created at the beginning.
			row_data = [postcode, easting, northing]
			postcode_data.append(row_data)

	return postcode_data

# Function to return the first row of the CSV_file.
# This is used to display the preview of the file where the user selects the columns containing
# postcodes, eastings and northings.
def get_first_row(csv_path):

	with open(csv_path, "r") as csv_file:
		csv_reader = csv.reader(csv_file, delimiter = ",", lineterminator = "\n")

		# Use next() to extract the first iteration of the csv file into a variable called headings.
		headings = next(csv_reader)
		# valid_length prevents the user from trying to select a column that does not exist.
		valid_length = len(headings)

		# Create a list of the headings and return them to the main application.
		heading_no = 1
		headings_formatted = list()
		for heading in headings:
			headings_formatted.append("Column " + str(heading_no) + ": " + heading)
			heading_no += 1

	return headings_formatted, valid_length

# Function to check whether the csv_path is valid.
def valid_csv_test(csv_path):

	# Simply try to open the CSV file and create a reader. If an exception occurs, the CSV
	# file is invalid and cannot be used.
	try:
		csv_file = open(csv_path, "r")
		reader = csv.reader(csv_file, delimiter = ",", lineterminator = "\n")
		csv_file.close()
		return True
	except:
		return False
