import turtle

# I just played the game a bit and there are a shit ton of bugs, please find and fix them (game logic bugs)

# declare all of the main variables

board = [["K", "P", "P", "P", "K"],
        ["P", "W", "W", "W", "P"],
        ["W", "W", "W", "W", "W"],
        ["p", "W", "W", "W", "p"],
        ["k", "p", "p", "p", "k"]]

penalty_points = [0, 0]


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

# store the state of the highlighting of boxes

highlight_params = [0, 0, 0]
box_selected = 0


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
def draw_board():
    """
    This function will draw the game board onto the screen based upon the constants BOARD_DIMENSION and SYMBOL_DICT
    """

    # want to edit the global variables
    global box_locations, board_turtles

    # Execute Cam's function to draw the welcome text
    welcome_text(screen)

    # Initiate turtle that will draw the board
    main_board = turtle.Turtle()
    main_board.up()
    # set color to something a bit lighter than background
    main_board.color("#5E5E5E")
    main_board.hideturtle()
    #main_board.speed(0)
    # disable animations, this got really annoying
    main_board._tracer(False)

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
            char_turtle._tracer(False)

            char_turtle.up()
            char_turtle.setx(main_board.xcor() + (BOARD_DIMENSION/10))
            char_turtle.color("white")

            # get symbol from dict
            text_to_write = SYMBOL_DICT[get_piece(row, column)]

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
def move_piece(x, y, new_x, new_y, x2, y2, new_x2, new_y2):
    """
    This function handles the movement process for both pieces to make sure they are simultaneous
    x2, y2, new_x2, new_y2 is for the AI
    """
    global board
    # check whether the destination is the same for both

    if new_x == new_x2 and new_y == new_y2:
        print("Both pieces going to the same location")
        piece_type1 = get_piece(y, x)
        piece_type2 = get_piece(y2, x2)
        if piece_type1 == "p" and piece_type2 == "P":
            # both pawns, delete both
            print("Both are pawns, detroying both")
            board = delete_piece(x, y, board, board_turtles)
            board = delete_piece(x2, y2, board, board_turtles)
        elif piece_type1 == "k" and piece_type2 == "K":
            print("Both are knights, detroying both")
            board = delete_piece(x, y, board, board_turtles)
            board = delete_piece(x2, y2, board, board_turtles)
        elif piece_type1 == "p" and piece_type2 == "K":

            board = delete_piece(x, y, board, board_turtles)
            # execute move for AI
            board = execute_move(x2, y2, new_x2, new_y2, SYMBOL_DICT[get_piece(y2, x2)])
        elif piece_type1 == "k" and piece_type2 == "P":
            board = delete_piece(x2, y2, board, board_turtles)
            # execute move for AI
            board = execute_move(x, y, new_x, new_y, SYMBOL_DICT[get_piece(y, x)])
    else:
        # the pieces are moving to different locations, simultaneous movement does not matter


        # we need to save the pawn type for each value
        if x != -1:
            player_pawn = SYMBOL_DICT[get_piece(y, x)]
        if x2 != -1:
            ai_pawn = SYMBOL_DICT[get_piece(y2, x2)]

        if (x != -1):
            board = execute_move(x, y, new_x, new_y, player_pawn)
        if (x2 != -1):
            # since this is the second move,
            board = execute_move(x2, y2, new_x2, new_y2, ai_pawn)


def execute_move(x, y, new_x, new_y, symbol):
    """
    Executes a given move, rather than just handling them
    """
    row = 0
    column = 0

    global highlight_params, box_selected, board
    print("Moving The Piece At: Column:", highlight_params[1], "and Row:", highlight_params[2], "\n\t\t To: Column:", column, "and Row:", row)

    # replace piece on the board

    board = set_piece(board, new_y, new_x, get_piece(y, x))
    #board[new_y][new_x] = board[y][x]


    # check the saved symbol is the same as the current piece on the board at that location, make sure we don't delete it
    test_symbol = SYMBOL_DICT[get_piece(y, x)]
    if test_symbol == symbol:
        # the other player did not move into our old location, we can delete whatever is there
        board = delete_piece(x, y, board, board_turtles)

    # Get the turtle stored for the new block
    new_turtle = board_turtles[new_y][new_x]

    # clear the turtle (in case there is a written piece there) at the desired position
    new_turtle.clear()

    # write out the piece symbol centered in the block in ariel font with a size of the block height/width
    new_turtle.write(symbol, False, align="center", font=("Ariel", int(BOARD_DIMENSION/5)))

    return board


