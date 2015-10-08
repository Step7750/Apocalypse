import random

"""
This program will generate a pseudorandom number that the user has 10 tries to guess.
If the user's input is less than, or greater than or equal to the pseudorandom number, notify the user.

Continue the game even if the user has guessed the number, then ask for a final guess and print the appropriate message
"""


"""
    This function will compare the random value with the user's guess, and print the appropriate message
"""
def compare(rand_int, user_input):
    if rand_int > user_input:
        print("The number you hae entered is smaller than the pseudorandom number")
    elif rand_int <= user_input:
        print("The number you have entered is greater than or equal to the pseudorandom number")


"""
    This function will ask the user for a final guess and say whether it was the same as
    the pseudorandom number

    If they were wrong, print the pseudorandom number
"""
def final_guess(rand_int):
    final_guess_user = int(input("\nWhat is your final guess? (1-100)"))
    if final_guess_user == rand_int:
        print("\nYou guessed the number correctly!")
    else:
        print("\nYou didn't answer the number correctly, it was", rand_int)


"""
    This function is the first function called by the execution of the program

    It asks for a user's guess of a generated pseudorandom number 10 times and calls the "compare"
    function to compare the values with the pseudorandom inclusive int from 1-100

    At the end, it calls final_guess and passes in the generated random int
"""
def main():
    print("Try to guess the pseudorandom number!\n\n")
    rand_int = random.randint(1, 100)
    for i in range(10):
        user_input = int(input("Please enter a number (1-100): "))
        compare(rand_int, user_input)
    final_guess(rand_int)

# call the function "main"
main()
