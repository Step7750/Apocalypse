import turtle

# CPSC 231 Group Project

# Welcome message by Cam.  Task Given:  Add a welcome message to the turtle screen.
def welcome_text(screen):

    welcome = turtle.Turtle()
    welcome2 = turtle.Turtle()
    height = screen.window_height() #Calculate the height of the canvas
    ycord = height/2 - (height * 0.030) #Determine the margin for the text to be placed
    ycord2 = height/2 - (height * 0.055)

    # Hide the turtle, lift the pen up, and increase speed
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
            text_to_write = SYMBOL_DICT[get_piece(board, row, column)]

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
        
    return box_locations


# Michael's function
def move_piece(x, y, new_x, new_y, x2, y2, new_x2, new_y2, board, board_turtles, SYMBOL_DICT, BOARD_DIMENSION):
    """
    This function handles the movement process for both pieces to make sure they are simultaneous

    x2, y2, new_x2, new_y2 is for the AI
    """

    # check whether the destination is the same for both

    if (new_x == new_x2 and new_y == new_y2):
        print("Both pieces going to the same location")
        piece_type1 = get_piece(board, y, x)
        piece_type2 = get_piece(board, y2, x2)
        if (piece_type1 == "p" and piece_type2 == "P"):
            # both pawns, delete both
            print("Both are pawns, detroying both")
            board = delete_piece(x, y, board, board_turtles)
            board = delete_piece(x2, y2, board, board_turtles)
        elif (piece_type1 == "k" and piece_type2 == "K"):
            print("Both are knights, detroying both")
            board = delete_piece(x, y, board, board_turtles)
            board = delete_piece(x2, y2, board, board_turtles)
        elif (piece_type1 == "p" and piece_type2 == "K"):

            board = delete_piece(x, y, board, board_turtles)
            # execute move for AI
            board = execute_move(x2, y2, new_x2, new_y2, board, board_turtles, SYMBOL_DICT, BOARD_DIMENSION)
        elif (piece_type1 == "k" and piece_type2 == "P"):
            board = delete_piece(x2, y2, board, board_turtles)
            # execute move for AI
            board = execute_move(x, y, new_x, new_y, board, board_turtles, SYMBOL_DICT, BOARD_DIMENSION)
    else:
        # the pieces are moving to different locations, simultaneous movement does not matter
        print("Executing moves normally")
        if (x != -1):
            board = execute_move(x, y, new_x, new_y, board, board_turtles, SYMBOL_DICT, BOARD_DIMENSION)
        if (x2 != -1):
            board = execute_move(x2, y2, new_x2, new_y2, board, board_turtles, SYMBOL_DICT, BOARD_DIMENSION)

    return board


def execute_move(x, y, new_x, new_y, board, board_turtles, SYMBOL_DICT, BOARD_DIMENSION):
    """
    Executes a given move, rather than just handling them

    """
    print("Moving ", x, y, "to", new_x, new_y)

    # replace piece on the board

    board = set_piece(board, new_y, new_x, get_piece(board, y, x))
    #board[new_y][new_x] = board[y][x]

    # get piece symbol from the dictionary (based upon board int)
    symbol = SYMBOL_DICT[get_piece(board, y, x)]
    # call delete piece
    board = delete_piece(x, y, board, board_turtles)

    # Get the turtle stored for the new block
    new_turtle = board_turtles[new_y][new_x]

    # clear the turtle (in case there is a written piece there) at the desired position
    new_turtle.clear()

    # write out the piece symbol centered in the block in ariel font with a size of the block height/width
    new_turtle.write(symbol, False, align="center", font=("Ariel", int(BOARD_DIMENSION/5)))

    return board


