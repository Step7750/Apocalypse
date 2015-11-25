"""
CPSC 231 Group Project - Apocalypse 095

Play the game of Apocalypse! A simultaneous game based upon the principles of chess.

The rules can be found here: https://en.wikipedia.org/wiki/Apocalypse_(chess_variant)


Created by: Stepan Fedorko-Bartos, Khesualdo Condori Barykin, Cameron Davies, Michael Shi

Features:
- Fully interactive GUI to play Apocalypse
- Dark Theme Interface
- Main Menu Screen
- Saving and Loading game states
- Variable levels of AI difficulty (Can you beat it on hard?)
- Advanced MiniMax AI w/ Alpha Beta Pruning (that handles the simultaneous nature of Apocalypse)
- Uses Recursion for the MiniMax AI

"""

import turtle
import platform   # used to know what the scaling should be
import copy       # for deep copies (for the minimax ai)



# set the score weighting for pawns and knights
knight_points = 1
pawn_points = 3

# declare all of the global variables

board = [["K", "P", "P", "P", "K"],
        ["P", "W", "W", "W", "P"],
        ["W", "W", "W", "W", "W"],
        ["p", "W", "W", "W", "p"],
        ["k", "p", "p", "p", "k"]]

# penalty points for each player (ai, player)
penalty_points = [0, 0]

# X, Y coords for each board box (to make our lives easier for onclick events)
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
#screen.setup(width=400, height=1000)
screen.title("Apocalypse")

PenaltyTurtle = turtle.Turtle()
PenaltyTurtle.hideturtle()
penaltyTurtleAI = turtle.Turtle()
penaltyTurtleAI.hideturtle()
MessagesTurtle = turtle.Turtle()
MessagesTurtle.hideturtle()

# amount of moves the AI thinks forward (computation gets exponential). Anything over 7 will take a very long time....
depth_amt = 6

# for proper scaling with many dimensions, if the width is substantially more, go by the height of the screen
if (screen.window_width()/screen.window_height() > 1.20):
    # width of the board is equal to 95% of the screen height
    BOARD_DIMENSION = screen.window_height()*0.95
else:
    # width of the board is equal to 75% of the screen width
    BOARD_DIMENSION = screen.window_width()*0.75

# dictionary that converts location num to a symbol
SYMBOL_DICT = {"K": "♞", "P": "♟", "k": "♘", "p": "♙", "W": ""}

# store the state of the highlighting of boxes
highlight_params = [0, 0, 0, False, 0]
box_selected = 0

# stores coords of created buttons
buttons = []

# stores text height for the queue messages
text_height = int(BOARD_DIMENSION/7.5)

# stores text height for strings related to the penalty score board
penalty_text_height = int(BOARD_DIMENSION/50)

# creates the move offset that is needed to increment by everytime a new message is printed (creates extra var to save it)
moveOffset = BOARD_DIMENSION/2 - (text_height/0.7) - (penalty_text_height * 1.5)
saved_offset = moveOffset

# define dynamic scaling variable that stores whether to scale by height or width
scaling_value = screen.window_width()
if screen.window_height() < screen.window_width():
    scaling_value = screen.window_height()


def print_board():
    print("Board:")
    for i in range(5):
        print(board[i])


def draw_board():
    """
    This function will draw the game board onto the screen based upon the constants BOARD_DIMENSION and SYMBOL_DICT
    """

    # want to edit the global variables
    global box_locations, board_turtles, buttons
    del buttons[:]

    # Initiate turtle that will draw the board
    main_board = turtle.Turtle()
    main_board.up()
    # set color to something a bit lighter than background
    main_board.color("#5E5E5E")
    main_board.hideturtle()
    #main_board.speed(0)
    # disable animations, this got really annoying
    main_board._tracer(False)

    # Make the board 80% width and 10% to the left
    main_board.goto(-(BOARD_DIMENSION/2) - (screen.window_width()*0.1), BOARD_DIMENSION/2)

    # create outer rectangle
    main_board.down()
    main_board.pendown()
    for i in range(4):
        main_board.forward(BOARD_DIMENSION)
        main_board.right(90)
    main_board.penup()

    # move turtle back to top left of the board
    main_board.goto(-(BOARD_DIMENSION/2) - (screen.window_width()*0.1), BOARD_DIMENSION/2)

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

            if platform.system() == "Windows":
                # adjust scaling of the y coord based upon the os
                char_turtle.sety(main_board.ycor() - (BOARD_DIMENSION/4.10))
                char_turtle.write(text_to_write, False, align="center", font=("Ariel", int(BOARD_DIMENSION/5.4)))
            else:
                # haven't tested on a Unix system other than Mac OSX, Linux may have a different character set
                char_turtle.sety(main_board.ycor() - (BOARD_DIMENSION/5))
                char_turtle.write(text_to_write, False, align="center", font=("Ariel", int(BOARD_DIMENSION/5)))

            # add turtle to the board so that the memory location is stored
            board_turtles[row][column] = char_turtle

            # move the turtle to the right for the distance of one block
            main_board.setx(main_board.xcor() + (BOARD_DIMENSION/5))

        # reset x position each time a row is done (to the very left), move the turtle down one block
        main_board.setpos(-(BOARD_DIMENSION/2) - (screen.window_width()*0.1), (main_board.ycor() - (BOARD_DIMENSION/5)))

    # create buttons on the main board to perform various actions, the offsets were calculated by eye and are relative
    draw_button(BOARD_DIMENSION/2 + (BOARD_DIMENSION/2 * 0.03), -BOARD_DIMENSION/2.13, "Load Game", 'load_state()', screen.window_width()*0.20, scaling_value/36)
    draw_button(BOARD_DIMENSION/2 + (BOARD_DIMENSION/2 * 0.03), -BOARD_DIMENSION/2.50, "Save Game", 'save_state()', screen.window_width()*0.20, scaling_value/36)
    draw_button(BOARD_DIMENSION/2 + (BOARD_DIMENSION/2 * 0.03), -BOARD_DIMENSION/3.02, "Main Menu", 'draw_main_screen()', screen.window_width()*0.20, scaling_value/36)


