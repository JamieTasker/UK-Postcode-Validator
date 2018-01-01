# Postcode logic v 1.0
# Takes a full GB postcode and attempts to correct common errors.
# Created by Jamie Tasker on 05/11/2017.

from fuzzywuzzy import process

# The Postcode class accepts a string object.
class Postcode(object):
    """"A Postcode object"""
    def __init__(self, postcode):
        self.postcode = postcode
        # Break each character of the string into a list called self.split.
        self.split = list(self.postcode)

    def number_to_char(self, char):
        """Convert common number errors to characters. Common errors include accidentally using 0 instead of O."""
        if char == "0":
            return "O"
        elif char == "1":
            return "I"
        elif char == "3":
            return "E"
        elif char == "5":
            return "S"
        else:
            return char

    def char_to_number(self, char):
        """Convert common character errors to numbers. Common errors include accidentally using O instead of 0."""
        if char.lower() == "o":
            return "0"
        elif char.lower() == "!":
            return "1"
        elif char.lower() == '"':
            return "2"
        elif char.lower() == "£":
            return "3"
        elif char.lower() == "$":
            return "4"
        elif char.lower() == "%":
            return "5"
        elif char.lower() == "^":
            return "6"
        elif char.lower() == "&":
            return "7"
        elif char.lower() == "*":
            return "8"
        elif char.lower() == "(":
            return "9"
        elif char.lower() == ")":
            return "0"
        elif char.lower() == "i":
            return "1"
        elif char.lower() == "e":
            return "3"
        elif char.lower() == "s":
            return "5"
        else:
            return char

    def case_check(self, split):
        """Create a new version of the split postcode in uppercase and return it."""
        split = [i.upper() for i in split]
        return split

    def space_check(self, split):
        """Remove all spaces from the postcode and place a new one at index -3."""
        split = [i for i in split if i != " "]
        split.insert(-3, " ")

        return split

    def validate_postcode(self):
        """Validate the postcode string"""
        # Create a copy of self.split called new_postcode.
        new_postcode = self.split

        # Perform the space checks and case checks.
        new_postcode = self.space_check(new_postcode)
        new_postcode = self.case_check(new_postcode)

        # Ensure that the character in position 0 is a character.
        char1 = new_postcode[0]
        char1 = self.number_to_char(char1)
        new_postcode[0] = char1

        # Find out the length of the first half the postcode before the space. Sme UK postcodes are 4 letters long
        # before the space e.g. "LS14" nnd others can be two or three e.g "M1" or "S71"
        length_before_space = len(new_postcode[:-4])
        if length_before_space == 4:
            # If the postcode has a length of 4 before the space, we know that the correct format is two characters
            # followed by two numbers. We thus can perform checks to ensure that this is the case.
            char2 = new_postcode[1]
            char2 = self.number_to_char(char2)
            new_postcode[1] = char2
            char3 = new_postcode[2]
            char3 = self.char_to_number(char3)
            new_postcode[2] = char3

        # Postcodes that are three characters long before the space are more complicated. This is because we should
        # have two possible postcode formats: character, character, number (LS6) or character, number, number (S71)
        elif length_before_space == 3:
            char2 = new_postcode[1]
            # First of all, we attempt to convert the character in index 1 to an integer.
            try:
                int(char2)
            except:
                # If this conversion fails, we test for common number errors. If these errors are found, we convert
                # the incorrect character into a number.
                if char2 in ["!", '"', "£", "$", "%", "^", "&", "*", "(", ")"]:
                    char2 = self.char_to_number(char2)
                else:
                    # If the conversion fails and the character does not match common number errors, we assume that
                    # the character is not a number and precede.
                    new_postcode[1] = char2
            # We now do the exact same process for the character in index 2.
            char3 = new_postcode[2]
            try:
                int(char3)
            except:
                if char3 in ["!", '"', "£", "$", "%", "^", "&", "*", "(", ")"]:
                    char3 = self.char_to_number(char2)
                else:
                    new_postcode[1] = char3

        # Now we start working backwards. We always know that the character in index -5 is a number, so we can convert
        # it from a character if an error is detected.
        number1_1_part = new_postcode[-5]
        number1_1_part = self.char_to_number(number1_1_part)
        new_postcode[-5] = number1_1_part

        # Likewise, we also know that position -3 is a number, so we can attempt to change that too.
        number_2_part = new_postcode[-3]
        number_2_part = self.char_to_number(number_2_part)
        new_postcode[-3] = number_2_part

        # The final two characters are not numbers, so we can run the number_to_char method to convert them.
        char1_2_part = new_postcode[-2]
        char1_2_part = self.number_to_char(char1_2_part)
        new_postcode[-2] = char1_2_part

        char2_2_part = new_postcode[-1]
        char2_2_part = self.number_to_char(char2_2_part)
        new_postcode[-1] = char2_2_part

        # Finally, we join the split string back together and return it.
        return "".join(new_postcode)

    def fuzzy_logic(self, postcode_list, tolerance):

        fuzzy_match = process.extractOne(self.postcode, postcode_list)
        if fuzzy_match[1] >= tolerance:
            return fuzzy_match
        else:
            return "No Match", 0