def valid_move(board, x, y, newx, newy, playername):
    # x, y is current piece that wants to move to newx, newy
    # playername is p or a depending on player or ai
    knight_moves = [[1, 2], [2, 1], [2, -1], [1, -2], [-1, -2], [-2, -1], [-2, 1], [-1, 2]]
    if (0 <= x <= 4 and 0 <= y <= 4 and 0 <= newx <= 4 and 0 <= newy <= 4):
        piece_type = get_piece(board, x, y)
        new_piece_type = get_piece(board, newx, newy)
        if piece_type.lower() == "k":
            print("Knight piece")
            if ((piece_type == "k" and playername == "p") or (piece_type == "K" and playername == "a")):
                # make sure they own that piece
                # see whether it is a valid knight move in the grid
                for move in knight_moves:
                    if (x + move[0]) == newx and (y + move[1] == newy):
                        print("Valid L shape, checking whether they own the outgoing piece")
                        if (playername == "p"):
                            if (new_piece_type != "p" and new_piece_type != "k"):
                                # valid knight move, continue on
                                return True
                        elif (playername == "a"):
                            if (new_piece_type != "P" and new_piece_type != "K"):
                                # valid knight move, continue on
                                return True
                return False
            else:
                # they don't own that piece
                return False

        elif piece_type.lower() == "p":
            print("pawn piece")

            if ((piece_type == "p" and playername == "p") or (piece_type == "P" and playername == "a")):
                # they own the pawn piece
                # check whether it is going diagonal
                print("Owns piece")
                print(x, y, newx, newy)

                # whether the pawn is moving upwards or downwards, depending on whether it is the AI or Player
                if playername == "p":
                    offset_val = x - 1
                else:
                    offset_val = x + 1
                if (newx == offset_val and newy == (y + 1)) or (newx == offset_val and newy == (y - 1)):
                    # check whether there is an enemy there
                    print("Checking diagonal")
                    if playername == "p":
                        if (new_piece_type == "K" or new_piece_type == "P"):
                            return True
                        else:
                            return False
                    elif playername == "a":
                        if (new_piece_type == "k" or new_piece_type == "p"):
                            return True
                        else:
                            return False
                elif (newx == offset_val and newy == y):
                    # check whether it is going forward
                    # check whether forward is whitespace or not
                    print("Checking whitespace")
                    if (new_piece_type == "W"):
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                # they don't own that piece
                return False
        else:
            print("Selected white space, invalid")
            return False
    else:
        print("One of the pieces isn't in the range of the board")
        return False



# Michael's function
def delete_piece(x, y, board, board_turtles):
    """
    This function will remove a board piece, and do the proper logic to remove the current location of it
    """
    print("Deleting ", x, y)

    # get the turtle at x, y
    cur_turtle = board_turtles[y][x]

    # set the state of the board at that location to W
    board = set_piece(board, y, x, "W")

    # clear any symbols in that location
    cur_turtle.clear()

    return board


def get_piece(board_string, row, column):
    # gets the piece from the board at the specified coord
    string_array = board_string.split(" ")

    # 5 rows per column
    row_offset = row * 5

    column_offset = (column + 1)

    # add total offset and remove 1 because computers count from 0
    total_offset = (2 + row_offset + column_offset) - 1

    return string_array[total_offset]


def set_piece(board_string, row, column, new_val):
    # sets the given piece to a new value
    string_array = board_string.split(" ")
    # 5 rows per column
    row_offset = row * 5

    column_offset = (column + 1)

    # add total offset and remove 1 because computers count from 0
    total_offset = (2 + row_offset + column_offset) - 1

    string_array[total_offset] = new_val

    return " ".join(string_array)


def game_over(board):
    # checks whether one player won or not, given the game state

    print("Checking whether it is game over or not")

    # returns 1 if the player won, 0 if the AI won, 2 if it is a stalemate
    # returns 3 if the game is not over

    # check whether one of the players has made two illegal moves
    if board[0] == "2" and board[2] == "2":
        return 2
    elif board[0] == "2":
        return 0
    elif board[2] == "2":
        return 1

    # now check whether one of the players has no pawns left
    # loop over each pawn
    pieces = board.split(" ")

    ai_pieces = 0
    player_pieces = 0

    # don't want to include the first two entries since they define the amount of infractions for that player
    for piece in pieces[2:]:
        if (piece == "K" or piece == "P"):
            ai_pieces += 1
        elif (piece == "k" or piece == "p"):
            player_pieces += 1

    if (ai_pieces == 0):
        return 1
    elif (player_pieces == 0):
        return 0
    else:
        # the game isn't over
        return 3