def move_piece(x, y, new_x, new_y, x2, y2, new_x2, new_y2):
    """
    This function handles the movement process for both pieces to make sure they are simultaneous
    x2, y2, new_x2, new_y2 is for the AI
    x, y, new_x, new_y is for the player
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
            delete_piece(x, y, board_turtles)
            delete_piece(x2, y2, board_turtles)
        elif piece_type1 == "k" and piece_type2 == "K":
            print("Both are knights, detroying both")
            delete_piece(x, y, board_turtles)
            delete_piece(x2, y2, board_turtles)
        elif piece_type1 == "p" and piece_type2 == "K":

            delete_piece(x, y, board_turtles)
            # execute move for AI
            execute_move(x2, y2, new_x2, new_y2, SYMBOL_DICT[get_piece(y2, x2)])
        elif piece_type1 == "k" and piece_type2 == "P":
            delete_piece(x2, y2, board_turtles)
            # execute move for AI
            execute_move(x, y, new_x, new_y, SYMBOL_DICT[get_piece(y, x)])
    else:
        # the pieces are moving to different locations, simultaneous movement does not matter


        # we need to save the pawn type for each value
        if x != -1:
            player_pawn = SYMBOL_DICT[get_piece(y, x)]
            player_code = get_piece(y, x)
        if x2 != -1:
            ai_pawn = SYMBOL_DICT[get_piece(y2, x2)]
            ai_code = get_piece(y2, x2)

        if (x != -1):
            execute_move(x, y, new_x, new_y, player_pawn, player_code)
        if (x2 != -1):
            # since this is the second move,
            execute_move(x2, y2, new_x2, new_y2, ai_pawn, ai_code)


def execute_move(x, y, new_x, new_y, symbol, piece_code=-1, force_delete=3):
    """
    Executes a given move on the board (modifying values, drawing the board)

    :param x: **int** current piece x coord
    :param y: **int** current piece y coord
    :param newx: **int** new piece x coord
    :param newy: **int** new piece y coord
    :param symbol: **string** Symbol of the piece you're moving
    :param piece_code: **int** Piece value (on the board) to use (optional)
    :param force_delete: **int** Force delete the previous piece on the board (optional)
    :return:
    """

    global highlight_params, box_selected, board
    print("Moving The Piece At: Column:", x, "and Row:", y, "\n\t\t\t To: Column:", new_x, "and Row:", new_y)

    # replace piece on the board
    if piece_code == -1:
        piece_code = get_piece(y, x)

    set_piece(new_y, new_x, piece_code)


    # check the saved symbol is the same as the current piece on the board at that location, make sure we don't delete it
    test_symbol = SYMBOL_DICT[get_piece(y, x)]
    if test_symbol == symbol and force_delete == 3:
        # the other player did not move into our old location, we can delete whatever is there
        delete_piece(x, y, board_turtles)
    if force_delete == True:
        print("Force deleting the piece")
        delete_piece(x, y, board_turtles)

    # Get the turtle stored for the new block
    new_turtle = board_turtles[new_y][new_x]

    # clear the turtle (in case there is a written piece there) at the desired position
    new_turtle.clear()

    # write out the piece symbol centered in the block in ariel font with a size of the block height/width

    if platform.system() == "Windows":
        # adjust scaling of the y coord based upon the os
        new_turtle.write(symbol, False, align="center", font=("Ariel", int(BOARD_DIMENSION/5.5)))
    else:
        # haven't tested on a Unix system other than Mac OSX, Linux may have a different character set
        new_turtle.write(symbol, False, align="center", font=("Ariel", int(BOARD_DIMENSION/5)))
    displayMove(x, y, new_x, new_y)


def valid_move(x, y, newx, newy, playername):
    """
    Checks whether a given move is valid or not for playername

    :param x: **int** current piece x coord
    :param y: **int** current piece y coord
    :param newx: **int** new piece x coord
    :param newy: **int** new piece y coord
    :param playername: **string** playername is p or a depending on player or ai
    :return:
    """
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
                    print("New Piece is " + new_piece_type)
                    print("Board State: " + str(board))
                    if playername == "p":
                        if new_piece_type == "K" or new_piece_type == "P":
                            return True
                        else:
                            return False
                    elif playername == "a":
                        if new_piece_type == "k" or new_piece_type == "p":
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


def ai_score(board_state):
    """
    Computes the score of the board for the AI

    :param board_state: multidimensional list defining the board state
    :return: **numerical** returns score of the current board for the AI
    """
    current_score = 0
    current_pawns = 0
    for row in range(5):
        for column in range(5):
            if board_state[row][column] == "K":
                current_score += knight_points
            elif board_state[row][column] == "P":
                current_score += pawn_points
                current_pawns += 1

    player_score = 0
    player_pawns = 0
    for row in range(5):
        for column in range(5):
            if board_state[row][column] == "k":
                player_score += knight_points
            elif board_state[row][column] == "p":
                player_score += pawn_points
                player_pawns += 1
    if len(possible_moves(board_state, 0)) == 0:
        return float("-infinity")
    if current_pawns == 0 and player_pawns == 0:
        # stalemate, return value of 0
        return 0
    if current_pawns == 0:
        # the player won
        return float("-infinity")
    elif player_pawns == 0:
        # the ai won
        return float("infinity")
    else:
        return current_score-player_score


def combine_moves(board_state_val, x, y, new_x, new_y, x2, y2, new_x2, new_y2):
    """
    Combines moves together

    :param board_state:
    :return:
    """
    board_state = copy.deepcopy(board_state_val)
    if new_x == new_x2 and new_y == new_y2:

        piece_type1 = board_state[x][y]
        piece_type2 = board_state[x2][y2]
        if piece_type1 == "p" and piece_type2 == "P":
            # both pawns, delete both
            board_state[x][y] = "W"
            board_state[x2][y2] = "W"
        elif piece_type1 == "k" and piece_type2 == "K":
            board_state[y][x] = "W"
            board_state[x2][y2] = "W"
        elif piece_type1 == "p" and piece_type2 == "K":

            board_state[x][y] = "W"
            # execute move for AI
            board_state[new_x2][new_y2] = board_state[y2][x2]
            board_state[x2][y2] = "W"
        elif piece_type1 == "k" and piece_type2 == "P":
            board_state[x2][y2] = "W"
            # execute move for player
            board_state[new_x][new_y] = board_state[y][x]
            board_state[x][y] = "W"
    else:
        # the pieces are moving to different locations, simultaneous movement does not matter

        player_val = copy.copy(board_state[x][y])
        ai_val = copy.copy(board_state[x2][y2])

        board_state[new_x][new_y] = player_val
        board_state[x][y] = "W"

        board_state[new_x2][new_y2] = ai_val
        board_state[x2][y2] = "W"

        if ai_val == "P" and new_x == 4:
            # reached last rank, process it
            board_state[x2][y2] = "K"

        if ai_val == "p" and new_x == 0:
            # reached last rank, process it
            board_state[x2][y2] = "k"

        # check whether they reached the last rank

    # check whether we need to upgrade pawns to knights

    return board_state


def combine_single_move(board_state_val, x, y, new_x, new_y):
    """
    Combines one move onto the desired board
    """
    board_state = copy.deepcopy(board_state_val)

    player_val = copy.copy(board_state[x][y])

    board_state[new_x][new_y] = player_val
    board_state[x][y] = "W"
    # check whether we need to upgrade pawns to knights

    return board_state


def maximize(depth, board_state, alpha, beta, force_reply=0):
    """
    Maximizes nodes in the depth level for the AI
    Implements alpha beta pruning
    """
    alpha = copy.copy(alpha)
    beta = copy.copy(beta)
    board_copy = copy.deepcopy(board_state)
    best_move = []
    if depth == 0:
        # reached end of depth level, send back the score
        return ai_score(board_copy)
    moves = possible_moves(board_copy, 0)
    for move in moves:
        move_board = copy.deepcopy(board_copy)
        cur_score = minimize(depth - 1, move_board, move, alpha, beta)
        if force_reply == 1:
            print("Move with score " + str(cur_score) + "  Move: " + str(move))
        if cur_score >= beta:
            if force_reply == 1:
                return [[move], beta]
            else:
                return beta
        if cur_score > alpha and force_reply == 0:
            # reset alpha if this isn't a forced reply (top of tree)
            alpha = cur_score
        if force_reply == 1 and cur_score >= alpha:
            if cur_score > alpha:
                # score is higher, empty out the current moves
                print("Score is higher, emptying list")
                best_move.clear()
            alpha = cur_score
            best_move.append(copy.deepcopy(move))
    if force_reply == 1:
        return [best_move, alpha]
    else:
        return alpha


def minimize(depth, board_state, prev_move, alpha, beta):
    """
    Minimizes nodes in the depth level for the player to minimize our score
    Implements alpha beta pruning

    pre_move defines the move that was made in the upper depth level, this is done to mimic the simultaneous nature of Apocalypse
    We put simultaneous moves together in the minimizer (solves the simultaneous problem)

    board_state is a list in the following structure (board (1D list), penalty points (1D List))
    """
    alpha = copy.copy(alpha)
    beta = copy.copy(beta)
    board_copy = copy.deepcopy(board_state)
    if depth == 0:
        # put together the move with the board and send back the score evaluation
        board_copy = combine_single_move(board_copy, prev_move[0], prev_move[1], prev_move[2], prev_move[3])
        return -ai_score(board_copy)

    # generate all possible moves
    moves = possible_moves(board_copy, 1)
    for move in moves:
        # go through the move apply it to a new copy of the board state
        move_board = copy.deepcopy(board_copy)
        move_board = combine_moves(move_board, move[0], move[1], move[2], move[3], prev_move[0], prev_move[1], prev_move[2], prev_move[3])
        cur_score = maximize(depth - 1, move_board, alpha, beta)
        if cur_score <= alpha:
            return alpha
        if cur_score < beta:
            beta = cur_score
    return beta


def possible_moves(board_state, player_type):
    """
    Generates possible AI moves given a board state
    """
    possible_moves = []
    knight_moves = [[1, 2], [2, 1], [2, -1], [1, -2], [-1, -2], [-2, -1], [-2, 1], [-1, 2]]
    for x in range(5):
        for y in range(5):
            piece_type = board_state[x][y]
            # check whether the AI owns this piece
            if (piece_type == "K" and player_type == 0) or (piece_type == "k" and player_type == 1):

                for move in knight_moves:
                    if 0 <= (x + move[0]) < 5 and 0 <= (y + move[1]) < 5:
                        # it is inside the board
                        if player_type == 0:
                            if board_state[x+move[0]][y+move[1]] != "P" and board_state[x+move[0]][y+move[1]] != "K":
                                # valid AI move for the knight, return it
                                possible_moves.append([x, y, (x+move[0]), (y+move[1])])
                        else:
                            if board_state[x+move[0]][y+move[1]] != "p" and board_state[x+move[0]][y+move[1]] != "k":
                                # valid AI move for the knight, return it
                                possible_moves.append([x, y, (x+move[0]), (y+move[1])])

            elif (piece_type == "P" and player_type == 0) or (piece_type == "p" and player_type == 1):

                # offset of rows is down for the AI
                if piece_type == "P":
                    offset_val = x + 1
                else:
                    offset_val = x - 1

                # boolean defining whether the pawn is redeploying or not
                #print("Knight Amount for",player_type,knight_amount(board_state, player_type))
                movement_upgrade = ((player_type == 0 and offset_val != 4) or (player_type == 1 and offset_val != 0)) or ((knight_amount(board_state, player_type) < 2) and ((player_type == 0 and offset_val == 4) or (player_type == 1 and offset_val == 0)))
                #print("Movement Upgrade for " + str(player_type) + " is " + str(movement_upgrade))
                valid_move_val = False
                # check going diagonally right
                if 0 <= offset_val < 5 and 0 <= (y + 1) < 5:
                    # it is within the constraints of the board, check whether there is an enemy there
                    if player_type == 0:
                        if board_state[offset_val][(y + 1)] == "k" or board_state[offset_val][(y + 1)] == "p":
                            if movement_upgrade:
                                possible_moves.append([x, y, offset_val, (y + 1)])
                            else:
                                valid_move_val = True
                    else:
                        if board_state[offset_val][(y + 1)] == "K" or board_state[offset_val][(y + 1)] == "P":
                            if movement_upgrade:
                                possible_moves.append([x, y, offset_val, (y + 1)])
                            else:
                                valid_move_val = True
                if 0 <= offset_val < 5 and 0 <= (y - 1) < 5:
                    # it is within the constraints of the board, check whether there is an enemy there
                    if player_type == 0:
                        if board_state[offset_val][(y - 1)] == "k" or board_state[offset_val][(y - 1)] == "p":
                            if movement_upgrade:
                                possible_moves.append([x, y, offset_val, (y - 1)])
                            else:
                                valid_move_val = True
                    else:
                        if board_state[offset_val][(y - 1)] == "K" or board_state[offset_val][(y - 1)] == "P":
                            if movement_upgrade:
                                possible_moves.append([x, y, offset_val, (y - 1)])
                            else:
                                valid_move_val = True
                if 0 <= offset_val < 5:
                    # check whether it is going forward
                    # check whether forward is whitespace or not
                    if board_state[offset_val][y] == "W":
                        if movement_upgrade:
                            possible_moves.append([x, y, offset_val, y])
                        else:
                            valid_move_val = True
                if not movement_upgrade and valid_move_val == True:
                    # pawn reached last rank and they have 2 knights already
                    # allow them to redeploy, generate possible moves
                    for tempx in range(5):
                        for tempy in range(5):
                            temp_piece_type = board_state[tempx][tempy]
                            if temp_piece_type == "W":
                                # this is a possibility
                                possible_moves.append([x, y, tempx, tempy])
    return possible_moves


def delete_piece(x, y, board_turtles):
    """
    This function will remove a board piece, and do the proper logic to remove the current location of it
    """

    # get the turtle at x, y
    cur_turtle = board_turtles[y][x]

    # set the state of the board at that location to W
    set_piece(y, x, "W")

    # clear any symbols in that location
    cur_turtle.clear()


def get_piece(row, column):
    # gets the piece from the board at the specified coord
    string_array = board

    return string_array[row][column]


def set_piece(row, column, new_val):
    """
    Sets a value to the game state

    :param row: **int** row of the piece to set
    :param column: **int** column of the piece to set
    :param new_val: **string** value of the piece (ex. K, k, W, P, p)
    :return:
    """
    # sets the given piece to a new value
    global board

    board[row][column] = new_val


def game_over():
    """
    Checks the global game state as to whether the game is over or not and returns a value defining the state

    :return: **int** returns a value based upon the current state (0 = player won, 1 = ai won, 2 = stalemate, 3 = not game over)
    """
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

    # Check how many pawns each has, if they are all gone, they lose
    for row in board:
        for column in row:
            if column == "P":
                ai_pieces += 1
            elif column == "p":
                player_pieces += 1
    if ai_pieces == 0 and player_pieces == 0:
        return 2
    elif ai_pieces == 0:
        return 1
    elif player_pieces == 0:
        return 0
    else:
        return 3


def penalty_add(player):
    """
    Adds a penalty point to the player specified

    :param player: **string** letter defining the user (p for player, a for ai)
    :return:
    """

    if player == "p":
        penalty_index = 0 #Define player as index 0
    else:
        penalty_index = 1 #Define player as index 1

    # add one to the penalty, and return the new board
    cur_val = int(penalty_points[penalty_index])
    cur_val += 1
    penalty_points[penalty_index] = cur_val

    penaltyCount()

    return board


def displayMove(x, y, new_x, new_y):
    """
    Displays a given move in the queue messages

    :param x: **int** x coord of old piece position
    :param y: **int** y coord of old piece position
    :param new_x: **int** x coord of the new piece position
    :param new_y: **int** y coord of the new piece position
    :return:
    """
    to_write = str(y+1) + ", " + str(x+1) + " to " + str(new_y+1) + ", " + str(new_x+1)
    message_queue(to_write)


def message_queue(to_write):
    """
    Writes any defined string to the message queue on the right of the board

    :param to_write: **string** Message to write in the queue
    :return:
    """
    global moveOffset
    MessagesTurtle.up()

    # reset the messages if it goes beyond the height of board dimension
    if moveOffset < -(BOARD_DIMENSION/3.5):
        moveOffset = saved_offset
        MessagesTurtle.clear()

    moveOffset -= int(BOARD_DIMENSION/40) * 1.25
    MessagesTurtle._tracer(False)
    MessagesTurtle.color("grey")

    MessagesTurtle.goto(BOARD_DIMENSION/2 - screen.window_width() * 0.08, moveOffset)
    MessagesTurtle.write(to_write, move=True, align="left", font=("Ariel", int(BOARD_DIMENSION/40)))
    moveOffset = MessagesTurtle.ycor()


def penaltyCount():
    """
    Draws out the penalty points display on the right of the board

    :return:
    """
    # height of the text
    PenaltyTurtle.up()
    PenaltyTurtle.clear()

    PenaltyTurtle.color("grey")

    if platform.system() == "Windows":
        #button_turtle.setpos(x, y - (init_y/1.4))
        PenaltyTurtle.setpos(BOARD_DIMENSION/2 - screen.window_width() * 0.08, BOARD_DIMENSION/2 - (penalty_text_height/0.8))
    else:
        #button_turtle.setpos(x, y - (init_y/1.65))
        PenaltyTurtle.setpos(BOARD_DIMENSION/2 - screen.window_width() * 0.08, BOARD_DIMENSION/2 - (penalty_text_height/1))


    PenaltyTurtle.write("Penalty Points:", False, align="left", font=("Ariel", penalty_text_height))

    if platform.system() == "Windows":
        #button_turtle.setpos(x, y - (init_y/1.4))
        PenaltyTurtle.setpos(BOARD_DIMENSION/2 - screen.window_width() * 0.08, BOARD_DIMENSION/2 - (text_height/0.8))
    else:
        #button_turtle.setpos(x, y - (init_y/1.65))
        PenaltyTurtle.setpos(BOARD_DIMENSION/2 - screen.window_width() * 0.08, BOARD_DIMENSION/2 - (text_height/1))


    PenaltyTurtle.sety(PenaltyTurtle.ycor() - (penalty_text_height * 1.5))

    PenaltyTurtle.color("grey")
    PenaltyTurtle._tracer(False)

    # save coords to write out the numbers along with centered strings that define AI or Player
    # write out the player penalty amount and string
    saved_y = PenaltyTurtle.ycor()
    PenaltyTurtle.setx(BOARD_DIMENSION/2 - screen.window_width() * 0.08)
    text_width = PenaltyTurtle.xcor()
    PenaltyTurtle.write(penalty_points[0], move=True, align="left", font=("Ariel", text_height))
    text_width = PenaltyTurtle.xcor() - text_width
    saved_x = PenaltyTurtle.xcor()
    PenaltyTurtle.setx(saved_x - text_width/2)
    PenaltyTurtle.write("Player", False, align="center", font=("Ariel", penalty_text_height))
    PenaltyTurtle.setpos(saved_x, saved_y)


    # write out the ai penalty amount and string
    PenaltyTurtle.setx(PenaltyTurtle.xcor() + screen.window_width() * 0.03)
    text_width = PenaltyTurtle.xcor()
    PenaltyTurtle.write(penalty_points[1], move=True, align="left", font=("Ariel", text_height))
    text_width = PenaltyTurtle.xcor() - text_width
    saved_x = PenaltyTurtle.xcor()
    PenaltyTurtle.setx(saved_x - text_width/2)
    PenaltyTurtle.write("AI", move=False, align="center", font=("Ariel", penalty_text_height))


def load_state():
    """
    Loads a saved game state and overwrites the global variables defining it. Then it draws out the new game state to
    allow the player to continue playing

    :return:
    """
    try:
        global penalty_points, board, moveOffset
        file_obj = open("saved_board.apoc", "r")

        penalty_line = file_obj.readline().split(" ")
        penalty_points = [int(penalty_line[0]), int(penalty_line[1])]
        board_new_data = []
        for line in file_obj:
            split_data = line.replace("\n", "").split(" ")
            board_new_data.append(split_data)
        board = board_new_data

        # now we need to clear the screen and set the colour of it
        screen.clear()
        screen.bgcolor("#4A4A4A")

        # draw out the board and penalty system
        draw_board()
        penaltyCount()

        # bind the event handlers again
        screen.onclick(onclick_board_handler)
        screen.onkeyrelease(save_state, "s")
        screen.onkeyrelease(load_state, "l")

        screen.listen()

        # reset messages offset location
        moveOffset = BOARD_DIMENSION/2 - (text_height/0.7) - (penalty_text_height * 1.5)
        message_queue("Loaded Board")
        file_obj.close()
    except:
        print("There was an error loading the board")
        message_queue("Error Loading")


def save_state():
    """
    Saves the global game state of the board and penalty points to a file

    :return:
    """
    # we don't want to let them save while a pawn is redeploying (can cause game mechanics issues)
    if highlight_params[3] == False:
        try:
            file_obj = open("saved_board.apoc", "w")
            # the file is just a single line defining the state
            line_to_write = str(penalty_points[0]) + " " + str(penalty_points[1])
            for line in board:
                line_to_write += "\n" + " ".join(line)
            file_obj.write(line_to_write)
            message_queue("Saved Board")
            file_obj.close()
        except:
            print("There was an error saving the board")
            message_queue("Error Saving")


def knight_amount(board_state, player):
    """
    Returns the amount knights a player has

    :param board_state: multidimensional list defining the game state
    :param player: **numeric** integer defining player
    :return: **numeric** how many knights the player owns on that game state
    """
    board = board_state
    knight_amt = 0
    for row in board:
        for column in row:
            if player == 1 and column == "k":
                knight_amt += 1
            elif player == 0 and column == "K":
                knight_amt += 1
    return knight_amt


def onclick_board_handler(x, y):
    """
    Handles click events on the board and figures out how to deal with the game state

    :param x: **numeric** x coord of the screen click
    :param y: **numeric** y coord of the sreen click
    :return:
    """
    global board
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

                        if box_selected == 1  and highlight_params[3] == False:
                            # move the piece, a move was made

                            # we don't want to let them click again while the AI move is being generated
                            screen.onclick(None)
                            # generate the AI move
                            print("GENERATING MINIMAX AI MOVE")
                            generated_ai = maximize(depth_amt, copy.deepcopy(board), -float("inf"), float("inf"), 1)

                            # if all the combinations are -inf and the depth level is very high, try to reduce the depth level and prolong the game
                            if generated_ai[1] == float("-infinity") and depth_amt >= 5:
                                print("Regenerating move with lower depth level since the AI thinks it will always die")
                                generated_ai = maximize(3, copy.deepcopy(board), -float("inf"), float("inf"), 1)
                            ai_val = generated_ai[0]
                            print("AI MOVES: " + str(ai_val))
                            if len(ai_val) == 1:
                                ai_val = ai_val[0]
                            elif len(ai_val) > 1:
                                # there are multiple choices with the same score value that was calculated
                                # check the immediate best move based upon score
                                # if the player makes a deviation from their perfect possible move set, then the Ai will be at an advantage
                                best_immediate_score = float("-infinity")
                                best_immediate_move = ai_val[0]
                                for aimove in ai_val:
                                    # make the move
                                    board_copy = copy.deepcopy(board)
                                    board_copy = combine_single_move(board_copy, aimove[0], aimove[1], aimove[2], aimove[3])
                                    cur_score = ai_score(board_copy)
                                    print("Score of " + str(cur_score))
                                    if cur_score > best_immediate_score:
                                        print("Resetting value")
                                        best_immediate_move = aimove
                                        best_immediate_score = cur_score
                                ai_val = best_immediate_move
                                print("Best Immediate Score: " + str(best_immediate_score))
                            print("==============\n\nAI Results:\nMove: " + str(ai_val))
                            print(generated_ai)
                            if len(ai_val) > 0:
                                ai_type_val = get_piece(ai_val[0], ai_val[1])
                            else:
                                print("FALSE AI MOVE==============================")
                                # the ai knows that there is no way they win if the player makes their best moves, still try to
                                # we should check
                                possible_ai_moves = possible_moves(board, 0)

                                if len(possible_ai_moves) > 1:
                                    # there is still a random move it can make to remedy the situation, try it out
                                    # if the opponent doesn't make their best moves, it can still win
                                    ai_val = possible_ai_moves[1]
                                    ai_type_val = get_piece(ai_val[0], ai_val[1])
                                else:
                                    # there are no moves it can make
                                    ai_val = False
                            print("DONE GENERATING MINIMAX AI MOVE")

                            player_validity = valid_move((highlight_params[2] - 1), (highlight_params[1] - 1), (row - 1), (column - 1), "p")
                            player_type_val = get_piece((highlight_params[2] - 1), (highlight_params[1] - 1))
                            print(player_validity)

                            # check whether to upgrade the pawn to knight for the AI
                            if ai_val != False and ai_type_val == "P" and ai_val[2] == 4 and knight_amount(board, 0) < 2:
                                print("Upgraded AI pawn to knight")
                                board[ai_val[0]][ai_val[1]] = "K"

                            if ai_val != False and player_validity == True:
                                # both made valid moves, we'll process them
                                move_piece((highlight_params[1] - 1), (highlight_params[2] - 1), (column - 1), (row - 1), ai_val[1], ai_val[0], ai_val[3], ai_val[2])
                            elif ai_val == False and player_validity == False:
                                print("AI and Player Penalty")
                                message_queue("Player Penalty")
                                message_queue("AI Penalty")
                                board = penalty_add("a")
                                board = penalty_add("p")
                            elif ai_val == False:
                                # give the ai a penalty, and process the move
                                print("AI Penalty")
                                message_queue("AI Penalty")
                                board = penalty_add("a")
                                move_piece((highlight_params[1] - 1), (highlight_params[2] - 1), (column - 1), (row - 1), -1, 0, 0, 0)
                            elif player_validity == False:
                                print("Player Penalty")
                                message_queue("Player Penalty")
                                board = penalty_add("p")
                                move_piece(-1, 0, 0, 0, ai_val[1], ai_val[0], ai_val[3], ai_val[2])


                            print("Row",row,"Column",column)
                            print("Pawn Type:",player_type_val)
                            # rebind the onscreenclick since the user cannot click fast enough now to influence the game
                            screen.onclick(onclick_board_handler)

                            # check whether a player has moved to the end row with a pawn
                            if player_type_val == "p" and (row - 1) == 0 and player_validity == True:
                                print("Player pawn got to the last rank, checking how many knights they have")
                                if knight_amount(board, 1) >= 2:
                                    print("Allowing them to redeploy pawn, disabling saving")

                                    screen.onkeyrelease(None, "s")
                                    screen.onkeyrelease(None, "l")

                                    highlight_params[3] = True
                                    highlight_params[1] = column
                                    highlight_params[2] = row
                                    box_selected = 0

                                    redeploy_turtle = turtle.Turtle()

                                    highlight_params[4] = redeploy_turtle
                                    redeploy_turtle._tracer(False)
                                    redeploy_turtle.hideturtle()
                                    redeploy_turtle.color("#FF9500")

                                    redeploy_turtle.up()
                                    redeploy_turtle.goto(i[0], i[1])
                                    redeploy_turtle.down()
                                    for i2 in range(4):
                                        redeploy_turtle.forward(BOARD_DIMENSION/5)
                                        redeploy_turtle.right(90)
                                    redeploy_turtle.up()
                                    message_queue("Redeploy Pawn to")
                                    message_queue("a Vacant Square")
                                else:
                                    print("Changing piece to a knight")
                                    execute_move((highlight_params[1] - 1), (highlight_params[2] - 1), column - 1, row - 1, "♘", "k", False)
                                    #set_piece(board, (highlight_params[2] - 1), (highlight_params[1] - 1), "K")
                                    box_selected = 0
                                    highlight_params[0] = 0
                                    highlight_params[1] = 0
                                    highlight_params[2] = 0
                            else:
                                box_selected = 0
                                highlight_params[0] = 0
                                highlight_params[1] = 0
                                highlight_params[2] = 0

                            # check the game state, see whether someone won or not
                            # maybe we should game the screen to reflect this???
                            game_state = game_over()
                            if game_state != 3:
                                game_end_screen(game_state)

                            print_board()

                            #print("Possible AI Moves: " + str(possible_moves(board, 0)))
                            #print("Possible Player Moves: " + str(possible_moves(board, 1)))
                            #print("AI Score: " + str(ai_score(board)))

                        elif highlight_params[3] == True and get_piece(row - 1, column - 1) == "W":
                            print("The user wants to redeploy the pawn, making the move")
                            print(highlight_params)
                            execute_move((highlight_params[1] - 1), (highlight_params[2] - 1), (column - 1), (row - 1), "♙", "p", True)
                            highlight_params[4].clear()
                            highlight_params[0] = 0
                            highlight_params[1] = 0
                            highlight_params[2] = 0
                            highlight_params[3] = False
                            # rebind the saving and loading
                            screen.onkeyrelease(save_state, "s")
                            screen.onkeyrelease(load_state, "l")
                        elif (get_piece(row - 1, column - 1) == "k" or get_piece(row - 1, column - 1) == "p") and highlight_params[3] == False:
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
                        if highlight_params[3] == False:
                            print("deselected same box")
                            highlight_params[0] = 0
                            highlight_params[1] = 0
                            highlight_params[2] = 0
                            box_selected = 0
                        else:
                            print("You must redeploy to whitespace")

            column = 0
    else:
        for i in buttons:
            if (i[0] + i[2]) > x > i[0] and i[1] > y > (i[1] - i[3]):
                exec(i[5])


def game_end_screen(winner):
    """
    Clears the screen and draws out the end game screen as to who won

    :param winner: **numeric** integer that defines who won (0 for AI, 1 for Player, 3 for Stalemate)
    :return:
    """

    screen.clear()

    # clear any other buttons and rebind the handler
    global buttons
    del buttons[:]
    screen.onclick(button_event)

    screen.bgcolor("#4A4A4A")

    if winner == 0:
        text_write = "AI Won!"
    elif winner == 1:
        text_write = "Player Won!"
    elif winner == 2:
        text_write = "Stalemate!"

    # configure a turtle and write out who won
    end_screen_turtle = turtle.Turtle()
    end_screen_turtle.hideturtle()
    end_screen_turtle.color("white")
    end_screen_turtle._tracer(False)

    # the font size is just a relative static value to make sure it is proportionate to the screen dimensions
    end_screen_turtle.write(text_write, move=False, align="center", font=("Arial", int(BOARD_DIMENSION/8)))

    # draw out the main menu button
    draw_button(0, -(screen.window_height()/20), "Main Menu", 'draw_main_screen()', scaling_value/3.5)
    print(buttons)


def draw_button(x, y, text, code_exec, width=0, font_size=scaling_value/25):
    """
    Draws a button centered at the specified x, y point with the text passed in as a parameter and also handles
    configuring the click events for it

    :param x: **numeric** x coord of the center of the button
    :param y: **numeric** y coord of the center of the button
    :param text: **string** desired button text
    :param code_exec: **string** function or code to execute when the button is clicked
    :param width: optional **numeric** overwrites the default padding width with a specified width of the button
    :return:
    """

    # Find the width of the text (finding the height is not possible)
    width_turtle = turtle.Turtle()
    width_turtle.hideturtle()
    width_turtle._tracer(False)
    init_x = width_turtle.xcor()

    # set default text font size
    init_y = int(font_size)

    width_turtle.write(text, move=True, align="left", font=("Ariel", init_y))
    width_turtle.clear()
    text_width = width_turtle.xcor() - init_x

    # Create the proper box size dimensions depending on whether the user has overwritten them
    if width == 0:
        width_val = text_width + text_width * 0.15
    else:
        width_val = width
    height_val = init_y + init_y * 0.6


    print("Drawing button with text " + text)

    # draw out the background white box around the text
    button_turtle = turtle.Turtle()
    button_turtle.hideturtle()
    button_turtle.up()

    button_turtle.color("white")
    button_turtle._tracer(False)
    button_turtle.setpos(x - (width_val/2), y + (height_val/2))
    button_turtle.down()

    button_turtle.begin_fill()
    for i in range(4):
        if i % 2 == 0:
            # even num
            button_turtle.forward(width_val)
        else:
            button_turtle.forward(height_val)
        button_turtle.right(90)

    button_turtle.end_fill()
    button_turtle.up()
    button_turtle.color("black")

    # Windows and Unix based systems have different font heights and scaling
    if platform.system() == "Windows":
        button_turtle.setpos(x, y - (init_y/1.4))
    else:
        button_turtle.setpos(x, y - (init_y/1.65))

    # write out the text in the center of the button
    button_turtle.write(text, align="center", font=("Ariel", init_y))

    # append the attributes of the button to the list "buttons" for the event handler
    buttons.append([(x - width_val/2), (y + height_val/2), width_val, height_val, text, code_exec])


def button_event(x, y):
    """
    Handles user click events on screens that have buttons

    :param x: **numeric** The x coordinate of a user's click
    :param y: **numeric** The y coordinate of a user's click
    :return:
    """

    for i in buttons:
        if (i[0] + i[2]) > x > i[0] and i[1] > y > (i[1] - i[3]):
            exec(i[5])


def draw_main_bg():
    """
    Draws the checkerboard pattern onto the screen as a background for the main menu

    :return:
    """

    # create the turtle that draws the checkerboard bg pattern and configure its settings
    bg_turtle = turtle.Turtle()
    bg_turtle.color("#5E5E5E")
    bg_turtle.up()
    bg_turtle.hideturtle()

    # remove animations
    bg_turtle._tracer(False)

    # define the size of each box
    box_height = screen.window_height() / 5
    box_width = screen.window_width() / 5

    # set the turtle to the top left corner of the screen
    bg_turtle.setpos(-(screen.window_width()/2), (screen.window_height()/2))

    # iterate and draw out the checkerboard pattern
    for row in range(0, 5):
        for column in range(0, 5):
            if row % 2 == 0:
                # even case
                if column % 2 != 0:
                    # print out a block
                    bg_turtle.begin_fill()
                    for i in range(4):
                        if i % 2 == 0:
                            bg_turtle.forward(box_width)
                        else:
                            bg_turtle.forward(box_height)
                        bg_turtle.right(90)
                    bg_turtle.end_fill()
            else:
                if column % 2 == 0:
                    bg_turtle.begin_fill()
                    for i in range(4):
                        if i % 2 == 0:
                            bg_turtle.forward(box_width)
                        else:
                            bg_turtle.forward(box_height)
                        bg_turtle.right(90)
                    bg_turtle.end_fill()
            bg_turtle.setx(bg_turtle.xcor() + box_width)
        # reset position each time a row is done
        bg_turtle.setpos(-(screen.window_width()/2), (bg_turtle.ycor() - box_height))


def draw_main_screen():
    """
    Draws the main menu screen with created turtles and applies the proper event bindings for the buttons

    :return:
    """
    global buttons
    del buttons[:]
    screen.clear()
    screen.onclick(None)
    screen.onclick(button_event)
    screen.bgcolor("#4A4A4A")
    screen.title("Apocalypse")

    # draw the checkered background
    draw_main_bg()

    # initialize a turtle to draw the main screen text
    main_menu_turtle = turtle.Turtle()
    main_menu_turtle.hideturtle()
    main_menu_turtle.up()
    main_menu_turtle.color("white")
    main_menu_turtle._tracer(False)

    main_menu_turtle.sety(screen.window_height()/5)
    main_menu_turtle.write("Apocalypse", True, align="center", font=("Ariel", int(scaling_value/8)))
    main_menu_turtle.home()
    main_menu_turtle.write("♘ ♙ ♞ ♟", True, align="center", font=("Ariel", int(scaling_value/10)))
    main_menu_turtle.setposition((screen.window_width() / 2), -((screen.window_height() / 2) - 10))


    draw_button(0, -(screen.window_height()/20), "New Game", 'choose_difficulty()', screen.window_width()/3.5)
    draw_button(0, -(screen.window_height()/7), "Load Game", 'load_state()', screen.window_width()/3.5)


def main_menu():
    """
    Main function call, immediately draws the main menu screen

    :return:
    """

    # print out the "Apocalypse" text into the console (not needed, but a nice commemoration of our roots)
    print("""
       (                         (
       )\                      ) )\(             (
    ((((_)(  `  )  (    (  ( /(((_)\ ) `  )  (   ))\\
     )\ _ )\ /(/(  )\   )\ )(_) )_(()/( /(/(  )\ /((_)
     (_)_\(_|(_)_\((_) ((_| (_)_| |(_)|(_)_\((__|__))
      / _ \ | '_ \) _ \/ _|/ _` | | || | '_ \|_-< -_)
     /_/ \_\| .__/\___/\__|\__,_|_|\_, | .__//__|___|
            |_|                    |__/|_|
        """)

    draw_main_screen()
    turtle.done()


def new_game():
    """
    Starts a new game, draws the board, and binds event handlers

    :return:
    """
    global buttons
    del buttons[:]
    screen.clear()
    screen.bgcolor("#4A4A4A")

    # reset the game state and draw it out
    reset_game_state()
    draw_board()
    penaltyCount()

    # bind the event handler
    screen.onclick(onclick_board_handler)
    screen.onkeyrelease(save_state, "s")
    screen.onkeyrelease(load_state, "l")
    screen.listen()


def reset_game_state():
    """
    Resets the game state for a new game, rewrites variables

    :return:
    """
    global board, penalty_points
    board = [["K", "P", "P", "P", "K"],
        ["P", "W", "W", "W", "P"],
        ["W", "W", "W", "W", "W"],
        ["p", "W", "W", "W", "p"],
        ["k", "p", "p", "p", "k"]]

    penalty_points = [0, 0]


def choose_difficulty():
    """
    Clears and draws the difficulty screen

    :return:
    """
    global buttons
    del buttons[:]
    screen.clear()
    screen.onclick(button_event)
    screen.bgcolor("#4A4A4A")

    main_turtle = turtle.Turtle()
    main_turtle.hideturtle()
    main_turtle.color("white")
    main_turtle._tracer(False)
    main_turtle.up()
    main_turtle.setpos(0, screen.window_height()/20)
    main_turtle.write("Difficulty", True, align="center", font=("Ariel", int(screen.window_width()/12)))
    draw_button(0, -(screen.window_height()/20), "Easy", 'modify_difficulty(1); new_game()', screen.window_width()/3)
    draw_button(0, -(screen.window_height()/7), "Medium", 'modify_difficulty(3); new_game()', screen.window_width()/3)
    draw_button(0, -(screen.window_height()/4.2), "Hard", 'modify_difficulty(6); new_game()', screen.window_width()/3)


def modify_difficulty(level):
    """
    Modifies a global to change the ai difficulty for future move calculations

    :param level: **numeric** Specifies the difficulty level (ai move depth)
    :return:
    """
    global depth_amt
    depth_amt = level


# call the main function
if __name__ == '__main__':
    main_menu()
