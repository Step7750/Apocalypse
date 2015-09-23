# CPSC 231 Group Project
#
# 0 = nothing, first number 1 = pawn, 2 = knight. Second number dictates player 0 = ai, 1 = player


board = [[20, 10, 10, 10, 20],
         [10, 0, 0, 0, 10],
         [0, 0, 0, 0, 0],
         [11, 0, 0, 0, 11],
         [21, 11, 11, 11, 21]]

def print_board():
    for row in range(0, 5):
        for column in range(0, 5):
            if board[row][column] == 0:
                print("  |", end="")
            elif board[row][column] == 10:
                print("♟ |", end="")
            elif board[row][column] == 20:
                print("♞ |", end="")
            elif board[row][column] == 11:
                print("♙ |", end="")
            elif board[row][column] == 21:
                print("♘ |", end="")
        print("\n---------------")

print("Welcome to Apocalypse\nThis is a simultaneous turn game that is based upon rules of chess")
print_board()

row = input("What row do you choose? (1-5)")
column = input("What column do you choose? (1-5)")
print("You chose row", row, "column", column)