def penalty_add(board, player):
    # this function will add a penalty to the player specified
    split_board = board.split(" ")

    if player == "p":
        penalty_index = 0
    else:
        penalty_index = 1

    # add one to the penalty, and return the new board
    cur_val = int(split_board[penalty_index])
    cur_val += 1
    split_board[penalty_index] = str(cur_val)

    return " ".join(split_board)


def main():

    # declare all of the main variables

    # Stores the state of the board in a string, (MOST EFFICIENT METHOD EVER)
    # first 2 zeroes store the number of illegal moves for each player (player, ai)
    board = "0 0 " \
            "K P P P K " \
            "P W W W P " \
            "W W W W W " \
            "p W W W p " \
            "k p p p k"


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
    SYMBOL_DICT = {"K": "♞", "P": "♟", "k": "♘", "p": "♙", "W": ""}

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

    box_locations = draw_board(board, board_turtles, box_locations, screen, SYMBOL_DICT, BOARD_DIMENSION)

    # var that stores whether the game ended
    game_state = 3
    while game_state == 3:
        print("\nFor the Player's Turn\n")

        row = int(input("What row do you choose? (1-5) "))
        column = int(input("What column do you choose? (1-5) "))
        print("You chose row", row, "column", column)

        row_move = int(input("What row do you move to? (1-5)"))
        column_move = int(input("What column do you move to? (1-5)"))
        print("You want to move to row", row_move, "column", column_move)

        player_validity = valid_move(board, (row - 1), (column - 1), (row_move - 1), (column_move - 1), "p")

        print("\nFor the AI's Turn\n")

        row_ai = int(input("What row do you choose? (1-5) "))
        column_ai = int(input("What column do you choose? (1-5) "))
        print("You chose row", row_ai, "column", column_ai)

        row_move_ai = int(input("What row do you move to? (1-5) "))
        column_move_ai = int(input("What column do you move to? (1-5) "))
        print("You want to move to row", row_move_ai, "column", column_move_ai)

        ai_validity = valid_move(board, (row_ai - 1), (column_ai - 1), (row_move_ai - 1), (column_move_ai - 1), "a")

        print(player_validity, ai_validity)

        if player_validity == True and ai_validity == True:
            board = move_piece((column - 1), (row - 1), (column_move - 1), (row_move - 1), (column_ai - 1), (row_ai - 1), (column_move_ai - 1), (row_move_ai - 1), board, board_turtles, SYMBOL_DICT, BOARD_DIMENSION)
        elif player_validity == False and ai_validity == True:
            # add penalty point to player
            board = penalty_add(board, "p")
            board = move_piece(-1, 0, 0, 0, (column_ai - 1), (row_ai - 1), (column_move_ai - 1), (row_move_ai - 1), board, board_turtles, SYMBOL_DICT, BOARD_DIMENSION)
        elif player_validity == True and ai_validity == False:
            # add penalty point to ai
            board = penalty_add(board, "a")
            board = move_piece((column - 1), (row - 1), (column_move - 1), (row_move - 1), -1, 0, 0, 0, board, board_turtles, SYMBOL_DICT, BOARD_DIMENSION)
        elif player_validity == False and ai_validity == False:
            # add penalty points to both
            board = penalty_add(board, "a")
            board = penalty_add(board, "p")

        print(board)

        game_state = game_over(board)

    # if it got here, the game has ended, print out who won
    if game_state == 0:
        print("AI Won")
    elif game_state == 1:
        print("Player Won")
    else:
        print("Stalemate")

    turtle.done()

# call the main function
if __name__ == '__main__':
    main()
