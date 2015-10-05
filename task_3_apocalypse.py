import turtle

# CPSC 231 Group Project

# Welcome message by Cam.  Task Given:  Add a welcome message to the turtle screen.
def welcome_text(screen):

    welcome = turtle.Turtle()
    welcome2 = turtle.Turtle()
    height = screen.window_height() #Calculate the height of the canvas
    ycord = height/2 - (height * 0.035) #Determine the margin for the text to be placed
    ycord2 = height/2 - (height * 0.055)

    # Hide the turtle, lift the pen up, and increase speed.
    welcome.hideturtle()
    welcome.penup()
    welcome.speed(0)

    welcome2.hideturtle()
    welcome2.penup()
    welcome2.speed(0)

    # Position the text accordingly, and display it in the center.
    welcome.setposition(x=0, y=ycord)
    welcome.write("Welcome to Apocalypse!!", move=False, align="center", font=("Arial", 18))
    welcome2.setposition(x=0, y=ycord2)
    welcome2.write("This is a simultaneous turn game which is based upon rules of chess", move=False, align="center",
                   font=("Arial", 18))


# Stepan's function
def draw_board(board, board_turtles, box_locations, screen, SYMBOL_DICT, BOARD_DIMENSION):
    """
    This function will draw the game board onto the screen based upon the constants BOARD_DIMENSION and SYMBOL_DICT
    """

    # Execute Cam's function to draw the welcome text
    welcome_text(screen)

    print("Drawing board")

    # Initiate turtle that will draw the board
    main_board = turtle.Turtle()
    main_board.up()
    # set color to something a bit lighter than background
    main_board.color("#5E5E5E")
    main_board.speed(0)

    # center the board, -10 is a static offset
    main_board.goto(-(BOARD_DIMENSION/2) - 10, BOARD_DIMENSION/2)

    # create outer rectangle
    main_board.down()
    main_board.pendown()
    for i in range(4):
        main_board.forward(BOARD_DIMENSION)
        main_board.right(90)
    main_board.penup()

    # move turtle back to top left of the board
    main_board.goto(-(BOARD_DIMENSION/2) - 10, BOARD_DIMENSION/2)

    # iterate through each box and draw it
    for row in range(0, 5):
        for column in range(0, 5):
            # store the top left of every box in the chess table for future reference and click events
            box_locations[row][column][0] = main_board.xcor()
            box_locations[row][column][1] = main_board.ycor()

            # create checkerboard pattern

            # check if the row is 0, 2, 4
            if row % 2 == 0:
                # Check whether there is an even column
                if column % 2 == 0:
                    # print out a block
                    main_board.begin_fill()
                    for i in range(4):
                        main_board.forward(BOARD_DIMENSION/5)
                        main_board.right(90)
                    main_board.end_fill()
            else:
                # row is 1, 3
                # Check whether it is an odd column
                if column % 2 != 0:
                    main_board.begin_fill()
                    for i in range(4):
                        main_board.forward(BOARD_DIMENSION/5)
                        main_board.right(90)
                    main_board.end_fill()

            # write out the characters (board pieces)
            # create new turtle just for the character, and store it in the array board_turtles
            char_turtle = turtle.Turtle()
            char_turtle.hideturtle()
            char_turtle.speed(0)

            char_turtle.up()
            char_turtle.setx(main_board.xcor() + (BOARD_DIMENSION/10))
            char_turtle.color("white")

            # get symbol from dict
            text_to_write = SYMBOL_DICT[board[row][column]]

            # mac osx and windows have different symbol designs, with diff height/width
            # haven't tested on a Unix system other than Mac OSX, Linux may have a different character set
            char_turtle.sety(main_board.ycor() - (BOARD_DIMENSION/5))
            char_turtle.write(text_to_write, False, align="center", font=("Ariel", int(BOARD_DIMENSION/5)))

            # add turtle to the board so that the memory location is stored
            board_turtles[row][column] = char_turtle

            # move the turtle to the right for the distance of one block
            main_board.setx(main_board.xcor() + (BOARD_DIMENSION/5))

        # reset x position each time a row is done (to the very left), move the turtle down one block
        main_board.setpos(-(BOARD_DIMENSION/2) - 10, (main_board.ycor() - (BOARD_DIMENSION/5)))


