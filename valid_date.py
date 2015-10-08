"""
This program shows unit testing results of two functions that will determine whether a given date
is valid or not
"""


"""
Determine whether a given year is a leap year or not
Return boolean based on the state
"""
def isvalid_leap_year(year):
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return True
        else:
            return True
    # Not a leap year
    return False


"""
Checks whether a given date stamp is valid or not
Return boolean based on the state
"""
def isvalid_date(month, day, year):
    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        # month with 31 days
        if 1 <= day <= 31:
            # valid day
            return True
    elif month == 4 or month == 6 or month == 9 or month == 11:
        # month with 30 days
        if 1 <= day <= 30:
            # valid day
            return True
    elif month == 2:
        # check if leap year
        if isvalid_leap_year(year):
            if 1 <= day <= 29:
                return True
        else:
            if 1 <= day <= 28:
                return True

    # if it ends up here, it is invalid
    return False


"""
Unit test the isvalid_date function with some static test cases
"""
def main():
    print("Printing out the validity of test cases\n")

    print("2, 29, 2015")
    print(isvalid_date(2, 29, 2015))  # false
    print("8, 29, 2005")
    print(isvalid_date(8, 29, 2005))  # true
    print("1, 5, 2560")
    print(isvalid_date(1, 5, 2560))   # true
    print("15, 29, 2000")
    print(isvalid_date(15, 29, 2000)) # false
    print("2, 29, 1200")
    print(isvalid_date(2, 29, 1200))  # true
    print("4, 15, 1")
    print(isvalid_date(4, 15, 1))     # true
    print("2, 29, 2016")
    print(isvalid_date(2, 29, 2016))  # true


if __name__ == '__main__':
    main()