def valid_move(x, y, newx, newy, playername):
    # x, y is current piece that wants to move to newx, newy
    # playername is p or a depending on player or ai
    knight_moves = [[1, 2], [2, 1], [2, -1], [1, -2], [-1, -2], [-2, -1], [-2, 1], [-1, 2]]
    if (0 <= x <= 4 and 0 <= y <= 4 and 0 <= newx <= 4 and 0 <= newy <= 4):
        piece_type = get_piece(x, y)
        new_piece_type = get_piece(newx, newy)
        if piece_type.lower() == "k":
            if ((piece_type == "k" and playername == "p") or (piece_type == "K" and playername == "a")):
                # make sure they own that piece
                # see whether it is a valid knight move in the grid
                for move in knight_moves:
                    if (x + move[0]) == newx and (y + move[1] == newy):
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

    # get the turtle at x, y
    cur_turtle = board_turtles[y][x]

    # set the state of the board at that location to W
    board = set_piece(board, y, x, "W")

    # clear any symbols in that location
    cur_turtle.clear()

    return board


def get_piece(row, column):
    # gets the piece from the board at the specified coord
    string_array = board

    return string_array[row][column]


def set_piece(board_string, row, column, new_val):
    # sets the given piece to a new value
    string_array = board_string

    string_array[row][column] = new_val

    return string_array


def game_over():
    # checks whether one player won or not, given the game state
    print("Checking whether it is game over or not")

    # returns 1 if the player won, 0 if the AI won, 2 if it is a stalemate
    # returns 3 if the game is not over

    # check whether one of the players has made two illegal moves
    if penalty_points[0] == 2 and penalty_points[1] == 2:
        return 2
    elif penalty_points[0] == 2 and not penalty_points[1] == 2:
        return 0
    elif penalty_points[1] == 2 and not penalty_points[0] == 2:
        return 1

    # now check whether one of the players has no pawns left
    # loop over each pawn

    ai_pieces = 0
    player_pieces = 0

    # don't want to include the first two entries since they define the amount of infractions for that player
    for row in board:
        for column in row:
            if column == "K" or column == "P":
                ai_pieces += 1
            elif column == "k" or column == "p":
                player_pieces += 1

    if ai_pieces == 0:
        return 1
    elif player_pieces == 0:
        return 0
    else:
        return 3


def penalty_add(player):
    # this function will add a penalty to the player specified

    if player == "p":
        penalty_index = 0 #Define player as index 0
    else:
        penalty_index = 1 #Define player as index 1

    # add one to the penalty, and return the new board
    cur_val = int(penalty_points[penalty_index])
    cur_val += 1
    penalty_points[penalty_index] = cur_val

    return board


def clicky(x, y):
    # its a good name, isn't it?

    # check whether they clicked inside the board
    if box_locations[0][0][0] < x < (box_locations[4][4][0] + BOARD_DIMENSION/5) and (box_locations[4][4][1] - BOARD_DIMENSION/5) < y < box_locations[0][0][1]:
        # they clicked inside, let's go!

        global highlight_params, box_selected, board

        if highlight_params[0] != 0:
            # already selected
            highlight_params[0].clear()

        selected_turtle = turtle.Turtle()

        highlight_params[0] = selected_turtle
        selected_turtle._tracer(False)
        selected_turtle.hideturtle()
        selected_turtle.color("#007AFF")

        row = 0
        column = 0

        for n in box_locations:
            row += 1
            for i in n:
                column += 1

                if (i[0] + (BOARD_DIMENSION/5)) > x > i[0] and i[1] > y > (i[1] - (BOARD_DIMENSION/5)):

                    # What is this for?  print(highlight_params[1], highlight_params[2], column, row)
                    #print("Clicked on: Row", row, "& Column:", column)

                    if column != highlight_params[1] or row != highlight_params[2]:

                        if box_selected == 1:
                            # move the piece, a move was made

                            # generate the AI move
                            
                            player_validity = valid_move((highlight_params[2] - 1), (highlight_params[1] - 1), (row - 1), (column - 1), "p")

                            print(player_validity)

                            # generate the AI move
                            ai_val = ai_move()

                            if ai_val != False and player_validity == True:
                                # both made valid moves, we'll process them
                                move_piece((highlight_params[1] - 1), (highlight_params[2] - 1), (column - 1), (row - 1), ai_val[1], ai_val[0], ai_val[3], ai_val[2])
                            elif ai_val == False:
                                # give the ai a penalty, and process the move
                                print("AI Penalty")
                                board = penalty_add("a")
                                move_piece((highlight_params[1] - 1), (highlight_params[2] - 1), (column - 1), (row - 1), -1, 0, 0, 0)
                            elif player_validity == False:
                                print("Player Penalty")
                                board = penalty_add("p")
                                move_piece(-1, 0, 0, 0, ai_val[1], ai_val[0], ai_val[3], ai_val[2])


                            # check the game state, see whether someone won or not
                            # maybe we should game the screen to reflect this???
                            game_state = game_over()
                            if game_state != 3:
                                game_end_screen(game_state)