# Michael's function
def move_piece(x, y, new_x, new_y, board, board_turtles, SYMBOL_DICT, BOARD_DIMENSION):
    """
    This function only moves pieces and doesn't apply valid logic whether they should be there

    This function will only replace what is in the tile
    """
    print("Moving ", x, y, "to", new_x, new_y)

    # replace piece on the board
    board[new_y][new_x] = board[y][x]

    # get piece symbol from the dictionary (based upon board int)
    symbol = SYMBOL_DICT[board[y][x]]

    # call delete piece
    delete_piece(x, y, board, board_turtles)

    # Get the turtle stored for the new block
    new_turtle = board_turtles[new_y][new_x]

    # clear the turtle (in case there is a written piece there) at the desired position
    new_turtle.clear()

    # write out the piece symbol centered in the block in ariel font with a size of the block height/width
    new_turtle.write(symbol, False, align="center", font=("Ariel", int(BOARD_DIMENSION/5)))


# Michael's function
def delete_piece(x, y, board, board_turtles):
    """
    This function will remove a board piece, and do the proper logic to remove the current location of it
    """
    print("Deleting ", x, y)

    # get the turtle at x, y
    cur_turtle = board_turtles[y][x]

    # set the state of the board at that location to 0
    board[y][x] = 0

    # clear any symbols in that location
    cur_turtle.clear()


def main():

    # declare all of the main variables

    # Stores the state of the board
    # 0 = nothing, first number 1 = pawn, 2 = knight. Second number dictates player 0 = ai, 1 = player
    board = [[20, 10, 10, 10, 20],
             [10, 0, 0, 0, 10],
             [0, 0, 0, 0, 0],
             [11, 0, 0, 0, 11],
             [21, 11, 11, 11, 21]]

    # X, Y Coords for each box (to make our lives easier for onclick events)
    box_locations = [[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                     [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                     [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                     [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
                     [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]]


    # store individual turtle objects for each position on the board (makes editing easier)
    board_turtles = [[0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0]]

    # Initiate the screen with bgcolor
    screen = turtle.Screen()
    screen.bgcolor("#4A4A4A")


    # Constants created by Khesualdo, they store the appropriate board dimensions and a dict defining the conversion from int to symbol

    # width of the board is equal to 75% of the screen width
    BOARD_DIMENSION = screen.window_width() * 0.75

    # dictionary that converts location num to a symbol
    SYMBOL_DICT = {20: "♞", 10: "♟", 21: "♘", 11: "♙", 0: ""}

    # print out the "Apocalypse" text
    print("""
       (                         (
       )\                      ) )\(               (
    ((((_)(  `  )   (    (  ( /(((_)\ ) `  )  (   ))\\
     )\ _ )\ /(/(   )\   )\ )(_))_(()/( /(/(  )\ /((_)
     (_)_\(_|(_)_\ ((_) ((_|(_)_| |)(_)|(_)_\((_|_))
      / _ \ | '_ \) _ \/ _|/ _` | | || | '_ \|_-< -_)
     /_/ \_\| .__/\___/\__|\__,_|_|\_, | .__//__|___|
            |_|                    |__/|_|
        """)
    print("Welcome to Apocalypse!!\nThis is a simultaneous turn game which is based upon rules of chess\n")

    draw_board(board, board_turtles, box_locations, screen, SYMBOL_DICT, BOARD_DIMENSION)

    row = int(input("What row do you choose? (1-5)"))
    column = int(input("What column do you choose? (1-5)"))
    print("You chose row", row, "column", column)

    row_move = int(input("What row do you move to? (1-5)"))
    column_move = int(input("What column do you move to? (1-5)"))
    print("You want to move to row", row_move, "column", column_move)

    move_piece((column - 1), (row - 1), (column_move - 1), (row_move - 1), board, board_turtles, SYMBOL_DICT, BOARD_DIMENSION)

    turtle.done()

# call the main function
if __name__ == '__main__':
    main()