#                            print("AI Move:", ai_val)

                            box_selected = 0
                            highlight_params[0] = 0
                            highlight_params[1] = 0
                            highlight_params[2] = 0

                        elif get_piece(row - 1, column - 1) == "k" or get_piece(row - 1, column - 1) == "p":
                            # only let the user select tiles it owns
                            selected_turtle.up()
                            selected_turtle.goto(i[0], i[1])
                            selected_turtle.down()
                            for i2 in range(4):
                                selected_turtle.forward(BOARD_DIMENSION/5)
                                selected_turtle.right(90)
                            selected_turtle.up()
                            box_selected = 1

                            # save x y coords from the turtle for future reference
                            highlight_params[1] = column
                            highlight_params[2] = row
                    else:
                        print("deselected same box")
                        highlight_params[0] = 0
                        highlight_params[1] = 0
                        highlight_params[2] = 0
                        box_selected = 0

            column = 0
    else:
        print("Didn't click inside the board")


def ai_move():
    # this function figures out what valid move the AI should make
    # this is also a very stupid ai

    knight_moves = [[1, 2], [2, 1], [2, -1], [1, -2], [-1, -2], [-2, -1], [-2, 1], [-1, 2]]
    for x in range(5):
        for y in range(5):
            piece_type = get_piece(x, y)
            # check whether the AI owns this piece
            if piece_type == "K":

                for move in knight_moves:
                    if 0 <= (x + move[0]) < 5 and 0 <= (y + move[1]) < 5:
                        # it is inside the board
                        if get_piece((x+move[0]), (y+move[1])) != "P" and get_piece((x+move[0]), (y+move[1])) != "K":
                            # valid AI move for the knight, return it
                            return [x, y, (x+move[0]), (y+move[1])]

            elif piece_type == "P":

                # offset of rows is down for the AI
                offset_val = x + 1

                # check going diagonally right
                if 0 <= offset_val < 5 and 0 <= (y + 1) < 5:
                    # it is within the constraints of the board, check whether there is an enemy there
                    if get_piece(offset_val, (y + 1)) == "k" or get_piece(offset_val, (y + 1)) == "p":
                        return [x, y, offset_val, (y + 1)]
                elif 0 <= offset_val < 5 and 0 <= (y - 1) < 5:
                    # it is within the constraints of the board, check whether there is an enemy there
                    if get_piece(offset_val, (y - 1)) == "k" and get_piece(offset_val, (y - 1)) == "p":
                        return [x, y, offset_val, (y - 1)]
                if 0 <= offset_val < 5:
                    # check whether it is going forward
                    # check whether forward is whitespace or not
                    if get_piece(offset_val, y) == "W":
                        return [x, y, offset_val, y]
    return False


def game_end_screen(winner):
    turtle.clearscreen()
    screen.bgcolor("#4A4A4A")

    if winner == 0:
        text_write = "AI Won!"
    elif winner == 1:
        text_write = "Player Won!"
    elif winner == 2:
        text_write = "Stalemate!"

    end_turtle = turtle.Turtle()
    end_turtle.hideturtle()
    end_turtle.color("white")
    end_turtle._tracer(False)
    # the font size is just a relative static value to make sure it is proportionate
    end_turtle.write(text_write, move=False, align="center", font=("Arial", int(BOARD_DIMENSION/10)))



def main():

    # want to edit the global copy
    global board

    # print out the "Apocalypse" text
    print("""
       (                         (
       )\                      ) )\(              (
    ((((_)(  `  )  (    (  ( /(((_)\ ) `  )  (    ))\\
     )\ _ )\ /(/(  )\   )\ )(_) )_(()/( /(/(  )\  /((_)
     (_)_\(_|(_)_\((_) ((_| (_)_| |(_)|(_)_\((__|__))
      / _ \ | '_ \) _ \/ _|/ _` | | || | '_ \|_-< -_)
     /_/ \_\| .__/\___/\__|\__,_|_|\_, | .__//__|___|
            |_|                    |__/|_|
        """)
    print("Welcome to Apocalypse!!\nThis is a simultaneous turn game which is based upon rules of chess\n")
    draw_board()

    # bind the event handler
    screen.onclick(clicky)

    turtle.done()

# call the main function
if __name__ == '__main__':
    main()
