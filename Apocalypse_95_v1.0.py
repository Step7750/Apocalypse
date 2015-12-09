"""
CPSC 231 Group Project - Apocalypse 095

Play the game of Apocalypse! A simultaneous game based upon the principles of chess.


Rules:

The starting setup is as shown. Horsemen and footmen move and capture the same as knights and pawns in chess,
except footmen do not have a double-step option on their first move. For each turn, each player secretly writes
down his move, then the players simultaneously declare them. The following rules apply:

If they moved to the same square, a horseman captures a footman. Same-type pieces are both removed from the board.
If a capture was declared using a footman, but the piece to be captured moved from its square, the footman move still
stands. (The move converts to a diagonal step instead of a capture.)
If a declared move is illegal, the player incurs a penalty point.
A footman promotes to horseman when reaching the last rank, but only when the player has less than two horsemen.
Otherwise the player must redeploy the footman to any vacant square.

[Wikipedia - https://en.wikipedia.org/wiki/Apocalypse_(chess_variant)]


----------------------------------


The program functions are neatly divided into different sections to define different areas of the program.
There are classes for the board drawing, AI, and buttons

Created by: Stepan Fedorko-Bartos, Khesualdo Condori Barykin, Cameron Davies, Michael Shi


Features:
- Fully interactive GUI to play Apocalypse
- GUI that scales on any resolution
- Dark Theme Interface
- Main Menu Screen
- Saving and Loading game states
- Sounds that work on most platforms (Windows, Mac OSX)
- Classes to simplify code structure for the AI, board drawing, and buttons


AI:
- Advanced MiniMax AI w/ Fail Soft Alpha Beta Pruning (that handles the simultaneous nature of Apocalypse)
- Uses Recursion for the MiniMax AI
- Variable levels of AI difficulty (Can you beat it on hard?)
- Uses the "Killer Heuristic" to store moves that cause a beta cutoff and order them first when sorting
- Uses MVV ordering to speed up the AI and reduce the branching factor
- Uses Quiescence search on truncated terminal nodes to increase the overall evaluation of the AI and
  reduce the "Horizon Effect"

Sound Resources:
- In order to hear sounds, you must have mouseDeselect.wav in the same directory as this file


General Chess Documentation on the heuristics used: https://chessprogramming.wikispaces.com
Killer Heuristic: http://chessprogramming.wikispaces.com/Killer+Heuristic
Quiescence Search: https://chessprogramming.wikispaces.com/Quiescence+Search
MVV-LAA Ordering: https://chessprogramming.wikispaces.com/MVV-LVA


Easy - 1ply
Medium - 4ply
Hard - 6ply

All difficulty levels implement quiescence search to a variable depth, the killer heuristic, and alpha beta pruning
for the minimax AI


For sounds, since we can't use external libraries, we've decided to support Windows and Mac OSX using system sounds
"""

import turtle
import platform   # For display scaling and system configuration
import copy       # for deep copies (for the minimax ai)
import os

# libraries used for sounds in Windows
if platform.system() == "Windows":
    import winsound

# declare all of the global variables

board = [["K", "P", "P", "P", "K"],
        ["P", "W", "W", "W", "P"],
        ["W", "W", "W", "W", "W"],
        ["p", "W", "W", "W", "p"],
        ["k", "p", "p", "p", "k"]]

# penalty points for each player (player, ai)
penalty_points = [0, 0]

# default amount of moves the AI thinks forward (computation gets exponential)
# This changes based upon the difficulty selected
depth_amt = 6

# store the state of the highlighting of boxes (and their corresponding turtles)
highlight_params = [0, 0, 0, False, 0]
box_selected = 0

# stores objects of created buttons
buttons = []

# Stores the object of BoardDraw after the main function is executed
DrawingBoard = False


"""

Board Drawing Class

"""


class BoardDraw:
    """
    This class contains the necessary variables and functions for drawing things onto the screen

    When setting elements height, width, and position, many relative "scaling" values are used depending upon
    the OS configuration
    """

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

    screen = turtle.Screen()

    # for proper scaling with many dimensions, if the width is substantially more, go by the height of the screen
    BOARD_DIMENSION = screen.window_width()*0.75

    # dictionary that converts location num to a symbol
    SYMBOL_DICT = {"K": "♞", "P": "♟", "k": "♘", "p": "♙", "W": ""}

    # define dynamic scaling variable that stores whether to scale by height or width
    scaling_value = screen.window_width()

    # Colours for the GUI
    GREY = "#5E5E5E"
    DARK_GREY = "#4A4A4A"

    def __init__(self):
        """
        Creates the object and sets the corresponding turtle, screen and scaling values

        :return:
        """
        # Initiate the screen with bgcolor
        self.screen.bgcolor(self.DARK_GREY)
        self.screen.title("Apocalypse")


        # Initialize Turtles for the right message queue and penalties
        self.PenaltyTurtle = turtle.Turtle()
        self.PenaltyTurtle._tracer(False)
        self.PenaltyTurtle.hideturtle()
        self.PenaltyTurtle.color("grey")

        self.MessagesTurtle = turtle.Turtle()
        self.MessagesTurtle._tracer(False)
        self.MessagesTurtle.hideturtle()

        # for proper scaling for relative values, if the height is less than the width, go based off of that
        if self.screen.window_height() < self.screen.window_width():
            self.scaling_value = self.screen.window_height()

        # If there is a high ratio of width to height, make the board dimensions based upon the height
        if self.screen.window_width()/self.screen.window_height() > 1.20:
            # width of the board is equal to 95% of the screen height
            self.BOARD_DIMENSION = self.screen.window_height()*0.95

        # set the text height scalings based upon OS
        if platform.system() == "Linux":
            # stores text height for the queue messages
            self.TEXT_HEIGHT = int(self.BOARD_DIMENSION/8.5)
            # stores text height for strings related to the penalty score board
            self.PENALTY_TEXT_HEIGHT = int(self.BOARD_DIMENSION/50)
        else:
            self.TEXT_HEIGHT = int(self.BOARD_DIMENSION/7.5)
            self.PENALTY_TEXT_HEIGHT = int(self.BOARD_DIMENSION/45)
            
        # creates the move offset that is needed to increment by everytime a new message is printed
        # (creates extra var to save it)
        self.moveOffset = self.BOARD_DIMENSION/2 - (self.TEXT_HEIGHT/0.7) - (self.PENALTY_TEXT_HEIGHT * 1.5)
        self.SAVED_OFFSET = self.moveOffset

    def draw_main_screen(self):
        """
        Draws the main menu screen with created turtles and creates the main screen buttons

        :return:
        """
        delete_buttons()
        self.screen.clear()
        self.screen.onclick(None)
        self.screen.onclick(button_event)
        self.screen.bgcolor(self.DARK_GREY)
        self.screen.title("Apocalypse")

        # draw the checkered background
        self.draw_main_bg()

        # Initialize a turtle to draw the main screen text
        main_menu_turtle = create_default_turtle()

        # Draw the "Apocalypse" text and the little pieces according to scaling values of the board size
        main_menu_turtle.sety(self.screen.window_height()/5)
        main_menu_turtle.write("Apocalypse", True, align="center", font=("Ariel", int(self.scaling_value/8)))
        main_menu_turtle.home()
        main_menu_turtle.write("♘ ♙ ♞ ♟", True, align="center", font=("Ariel", int(self.scaling_value/10)))
        main_menu_turtle.setposition((self.screen.window_width() / 2), -((self.screen.window_height() / 2) - 10))

        # Create the main screen buttons
        Button(0, -(self.screen.window_height()/20), "New Game", 'DrawingBoard.choose_difficulty()',
               self.screen.window_width()/3)
        Button(0, -(self.screen.window_height()/7), "Load Game", 'load_state()', self.screen.window_width()/3)

    def draw_main_bg(self):
        """
        Draws the checkerboard pattern onto the screen as a background for the main menu

        :return:
        """

        # create the turtle that draws the checkerboard bg pattern and configure its settings
        bg_turtle = create_default_turtle(self.GREY)

        # define the size of each box, it won't necessarily be a square
        box_height = self.screen.window_height() / 5
        box_width = self.screen.window_width() / 5

        # set the turtle to the top left corner of the screen
        bg_turtle.setpos(-(self.screen.window_width()/2), (self.screen.window_height()/2))

        # iterate and draw out the checkerboard pattern
        for row in range(0, 5):
            for column in range(0, 5):
                if row % 2 == 0:
                    if column % 2 != 0:
                        # fill the block
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
                        # fill the block
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
            bg_turtle.setpos(-(self.screen.window_width()/2), (bg_turtle.ycor() - box_height))

    def draw_board(self):
        """
        This function will draw the game board onto the screen based upon the constants BOARD_DIMENSION and SYMBOL_DICT

        :return:
        """
        delete_buttons()

        X_COR = 0
        Y_COR = 1

        # reset the move offset based upon relative values
        self.moveOffset = self.BOARD_DIMENSION/2 - (self.TEXT_HEIGHT/0.7) - (self.PENALTY_TEXT_HEIGHT * 1.5)
        self.SAVED_OFFSET = self.moveOffset

        # Initiate turtle that will draw the board
        main_board = create_default_turtle(self.GREY)

        # Make the board 80% width and 10% to the left
        main_board.goto(-(self.BOARD_DIMENSION/2) - (self.screen.window_width()*0.1), self.BOARD_DIMENSION/2)

        # create outer rectangle of the board
        main_board.down()
        for i in range(4):
            main_board.forward(self.BOARD_DIMENSION)
            main_board.right(90)
        main_board.up()

        # move turtle back to top left of the board
        main_board.goto(-(self.BOARD_DIMENSION/2) - (self.screen.window_width()*0.1), self.BOARD_DIMENSION/2)

        # iterate through each box and draw it
        for row in range(0, 5):
            for column in range(0, 5):
                # store the top left of every box in the chess table for future reference and click events
                self.box_locations[row][column][X_COR] = main_board.xcor()
                self.box_locations[row][column][Y_COR] = main_board.ycor()

                # create checkerboard pattern

                # check if the row is 0, 2, 4
                if row % 2 == 0:
                    # Check whether there is an even column
                    if column % 2 == 0:
                        # print out a block
                        main_board.begin_fill()
                        for i in range(4):
                            main_board.forward(self.BOARD_DIMENSION/5)
                            main_board.right(90)
                        main_board.end_fill()
                else:
                    # row is 1, 3
                    # Check whether it is an odd column
                    if column % 2 != 0:
                        main_board.begin_fill()
                        for i in range(4):
                            main_board.forward(self.BOARD_DIMENSION/5)
                            main_board.right(90)
                        main_board.end_fill()

                # write out the characters (board pieces)
                # create new turtle just for the character, and store it in the array board_turtles
                char_turtle = create_default_turtle()
                char_turtle.setx(main_board.xcor() + (self.BOARD_DIMENSION/10))

                # get symbol from dict
                text_to_write = self.SYMBOL_DICT[get_piece(row, column)]

                # mac osx and windows have different symbol designs, with diff height/width
                # haven't tested on a Unix system other than Mac OSX, Linux may have a different character set

                if platform.system() == "Windows" or platform.system() == "Linux":
                    # adjust scaling of the y coord based upon the os
                    char_turtle.sety(main_board.ycor() - (self.BOARD_DIMENSION/4.10))
                    char_turtle.write(text_to_write, False, align="center", font=("Ariel",
                                                                                  int(self.BOARD_DIMENSION/5.4)))
                else:
                    # Mac OSX Scaling
                    char_turtle.sety(main_board.ycor() - (self.BOARD_DIMENSION/5))
                    char_turtle.write(text_to_write, False, align="center", font=("Ariel",
                                                                                  int(self.BOARD_DIMENSION/5)))

                # add turtle to the board so that the memory location is stored
                self.board_turtles[row][column] = char_turtle

                # move the turtle to the right for the distance of one block
                main_board.setx(main_board.xcor() + (self.BOARD_DIMENSION/5))

            # reset x position each time a row is done (to the very left), move the turtle down one block
            main_board.setpos(-(self.BOARD_DIMENSION/2) - (self.screen.window_width()*0.1), (main_board.ycor() -
                                                                                             (self.BOARD_DIMENSION/5)))

        # create buttons on the main board to perform various actions,
        # the offsets were calculated by eye and are relative
        Button(self.BOARD_DIMENSION/2 + (self.BOARD_DIMENSION/2 * 0.03), -self.BOARD_DIMENSION/2.13, "Load Game",
               'load_state()', self.screen.window_width()*0.20, self.scaling_value/36)
        Button(self.BOARD_DIMENSION/2 + (self.BOARD_DIMENSION/2 * 0.03), -self.BOARD_DIMENSION/2.50, "Save Game",
               'save_state()', self.screen.window_width()*0.20, self.scaling_value/36)
        Button(self.BOARD_DIMENSION/2 + (self.BOARD_DIMENSION/2 * 0.03), -self.BOARD_DIMENSION/3.02, "Main Menu",
               'DrawingBoard.draw_main_screen()', self.screen.window_width()*0.20, self.scaling_value/36)

    def penalty_count(self):
        """
        Draws out the penalty points display on the right of the board

        :return:
        """

        # Simplify variable references
        PenaltyTurtle = self.PenaltyTurtle
        PENALTY_TEXT_HEIGHT = self.PENALTY_TEXT_HEIGHT
        BOARD_DIMENSION = self.BOARD_DIMENSION
        TEXT_HEIGHT = self.TEXT_HEIGHT
        screen = self.screen
        AI = 1
        PLAYER = 0

        PenaltyTurtle.up()
        PenaltyTurtle.clear()

        # Font sizes differ on Windows and Unix Platforms, use different scaling for both to position the turtle
        text_height_modifier = 1
        if platform.system() == "Windows" or platform.system() == "Linux":
            text_height_modifier = 0.8

        # Set the position on the right edge of the board
        PenaltyTurtle.setpos(BOARD_DIMENSION/2 - screen.window_width() * 0.08, BOARD_DIMENSION/2 -
                             (PENALTY_TEXT_HEIGHT/text_height_modifier))

        PenaltyTurtle.write("Penalty Points:", False, align="left", font=("Ariel", PENALTY_TEXT_HEIGHT))

        # reset the position
        PenaltyTurtle.setpos(BOARD_DIMENSION/2 - screen.window_width() * 0.08, BOARD_DIMENSION/2 -
                             (TEXT_HEIGHT/text_height_modifier))

        PenaltyTurtle.sety(PenaltyTurtle.ycor() - (PENALTY_TEXT_HEIGHT * 1.5))


        # save coords to write out the numbers along with centered strings that define AI or Player
        # write out the player penalty amount and string
        saved_y = PenaltyTurtle.ycor()
        PenaltyTurtle.setx(BOARD_DIMENSION/2 - screen.window_width() * 0.08)
        text_width = PenaltyTurtle.xcor()

        PenaltyTurtle.write(penalty_points[PLAYER], move=True, align="left", font=("Ariel", TEXT_HEIGHT))

        # Set the coords of the turtle to write the centered "Player" text below the penalty score
        text_width = PenaltyTurtle.xcor() - text_width
        saved_x = PenaltyTurtle.xcor()
        PenaltyTurtle.setx(saved_x - text_width/2)

        PenaltyTurtle.write("Player", False, align="center", font=("Ariel", PENALTY_TEXT_HEIGHT))

        # Reset the coord position to the saved position
        PenaltyTurtle.setpos(saved_x, saved_y)


        # Set the x coord of the penalty turtle to the location for the AI, using relative offsets
        PenaltyTurtle.setx(PenaltyTurtle.xcor() + screen.window_width() * 0.03)
        text_width = PenaltyTurtle.xcor()

        PenaltyTurtle.write(penalty_points[AI], move=True, align="left", font=("Ariel", TEXT_HEIGHT))

        # Set the coords of the turtle to write the centered "AI" text below the penalty score
        text_width = PenaltyTurtle.xcor() - text_width
        saved_x = PenaltyTurtle.xcor()
        PenaltyTurtle.setx(saved_x - text_width/2)

        PenaltyTurtle.write("AI", move=False, align="center", font=("Ariel", PENALTY_TEXT_HEIGHT))

    def display_move(self, x, y, new_x, new_y, player):
        """
        Displays a given move in the queue messages

        :param x: **int** x coord of old piece position
        :param y: **int** y coord of old piece position
        :param new_x: **int** x coord of the new piece position
        :param new_y: **int** y coord of the new piece position
        :return:
        """
        to_write = player + ": " + str(y+1) + ", " + str(x+1) + " to " + str(new_y+1) + ", " + str(new_x+1)
        self.message_queue(to_write)

    def message_queue(self, to_write):
        """
        Writes any defined string to the message queue on the right of the board

        :param to_write: **string** Message to write in the queue
        :return:
        """
        self.MessagesTurtle.up()

        # reset the messages if it goes beyond the space height
        if self.moveOffset < -(self.BOARD_DIMENSION/4.5):
            self.moveOffset = self.SAVED_OFFSET
            self.MessagesTurtle.clear()

        # position the height to be lower for the new text
        self.moveOffset -= int(self.BOARD_DIMENSION/40) * 1.25

        self.MessagesTurtle._tracer(False)
        self.MessagesTurtle.color("grey")

        # go to the position to write out the text and write it
        self.MessagesTurtle.goto(self.BOARD_DIMENSION/2 - self.screen.window_width() * 0.08, self.moveOffset)
        self.MessagesTurtle.write(to_write, move=True, align="left", font=("Ariel", self.PENALTY_TEXT_HEIGHT))

        # overwrite the moveOffset with the new location
        self.moveOffset = self.MessagesTurtle.ycor()

    def game_end_screen(self, winner):
        """
        Clears the screen and draws out the end game screen as to who won

        :param winner: **numeric** integer that defines who won (0 for AI, 1 for Player, 3 for Stalemate)
        :return:
        """

        self.screen.clear()

        # clear any other buttons and rebind the handler
        delete_buttons()

        self.screen.onclick(button_event)

        self.screen.bgcolor(self.DARK_GREY)

        if winner == 1:
            text_write = "AI Won!"
        elif winner == 0:
            text_write = "You Won!"
        elif winner == 2:
            text_write = "Stalemate!"

        # configure a turtle and write out who won
        end_screen_turtle = create_default_turtle()

        # the font size is just a relative static value to make sure it is proportionate to the screen dimensions
        end_screen_turtle.write(text_write, move=False, align="center", font=("Arial", int(self.BOARD_DIMENSION/8)))

        # draw out the main menu button
        Button(0, -(self.screen.window_height()/20), "Main Menu", 'DrawingBoard.draw_main_screen()',
               self.scaling_value/3)

    def choose_difficulty(self):
        """
        Clears and draws the difficulty screen

        :return:
        """
        delete_buttons()

        self.screen.clear()
        self.screen.onclick(button_event)
        self.screen.bgcolor(self.DARK_GREY)

        # setup the turtle
        difficulty_turtle = create_default_turtle()

        # Center the turtle x and offset it a bit up
        difficulty_turtle.setpos(0, self.screen.window_height()/20)
        difficulty_turtle.write("Difficulty", True, align="center", font=("Ariel", int(self.screen.window_width()/12)))

        # Create the difficulty buttons
        Button(0, -(self.screen.window_height()/20), "Easy", 'modify_difficulty(1); DrawingBoard.new_game()',
               self.screen.window_width()/3)
        Button(0, -(self.screen.window_height()/7), "Medium", 'modify_difficulty(4); DrawingBoard.new_game()',
               self.screen.window_width()/3)
        Button(0, -(self.screen.window_height()/4.2), "Hard", 'modify_difficulty(6); DrawingBoard.new_game()',
               self.screen.window_width()/3)

    def new_game(self):
        """
        Starts a new game, draws the board, and binds event handlers

        :return:
        """
        delete_buttons()
        self.screen.clear()
        self.screen.bgcolor(self.DARK_GREY)

        # reset the game state and draw it out
        reset_game_state()
        reset_highlight_params()
        self.draw_board()
        self.penalty_count()

        # bind the event handler
        self.screen.onclick(onclick_board_handler)
        self.screen.onkeyrelease(save_state, "s")
        self.screen.onkeyrelease(load_state, "l")
        self.screen.listen()

    def select_tile(self, New_Highlight_Turtle, current_box, column, row):
        """
        Draws the blue selection box around a given box and does the corresponding board logic

        :param New_Highlight_Turtle: **Turtle Object** Turtle to draw the blue square with
        :param current_box: **list** List containing the x, y of the top left of the wanted box
        :param column: **int** Column of the box
        :param row: **int** Row of the box
        :return:
        """
        global box_selected, highlight_params

        LAST_CLICK_COLUMN = 1
        LAST_CLICK_ROW = 2
        X_COORD = 0
        Y_COORD = 1

        # only let the user select tiles it owns
        New_Highlight_Turtle.up()
        New_Highlight_Turtle.goto(current_box[X_COORD], current_box[Y_COORD])
        New_Highlight_Turtle.down()
        for i2 in range(4):
            New_Highlight_Turtle.forward(self.BOARD_DIMENSION/5)
            New_Highlight_Turtle.right(90)
        New_Highlight_Turtle.up()
        box_selected = 1

        # save x y coords from the turtle for future reference
        highlight_params[LAST_CLICK_COLUMN] = column
        highlight_params[LAST_CLICK_ROW] = row


"""

Button Class and Delete Function

"""


class Button:
    def __init__(self, x, y, text, code_exec, width=0, font_size=BoardDraw.scaling_value/25):
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
        self.font_size = int(font_size)
        self.function = code_exec
        self.x = x
        self.y = y
        self.width = width
        self.text = text

        text_width = self.text_width()
        if width == 0:
            self.width = text_width + text_width * 0.15

        self.height = font_size + (font_size * 0.6)

        print("Drawing button with text " + text)
        self.draw_button()

        self.top_left = (x - self.width/2)
        self.bottom = (y + self.height/2)

        # append the object of the button to the list "buttons" for the event handler
        buttons.append(self)

    def text_width(self):
        """
        Determines the text width of the specified text of the button

        :return:
        """
        width_turtle = create_default_turtle()

        init_x = width_turtle.xcor()

        width_turtle.write(self.text, move=True, align="left", font=("Ariel", self.font_size))
        width_turtle.clear()

        self.text_width = width_turtle.xcor() - init_x

        return self.text_width

    def draw_button(self):
        """
        Draws the button given the already set state

        :return:
        """
        # draw out the background white box around the text
        self.button_turtle = create_default_turtle()

        self.button_turtle.setpos(self.x - (self.width/2), self.y + (self.height/2))
        self.button_turtle.down()

        self.button_turtle.begin_fill()
        for i in range(4):
            if i % 2 == 0:
                # even num
                self.button_turtle.forward(self.width)
            else:
                self.button_turtle.forward(self.height)
            self.button_turtle.right(90)

        self.button_turtle.end_fill()
        self.button_turtle.up()
        self.button_turtle.color("black")

        # Windows and Unix based systems have different font heights and scaling
        if platform.system() == "Windows" or platform.system() == "Linux":
            self.button_turtle.setpos(self.x, self.y - (self.font_size/1.4))
        else:
            self.button_turtle.setpos(self.x, self.y - (self.font_size/1.65))

        # write out the text in the center of the button
        self.button_turtle.write(self.text, align="center", font=("Ariel", self.font_size))

    def check_clicked(self, x, y):
        """
        Given the x and y of a user's click, return a Bool as to whether the user clicked this button

        :param x: **numeric** The x coordinate of a user's click
        :param y: **numeric** The y coordinate of a user's click
        :return: **bool** True if the user clicked the button, False if not
        """
        if (self.top_left + self.width) > x > self.top_left and self.bottom > y > (self.bottom - self.height):
            return True
        else:
            return False

    def execute_function(self):
        """
        Execute the function this button holds when clicked
        """
        exec(self.function)


def delete_buttons():
    """
    Deletes all of the onclick data for all current buttons
    """
    global buttons
    del buttons[:]


"""

AI Class

"""


class AIMove:
    # set the score weighting for pawns and knights (for the AI)
    KNIGHT_WEIGHTING = 1
    PAWN_WEIGHTING = 1
    killermoves = {}

    def __init__(self, board_copy):
        """
        Sets initial parameters for the AI

        :param board_copy: **multi-dimensional list** Board State
        :return:
        """
        self.board = board_copy

    def findmove(self, depth):
        """
        Starts the minimax recursion sequence with the given depth and board state

        :param depth: **int** Depth of moves to think ahead
        :return: **multi-dimensional list** Defines the best possible move using minimax w/ alpha beta pruning
        """
        self.depth = depth
        return self.minimax_alphabeta(self.board, depth, True, float("-infinity"), float("infinity"), 0, True)

    def killer_heuristic(self, moves, current_depth):
        """
        Pure Function

        Checks whether there is a move that the current depth level that is in the saved beta cutoff moves
        If so, set higher priority for them

        :param moves: **multi-dimensional list** List of moves that are currently playable
        :param current_depth: **int** Current depth level
        :return:
        """
        return_list = []
        SCORE = 1
        CLEAN_MOVE = 0

        depth_lvl = self.depth - current_depth
        if depth_lvl in self.killermoves:
            for move_index in range(len(moves)):
                move = moves[move_index]
                if move[CLEAN_MOVE] in self.killermoves[depth_lvl]:
                    # This move was a previous beta cutoff, give it more weighting
                    move[SCORE] = 4
                return_list.append(move)
        else:
            return moves
        return return_list

    def quiescence(self, board_state, depth, MaxPlayer, alpha, beta, prev_move=0, top_tree=False, move_score=0):
        """
        Implements same algorithm as "minimax_alphabeta" but is only called when the main minimax tree calls this
        function when it encounters a terminal node that may induce the "Horizon Effect"

        This function will also return the evaluation of the node if the node is "quiet" (move score == 0)

        :param board_state: **multi-dimensional list** Board state
        :param depth: **int** Current depth of the recursive call
        :param MaxPlayer: **bool** Defines whether to minimize or maximize in the current recursive call
        :param alpha: **float** Current alpha value for pruning purposes
        :param beta: **float** Current beta value for pruning purposes
        :param prev_move: **multi-dimensional list** **optional** List defining the previous move
                                                                 (set if the last call was maximizing
        :param top_tree: **bool** **optional** True if the current node is at the top of the tree
        :param move_score: **int** **optional** Piece value of the current move
        :return: If its the terminal node, returns the score of the node
        """
        board_copy = copy.deepcopy(board_state)

        OLD_ROW = 0
        OLD_COLUMN = 1
        NEW_ROW = 2
        NEW_COLUMN = 3

        # This mimics simultaneous movements when checking a leaf node that doesn't involve the minimizing player
        if prev_move != 0:
            board_copy = self.combine_single_move(board_copy, prev_move[OLD_ROW], prev_move[OLD_COLUMN],
                                                  prev_move[NEW_ROW], prev_move[NEW_COLUMN])

        current_score = self.ai_score(board_copy)

        if current_score == float("-infinity") or current_score == float("infinity") \
                or current_score == 255 or depth == 0 or move_score == 0:
            # this is a leaf node, return the score
            return self.ai_score(board_copy)

        # Revert any changes that were done to calculate the AI score
        board_copy = copy.deepcopy(board_state)

        if MaxPlayer:
            best_val = float("-infinity")

            moves = self.possible_capture_moves(board_copy, 0)

            # Heuristic: Sort moves by ones that kill pieces first
            moves = sorted(moves, key=lambda x: x[1], reverse=True)

            for move in moves:
                clean_move = move[0]
                val = self.quiescence(board_copy, depth - 1, False, alpha, beta, clean_move, False, move[1])

                if val > best_val:
                    best_move = clean_move
                    if len(move) == 3:
                        # this contains values about the piece that died in this process
                        old_piece = move[2]

                best_val = max(best_val, val)
                alpha = max(best_val, alpha)

                if beta <= alpha:
                    # Beta cutoff, we don't want to use the killer heuristic here
                    break
            # This might be the top of the tree, if so, return the best move along with the value
            if top_tree:
                return [[best_move, old_piece], best_val]
            else:
                return best_val
        else:
            # min player
            best_val = float("infinity")
            moves = self.possible_capture_moves(board_copy, 1)

            # Heuristic: Sort moves by ones that kill pieces first
            moves = sorted(moves, key=lambda x: x[1], reverse=True)

            for move in moves:
                clean_move = move[0]
                move_board = copy.deepcopy(board_copy)

                # The minimizing player always combines moves simultaneously
                move_board = self.combine_moves(move_board, clean_move[OLD_ROW], clean_move[OLD_COLUMN],
                                                clean_move[NEW_ROW], clean_move[NEW_COLUMN], prev_move[OLD_ROW],
                                                prev_move[OLD_COLUMN], prev_move[NEW_ROW], prev_move[NEW_COLUMN])

                val = self.quiescence(move_board, depth - 1, True, alpha, beta, 0, False, move[1])

                best_val = min(best_val, val)
                beta = min(best_val, beta)

                if beta <= alpha:
                    break
            return best_val

    def minimax_alphabeta(self, board_state, depth, MaxPlayer, alpha, beta, prev_move=0, top_tree=False, move_score=0):
        """
        Implements the Minimax algorithm with fail soft alpha beta pruning for calculating AI decisions
        This function is recursively called and tries to mimic simultaneous movements

        :param board_state: **multi-dimensional list** Board state
        :param depth: **int** Current depth of the recursive call
        :param MaxPlayer: **bool** Defines whether to minimize or maximize in the current recursive call
        :param alpha: **float** Current alpha value for pruning purposes
        :param beta: **float** Current beta value for pruning purposes
        :param prev_move: **multi-dimensional list** **optional** List defining the previous move (set if the
                                                                  last call was maximizing)
        :param top_tree: **bool** **optional** True if the current node is at the top of the tree
        :param move_score: **int** **optional** Piece value of the current move
        :return: If its the terminal node, returns the score of the node
        """
        board_copy = copy.deepcopy(board_state)

        OLD_ROW = 0
        OLD_COLUMN = 1
        NEW_ROW = 2
        NEW_COLUMN = 3

        PLAYER = 1
        AI = 0

        # This mimics simultaneous movements when checking a leaf node that doesn't involve the minimizing player
        if prev_move != 0:
            board_copy = self.combine_single_move(board_copy, prev_move[OLD_ROW], prev_move[OLD_COLUMN],
                                                  prev_move[NEW_ROW], prev_move[NEW_COLUMN])

        current_score = self.ai_score(board_copy)
        if current_score == float("-infinity") or current_score == float("infinity") \
                or current_score == 255:
            # this is a leaf node, return the score
            return self.ai_score(board_copy)
        elif depth == 0:
            # this is a terminal node, check whether it is a quiescence node
            if move_score == 0:
                # Just return the value, don't expect it to cause much of a "horizon effect"
                return self.ai_score(board_copy)
            else:
                # Try quiescence search
                # Quiescence depth is dynamic
                pieces = self.pieces_amt(board_copy)
                if 6 < pieces <= 8:
                    quiescence_depth = 4
                elif pieces <= 6:
                    quiescence_depth = 5
                else:
                    quiescence_depth = 3
                return self.quiescence(board_state, quiescence_depth, MaxPlayer, alpha, beta,
                                       prev_move, False, move_score)


        # Revert any changes that were done to calculate the AI score
        board_copy = copy.deepcopy(board_state)

        if MaxPlayer:
            best_val = float("-infinity")

            moves = self.possible_moves(board_copy, AI)

            # Use killer heuristic
            moves = self.killer_heuristic(moves, depth)

            # Heuristic: Sort moves by ones that kill pieces first to reduce alpha beta constraints faster
            moves = sorted(moves, key=lambda x: x[1], reverse=True)

            # We want to store the best moves if this is the root of the tree
            if top_tree:
                best_move = []
                old_piece = []

            for move in moves:
                clean_move = move[0]
                val = self.minimax_alphabeta(board_copy, depth - 1, False, alpha, beta, clean_move, False, move[1])

                if val > best_val:
                    # Store this as the current best move

                    best_move = clean_move
                    if len(move) == 3:
                        # this contains values about the piece that died in this process
                        old_piece = move[2]

                best_val = max(best_val, val)
                alpha = max(best_val, alpha)

                if beta <= alpha:
                    # Beta cut off
                    # Append to killer values
                    current_depth_lvl = self.depth - depth

                    if current_depth_lvl not in self.killermoves:
                        self.killermoves[current_depth_lvl] = []
                    self.killermoves[current_depth_lvl].append(clean_move)

                    break
            # This might be the top of the tree, if so, return the best move along with the value
            if top_tree:
                print("Possible Capture Moves: " + str(self.possible_capture_moves(board_copy, 0)))
                return [[best_move, old_piece], best_val]
            else:
                return best_val
        else:
            # min player
            best_val = float("infinity")
            moves = self.possible_moves(board_copy, PLAYER)

            # Heuristic: Sort moves by ones that kill pieces first to reduce alpha beta constraints faster
            moves = sorted(moves, key=lambda x: x[1], reverse=True)

            for move in moves:
                clean_move = move[0]
                move_board = copy.deepcopy(board_copy)

                # The minimizing player always combines moves simultaneously
                move_board = self.combine_moves(move_board, clean_move[OLD_ROW], clean_move[OLD_COLUMN],
                                                clean_move[NEW_ROW], clean_move[NEW_COLUMN], prev_move[OLD_ROW],
                                                prev_move[OLD_COLUMN], prev_move[NEW_ROW], prev_move[NEW_COLUMN])

                val = self.minimax_alphabeta(move_board, depth - 1, True, alpha, beta, 0, False, move[1])

                best_val = min(best_val, val)
                beta = min(best_val, beta)

                if beta <= alpha:
                    break
            return best_val

    def possible_moves(self, board_state, player_type):
        """
        Generates possible moves for player_type on the given board_state

        :param board_state: **multi-dimensional list** Represents the current board state
        :param player_type: **int** 0 if AI, 1 if Player
        :return: **multi-dimensional list** List that defines the possible moves that can be made by that player
        """

        # list to store the possible moves
        possible_moves = []

        # Possible knight move offsets
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
                                    if board_state[x+move[0]][y+move[1]] == "W":
                                        possible_moves.append([[x, y, (x+move[0]), (y+move[1])], 0])
                                    elif board_state[x+move[0]][y+move[1]] == "p":
                                        # give more points if it kills a pawn
                                        possible_moves.append([[x, y, (x+move[0]), (y+move[1])], 2])
                                    else:
                                        possible_moves.append([[x, y, (x+move[0]), (y+move[1])], 1])
                            else:
                                if board_state[x+move[0]][y+move[1]] != "p" and board_state[x+move[0]][y+move[1]] != "k":
                                    # valid AI move for the knight, return it
                                    if board_state[x+move[0]][y+move[1]] == "W":
                                        possible_moves.append([[x, y, (x+move[0]), (y+move[1])], 0])
                                    elif board_state[x+move[0]][y+move[1]] == "P":
                                        # give more points if it kills a pawn, that matters much much more
                                        possible_moves.append([[x, y, (x+move[0]), (y+move[1])], 2])
                                    else:
                                        possible_moves.append([[x, y, (x+move[0]), (y+move[1])], 1])

                elif (piece_type == "P" and player_type == 0) or (piece_type == "p" and player_type == 1):

                    # offset of rows is down for the AI
                    if piece_type == "P":
                        offset_val = x + 1
                    else:
                        offset_val = x - 1

                    # boolean defining whether the pawn is redeploying or not
                    movement_upgrade = ((player_type == 0 and offset_val != 4) or (player_type == 1 and offset_val != 0)) \
                                       or ((knight_amount(board_state, player_type) < 2)
                                           and ((player_type == 0 and offset_val == 4)
                                                or (player_type == 1 and offset_val == 0)))

                    valid_move_val = False
                    move_vals = []
                    # check going diagonally right
                    if 0 <= offset_val < 5 and 0 <= (y + 1) < 5:
                        # it is within the constraints of the board, check whether there is an enemy there
                        if player_type == 0:
                            if board_state[offset_val][(y + 1)] == "k" or board_state[offset_val][(y + 1)] == "p":
                                if movement_upgrade:
                                    if board_state[offset_val][(y + 1)] == "p":
                                        possible_moves.append([[x, y, offset_val, (y + 1)], 2])
                                    else:
                                        possible_moves.append([[x, y, offset_val, (y + 1)], 1])
                                else:
                                    valid_move_val = True
                                    move_vals.append([x, y, offset_val, (y + 1)])
                        else:
                            if board_state[offset_val][(y + 1)] == "K" or board_state[offset_val][(y + 1)] == "P":
                                if movement_upgrade:
                                    if board_state[offset_val][(y + 1)] == "p":
                                        possible_moves.append([[x, y, offset_val, (y + 1)], 2])
                                    else:
                                        possible_moves.append([[x, y, offset_val, (y + 1)], 1])
                                else:
                                    valid_move_val = True
                                    move_vals.append([x, y, offset_val, (y + 1)])
                    if 0 <= offset_val < 5 and 0 <= (y - 1) < 5:
                        # it is within the constraints of the board, check whether there is an enemy there
                        if player_type == 0:
                            if board_state[offset_val][(y - 1)] == "k" or board_state[offset_val][(y - 1)] == "p":
                                if movement_upgrade:
                                    if board_state[offset_val][(y - 1)] == "p":
                                        possible_moves.append([[x, y, offset_val, (y - 1)], 2])
                                    else:
                                        possible_moves.append([[x, y, offset_val, (y - 1)], 1])
                                else:
                                    valid_move_val = True
                                    move_vals.append([x, y, offset_val, (y - 1)])
                        else:
                            if board_state[offset_val][(y - 1)] == "K" or board_state[offset_val][(y - 1)] == "P":
                                if movement_upgrade:
                                    if board_state[offset_val][(y - 1)] == "P":
                                        possible_moves.append([[x, y, offset_val, (y - 1)], 2])
                                    else:
                                        possible_moves.append([[x, y, offset_val, (y - 1)], 1])
                                else:
                                    valid_move_val = True
                                    move_vals.append([x, y, offset_val, (y - 1)])
                    if 0 <= offset_val < 5:
                        # check whether it is going forward
                        # check whether forward is whitespace or not
                        if board_state[offset_val][y] == "W":
                            if movement_upgrade:
                                possible_moves.append([[x, y, offset_val, y], 0])
                            else:
                                valid_move_val = True
                                move_vals.append([x, y, offset_val, y])
                    if not movement_upgrade and valid_move_val is True:
                        # pawn reached last rank and they have 2 knights already
                        # allow them to redeploy, generate possible moves
                        for move_output in move_vals:
                            for tempx in range(5):
                                for tempy in range(5):
                                    temp_piece_type = board_state[tempx][tempy]
                                    if temp_piece_type == "W":
                                        # this is a possibility
                                        possible_moves.append([[x, y, tempx, tempy], 0, move_output])
        return possible_moves

    def possible_capture_moves(self, board_state, player_type):
        """
        Generates possible capture moves for player_type on the given board_state

        :param board_state: **multi-dimensional list** Represents the current board state
        :param player_type: **int** 0 if AI, 1 if Player
        :return: **multi-dimensional list** List that defines the possible moves that can be made by that player
        """

        # list to store the possible moves
        possible_moves = []

        # Possible knight move offsets
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

                                    if board_state[x+move[0]][y+move[1]] == "p":
                                        # give more points if it kills a pawn
                                        possible_moves.append([[x, y, (x+move[0]), (y+move[1])], 2])
                                    elif board_state[x+move[0]][y+move[1]] != "W":
                                        possible_moves.append([[x, y, (x+move[0]), (y+move[1])], 1])
                            else:
                                if board_state[x+move[0]][y+move[1]] != "p" and board_state[x+move[0]][y+move[1]] != "k":
                                    # valid AI move for the knight, return it
                                    if board_state[x+move[0]][y+move[1]] == "P":
                                        # give more points if it kills a pawn, that matters much much more
                                        possible_moves.append([[x, y, (x+move[0]), (y+move[1])], 2])
                                    elif board_state[x+move[0]][y+move[1]] != "W":
                                        possible_moves.append([[x, y, (x+move[0]), (y+move[1])], 1])

                elif (piece_type == "P" and player_type == 0) or (piece_type == "p" and player_type == 1):

                    # offset of rows is down for the AI
                    if piece_type == "P":
                        offset_val = x + 1
                    else:
                        offset_val = x - 1

                    # boolean defining whether the pawn is redeploying or not
                    movement_upgrade = ((player_type == 0 and offset_val != 4) or (player_type == 1 and offset_val != 0)) \
                                       or ((knight_amount(board_state, player_type) < 2)
                                           and ((player_type == 0 and offset_val == 4)
                                                or (player_type == 1 and offset_val == 0)))

                    valid_move_val = False
                    move_vals = []
                    # check going diagonally right
                    if 0 <= offset_val < 5 and 0 <= (y + 1) < 5:
                        # it is within the constraints of the board, check whether there is an enemy there
                        if player_type == 0:
                            if board_state[offset_val][(y + 1)] == "k" or board_state[offset_val][(y + 1)] == "p":
                                if movement_upgrade:
                                    if board_state[offset_val][(y + 1)] == "p":
                                        possible_moves.append([[x, y, offset_val, (y + 1)], 2])
                                    else:
                                        possible_moves.append([[x, y, offset_val, (y + 1)], 1])
                                else:
                                    valid_move_val = True
                                    move_vals.append([x, y, offset_val, (y + 1)])
                        else:
                            if board_state[offset_val][(y + 1)] == "K" or board_state[offset_val][(y + 1)] == "P":
                                if movement_upgrade:
                                    if board_state[offset_val][(y + 1)] == "p":
                                        possible_moves.append([[x, y, offset_val, (y + 1)], 2])
                                    else:
                                        possible_moves.append([[x, y, offset_val, (y + 1)], 1])
                                else:
                                    valid_move_val = True
                                    move_vals.append([x, y, offset_val, (y + 1)])
                    if 0 <= offset_val < 5 and 0 <= (y - 1) < 5:
                        # it is within the constraints of the board, check whether there is an enemy there
                        if player_type == 0:
                            if board_state[offset_val][(y - 1)] == "k" or board_state[offset_val][(y - 1)] == "p":
                                if movement_upgrade:
                                    if board_state[offset_val][(y - 1)] == "p":
                                        possible_moves.append([[x, y, offset_val, (y - 1)], 2])
                                    else:
                                        possible_moves.append([[x, y, offset_val, (y - 1)], 1])
                                else:
                                    valid_move_val = True
                                    move_vals.append([x, y, offset_val, (y - 1)])
                        else:
                            if board_state[offset_val][(y - 1)] == "K" or board_state[offset_val][(y - 1)] == "P":
                                if movement_upgrade:
                                    if board_state[offset_val][(y - 1)] == "P":
                                        possible_moves.append([[x, y, offset_val, (y - 1)], 2])
                                    else:
                                        possible_moves.append([[x, y, offset_val, (y - 1)], 1])
                                else:
                                    valid_move_val = True
                                    move_vals.append([x, y, offset_val, (y - 1)])
                    if not movement_upgrade and valid_move_val is True:
                        # pawn reached last rank and they have 2 knights already
                        # allow them to redeploy, generate possible moves
                        for move_output in move_vals:
                            for tempx in range(5):
                                for tempy in range(5):
                                    temp_piece_type = board_state[tempx][tempy]
                                    if temp_piece_type == "W":
                                        # this is a possibility
                                        possible_moves.append([[x, y, tempx, tempy], 0, move_output])
        return possible_moves

    def pieces_amt(self, current_board):
        """
        Returns the amount of pieces on the board

        :param current_board: **multi-dimensional list** List that defines the current board state
        :return:
        """
        pieces = 0
        for row in current_board:
            for column in row:
                if column != "W":
                    pieces += 1
        return pieces

    def ai_score(self, board_state):
        """
        Computes the score of the board for the AI using a weighted score heuristic

        :param board_state: **multi-dimensional list** defining the board state
        :return: **numerical** returns score of the current board for the AI
        """
        # Calculate the current AI score and pawn amount
        ai_score_val = 0
        ai_pawns = 0
        for row in range(5):
            for column in range(5):
                if board_state[row][column] == "K":
                    ai_score_val += self.KNIGHT_WEIGHTING
                elif board_state[row][column] == "P":
                    ai_score_val += self.PAWN_WEIGHTING
                    ai_pawns += 1

        # Calculate the current player score and pawn amount
        player_score = 0
        player_pawns = 0
        for row in range(5):
            for column in range(5):
                if board_state[row][column] == "k":
                    player_score += self.KNIGHT_WEIGHTING
                elif board_state[row][column] == "p":
                    player_score += self.PAWN_WEIGHTING
                    player_pawns += 1

        # Set value to store the return value
        return_val = 0

        # Calculate general score of the board for the AI
        if len(self.possible_moves(board_state, 0)) == 0:
            # AI has no moves
            return_val = float("-infinity")
        elif ai_pawns == 0 and player_pawns == 0:
            # stalemate, return a high value less than a win
            # This number is not generally achievable with pawn wighting and thus works for terminal nodes
            return_val = 255
        elif ai_pawns == 0:
            # the player won
            return_val = float("-infinity")
        elif player_pawns == 0:
            # the ai won
            return_val = float("infinity")
        else:
            # return the weighted heuristic
            return_val = ai_score_val-player_score

        return return_val

    def combine_moves(self, board_state_val, x, y, new_x, new_y, x2, y2, new_x2, new_y2):
        """
        Combines two move onto a given board state without any drawing functionality
        Uses the rules of simultaneous movement in Apocalypse when combining the moves

        :param board_state_val: **multi-dimensional list** Board state
        :param x: **int** current x coord of the first piece to move
        :param y: **int** current y coord of the first piece to move
        :param new_x: **int** new x coord of the first piece to move
        :param new_y: **int** new y coord of the first piece to move
        :param x2: **int** current x coord of the second piece to move
        :param y2: **int** current y coord of the second piece to move
        :param new_x2: **int** new y coord of the second piece to move
        :param new_y2: **int** new y coord of the second piece to move
        :return: **multi-dimensional list** Board state with the moves combined

        """
        # Create deep copy of the board to configure
        board_state = copy.deepcopy(board_state_val)

        # store the values of each moving board piece
        player_val = board_state[x][y]
        ai_val = board_state[x2][y2]

        # Pieces are moving to the same location, process them differently (with simultaneous movement)
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
                # Destroy pawn, keep knight
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

            board_state[new_x][new_y] = player_val
            board_state[x][y] = "W"

            board_state[new_x2][new_y2] = ai_val
            board_state[x2][y2] = "W"

        # check whether an AI pawn reached the last rank
        if ai_val == "P" and new_x2 == 4:
            # reached last rank, process it
            board_state[new_x2][new_y2] = "K"

        # check whether a player pawn reached the last rank
        if player_val == "p" and new_x == 0:
            # reached last rank, process it
            board_state[new_x][new_y] = "k"

        return board_state

    def combine_single_move(self, board_state_val, x, y, new_x, new_y):
        """
        Combines a single move onto a given board state without any drawing functionality
        **Does not take simultaneous action into account**

        :param board_state_val: **multi-dimensional list** Board state
        :param x: **int** current x coord of the piece to move
        :param y: **int** current y coord of the piece to move
        :param new_x: **int** new x coord of the piece to move
        :param new_y: **int** new y coord of the piece to move
        :return: **multi-dimensional list** Board state with the move combined
        """
        board_state = copy.deepcopy(board_state_val)

        player_val = copy.copy(board_state[x][y])

        board_state[new_x][new_y] = player_val
        board_state[x][y] = "W"
        
        # check whether we need to upgrade pawns to knights
        if new_x == 4 and player_val == "P":
            board_state[new_x][new_y] = "K"
        elif new_x == 0 and player_val == "p":
            board_state[new_x][new_y] = "k"

        return board_state


"""

Turtle Related Functions

"""


def create_default_turtle(colour="white"):
    """
    Creates a default turtle with standard settings that are used in many places throughout the program

    :param colour: **string** **optional** Colour of the turtle to set
    :return: **object** Configured turtle
    """
    temp_turtle = turtle.Turtle()
    temp_turtle.hideturtle()
    temp_turtle.color(colour)
    temp_turtle._tracer(False)
    temp_turtle.up()
    return temp_turtle


"""

Piece Handler and Game Logic Functions

"""


def move_logic(x, y, new_x, new_y, x2, y2, new_x2, new_y2):
    """
    Combines two move onto a given board state WITH drawing functionality
    Uses the rules of simultaneous movement in Apocalypse when combining the moves

    :param board_state_val: **multi-dimensional list** Board state
    :param x: **int** current x coord of the first piece to move
    :param y: **int** current y coord of the first piece to move
    :param new_x: **int** new x coord of the first piece to move
    :param new_y: **int** new y coord of the first piece to move
    :param x2: **int** current x coord of the second piece to move
    :param y2: **int** current y coord of the second piece to move
    :param new_x2: **int** new y coord of the second piece to move
    :param new_y2: **int** new y coord of the second piece to move
    :return: **multi-dimensional list** Board state with the moves combined

    """
    global board
    # check whether the destination is the same for both

    if new_x == new_x2 and new_y == new_y2:
        print("Both pieces going to the same location")
        piece_type1 = get_piece(y, x)
        piece_type2 = get_piece(y2, x2)
        if piece_type1 == "p" and piece_type2 == "P":
            # both pawns, delete both
            print("Both are pawns, destroying both")
            delete_piece(x, y)
            delete_piece(x2, y2)
        elif piece_type1 == "k" and piece_type2 == "K":
            print("Both are knights, destroying both")
            delete_piece(x, y)
            delete_piece(x2, y2)
        elif piece_type1 == "p" and piece_type2 == "K":
            # execute move for AI and delete the player piece, it won the fight
            delete_piece(x, y)
            execute_move(x2, y2, new_x2, new_y2, SYMBOL_DICT[get_piece(y2, x2)])
        elif piece_type1 == "k" and piece_type2 == "P":
            # execute move for player and delete the AI piece, it won the fight
            delete_piece(x2, y2)
            # execute move for AI
            execute_move(x, y, new_x, new_y, SYMBOL_DICT[get_piece(y, x)])
    else:
        # the pieces are moving to different locations, simultaneous movement does not matter
        # we need to save the pawn type for each value
        
        # Check whether they are actually making a move, if so, store the current piece symbol and code
        if x != -1:
            player_piece = DrawingBoard.SYMBOL_DICT[get_piece(y, x)]
            player_code = get_piece(y, x)
        if x2 != -1:
            ai_piece = DrawingBoard.SYMBOL_DICT[get_piece(y2, x2)]
            ai_code = get_piece(y2, x2)

        # Execute the moves
        if x != -1:
            execute_move(x, y, new_x, new_y, player_piece, player_code)
        if x2 != -1:
            execute_move(x2, y2, new_x2, new_y2, ai_piece, ai_code)


def execute_move(x, y, new_x, new_y, symbol, piece_code=-1, force_delete=3):
    """
    Executes a given move on the board (modifying values and drawing the board)

    :param x: **int** current piece x coord
    :param y: **int** current piece y coord
    :param new_x: **int** new piece x coord
    :param new_y: **int** new piece y coord
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


    # check the saved symbol is the same as the current piece on the
    # board at that location, make sure we don't delete it
    test_symbol = DrawingBoard.SYMBOL_DICT[get_piece(y, x)]
    if test_symbol == symbol and force_delete == 3:
        # the other player did not move into our old location, we can delete whatever is there
        delete_piece(x, y)
    if force_delete == True:
        print("Force deleting the piece")
        delete_piece(x, y)

    # Get the turtle stored for the new block
    new_turtle = DrawingBoard.board_turtles[new_y][new_x]

    # clear the turtle (in case there is a written piece there) at the desired position
    new_turtle.clear()


    # write out the piece symbol centered in the block in ariel font with a size of the block height/width
    if platform.system() == "Windows" or platform.system() == "Linux":
        # adjust scaling of the y coord based upon the os
        new_turtle.write(symbol, False, align="center", font=("Ariel", int(DrawingBoard.BOARD_DIMENSION/5.5)))
    else:
        # Seems to have proper scaling on Mac OSX systems
        new_turtle.write(symbol, False, align="center", font=("Ariel", int(DrawingBoard.BOARD_DIMENSION/5)))

    # display the move on the right display
    if piece_code.isupper():
        # AI Move
        DrawingBoard.display_move(x, y, new_x, new_y, "A")
    else:
        # Player Move
        DrawingBoard.display_move(x, y, new_x, new_y, "P")


def valid_move(x, y, newx, newy, playername):
    """
    Checks whether a given move is valid or not for playername

    :param x: **int** current piece x coord
    :param y: **int** current piece y coord
    :param newx: **int** new piece x coord
    :param newy: **int** new piece y coord
    :param playername: **string** playername is 'p' or 'a' depending on player or ai
    :return: **bool** True if it is a valid move, False if not
    """
    # x, y is current piece that wants to move to newx, newy
    # playername is p or a depending on player or ai
    Bool_Return = False

    # Offsets of possible knight moves
    knight_moves = [[1, 2], [2, 1], [2, -1], [1, -2], [-1, -2], [-2, -1], [-2, 1], [-1, 2]]

    if 0 <= x <= 4 and 0 <= y <= 4 and 0 <= newx <= 4 and 0 <= newy <= 4:
        # Store the piece values
        piece_type = get_piece(x, y)
        new_piece_type = get_piece(newx, newy)

        # Check if its a knight
        if piece_type.lower() == "k":
            if (piece_type == "k" and playername == "p") or (piece_type == "K" and playername == "a"):
                # make sure they own that piece
                # see whether it is a valid knight move in the grid
                for move in knight_moves:
                    if (x + move[0]) == newx and (y + move[1] == newy):
                        if playername == "p":
                            if new_piece_type != "p" and new_piece_type != "k":
                                # valid knight move, continue on
                                Bool_Return = True
                                break
                        elif playername == "a":
                            if new_piece_type != "P" and new_piece_type != "K":
                                # valid knight move, continue on
                                Bool_Return = True
                                break
        elif piece_type.lower() == "p":

            if (piece_type == "p" and playername == "p") or (piece_type == "P" and playername == "a"):
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
                            Bool_Return = True
                    elif playername == "a":
                        if new_piece_type == "k" or new_piece_type == "p":
                            Bool_Return = True
                elif newx == offset_val and newy == y:
                    # check whether it is going forward
                    # check whether forward is whitespace or not
                    print("Checking whitespace")
                    if new_piece_type == "W":
                        Bool_Return = True
    return Bool_Return


def delete_piece(x, y):
    """
    This function will remove a board piece, and do the proper logic to remove the current location of it.
    It also clears the piece visually on the board.

    :param x: **int** x coord of the piece to delete
    :param y: **int** y coord of the piece to delete
    :return:
    """

    # get the turtle at x, y
    cur_turtle = DrawingBoard.board_turtles[y][x]

    # set the state of the board at that location to W
    set_piece(y, x, "W")

    # clear any symbols in that location
    cur_turtle.clear()


def get_piece(x, y):
    """
    Returns the piece from the board at the specified coord

    :param x: **int** x coord of the piece to delete
    :param y: **int** y coord of the piece to delete
    :return:
    """
    return board[x][y]


def set_piece(x, y, new_val):
    """
    Sets a given piece to a new value on the current global game state

    :param x: **int** x coord of the piece to set
    :param y: **int** y coord of the piece to set
    :param new_val: **string** value of the piece (ex. K, k, W, P, p)
    :return:
    """
    # Want to edit the global copy
    global board

    board[x][y] = new_val


def game_over():
    """
    Checks the global game state as to whether the game is over or not and returns a value defining the state

    :return: **int** returns a value based upon the current state (0 = player won, 1 = ai won, 2 = stalemate,
                     3 = not game over)
    """
    print("Checking whether it is game over or not")

    # Set constants for readability
    AI = 1
    PLAYER = 0

    AI_WON = 1
    PLAYER_WON = 0
    STALEMATE = 2
    NOT_OVER = 3

    # check whether one of the players has made two illegal moves
    return_val = -1
    if penalty_points[AI] == 2 and penalty_points[PLAYER] == 2:
        return_val = STALEMATE
    elif penalty_points[PLAYER] == 2:
        return_val = AI_WON
    elif penalty_points[AI] == 2:
        return_val = PLAYER_WON

    if return_val == -1:
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
            # no pawns on both sides
            return_val = STALEMATE
        elif ai_pieces == 0:
            return_val = PLAYER_WON
        elif player_pieces == 0:
            return_val = AI_WON
        else:
            return_val = NOT_OVER

        return return_val
    else:
        # we've already come to the game over condition, return it
        return return_val


def penalty_add(player):
    """
    Adds a penalty point to the player specified

    :param player: **string** letter defining the user (p for player, a for ai)
    :return:
    """

    if player == "p":
        penalty_index = 0
    else:
        penalty_index = 1

    # add one to the penalty, and return the new board
    cur_val = int(penalty_points[penalty_index])
    cur_val += 1
    penalty_points[penalty_index] = cur_val

    DrawingBoard.penalty_count()

    return board


def knight_amount(board, player):
    """
    Returns the amount knights a player has

    :param board_state: multidimensional list defining the game state
    :param player: **numeric** integer defining player
    :return: **numeric** how many knights the player owns on that game state
    """
    knight_amt = 0
    for row in board:
        for column in row:
            if player == 1 and column == "k":
                knight_amt += 1
            elif player == 0 and column == "K":
                knight_amt += 1
    return knight_amt


"""

Saving and Loading Functions

"""


def load_state():
    """
    Loads a saved game state and overwrites the global variables defining it. Then it draws out the new game state to
    allow the player to continue playing

    :return:
    """

    try:
        global penalty_points, board, moveOffset, depth_amt
        DARK_GREY = "#4A4A4A"

        file_obj = open("saved_board.apoc", "r")

        # Process and file and overwrite globals
        penalty_line = file_obj.readline().split(" ")
        penalty_points = [int(penalty_line[0]), int(penalty_line[1])]
        depth_amt = int(file_obj.readline())
        board_new_data = []
        for line in file_obj:
            split_data = line.replace("\n", "").split(" ")
            board_new_data.append(split_data)
        board = board_new_data

        # now we need to clear the screen and set the colour of it
        DrawingBoard.screen.clear()
        DrawingBoard.screen.bgcolor(DARK_GREY)

        # draw out the board and penalty system
        DrawingBoard.draw_board()
        DrawingBoard.penalty_count()

        # bind the event handlers again
        DrawingBoard.screen.onclick(onclick_board_handler)
        DrawingBoard.screen.onkeyrelease(save_state, "s")
        DrawingBoard.screen.onkeyrelease(load_state, "l")

        DrawingBoard.screen.listen()

        # reset messages offset location
        moveOffset = (DrawingBoard.BOARD_DIMENSION/2) - (DrawingBoard.TEXT_HEIGHT/0.7) - \
                     (DrawingBoard.PENALTY_TEXT_HEIGHT * 1.5)

        DrawingBoard.message_queue("Loaded Board")
        file_obj.close()
    except IOError:
        print("There was an error loading the board")
        DrawingBoard.message_queue("Error Loading")


def save_state():
    """
    Saves the global game state of the board and penalty points to a file

    :return:
    """
    # we don't want to let them save while a pawn is redeploying (can cause game mechanics issues)
    if highlight_params[3] is False:
        try:
            file_obj = open("saved_board.apoc", "w")
            # the file is just a single line defining the state
            line_to_write = str(penalty_points[0]) + " " + str(penalty_points[1]) + "\n"
            #store the depth amt (difficulty)
            line_to_write += str(depth_amt)
            for line in board:
                line_to_write += "\n" + " ".join(line)
            file_obj.write(line_to_write)
            DrawingBoard.message_queue("Saved Board")
            file_obj.close()
        except IOError:
            print("There was an error saving the board")
            message_queue("Error Saving")


"""

Click Handler Functions

"""


def onclick_board_handler(x, y):
    """
    Handles click events on the board and figures out how to deal with the game state

    :param x: **numeric** x coord of the screen click
    :param y: **numeric** y coord of the sreen click
    :return:
    """
    global board

    TOP_LEFT_X = DrawingBoard.box_locations[0][0][0]
    BOTTOM_LEFT_X = DrawingBoard.box_locations[4][4][0]
    BOX_WIDTH = DrawingBoard.BOARD_DIMENSION/5

    TOP_LEFT_Y = DrawingBoard.box_locations[0][0][1]
    BOTTOM_RIGHT_Y = DrawingBoard.box_locations[4][4][1]

    HIGHLIGHT_TURTLE = 0
    LAST_CLICK_COLUMN = 1
    LAST_CLICK_ROW = 2
    REDEPLOYING_PAWN = 3

    X_COORD = 0
    Y_COORD = 1

    # check whether they clicked inside the board
    if TOP_LEFT_X < x < (BOTTOM_LEFT_X + BOX_WIDTH) and (BOTTOM_RIGHT_Y - BOX_WIDTH) < y < TOP_LEFT_Y:
        # Want to edit the global copies of these vars
        global highlight_params, box_selected, board

        # Check whether a box is already highlighted, if so, clear that turtle
        if highlight_params[HIGHLIGHT_TURTLE] != 0:
            # already selected
            highlight_params[HIGHLIGHT_TURTLE].clear()

        # create new turtle for highlighting squares
        New_Highlight_Turtle = create_default_turtle("#007AFF")
        highlight_params[HIGHLIGHT_TURTLE] = New_Highlight_Turtle

        row = 0
        column = 0

        for current_row in DrawingBoard.box_locations:
            row += 1
            for current_box in current_row:
                column += 1

                if (current_box[X_COORD] + BOX_WIDTH) > x > current_box[X_COORD] \
                        and current_box[Y_COORD] > y > (current_box[Y_COORD] - BOX_WIDTH):
                    # They clicked in this box
                    if column != highlight_params[LAST_CLICK_COLUMN] or row != highlight_params[LAST_CLICK_ROW]:
                        # They clicked on a different square than last time

                        if box_selected == 1 and not highlight_params[REDEPLOYING_PAWN]:
                            # move the piece, a move was made
                            process_turn(row, column, current_box)

                            # Check whether it is game over
                            game_state = game_over()
                            if game_state != 3:
                                DrawingBoard.game_end_screen(game_state)

                            print_board()

                        elif highlight_params[REDEPLOYING_PAWN] is True and get_piece(row - 1, column - 1) == "W":
                            print("The user wants to redeploy the pawn, making the move")
                            redeploy_pawn(column, row)
                        elif (get_piece(row - 1, column - 1) == "k" or get_piece(row - 1, column - 1) == "p") \
                                and highlight_params[REDEPLOYING_PAWN] is False:
                            # only let the user select tiles it owns
                            play_sound("mouseDeselect.wav")
                            DrawingBoard.select_tile(New_Highlight_Turtle, current_box, column, row)
                    else:
                        if highlight_params[REDEPLOYING_PAWN] is False:
                            play_sound("mouseDeselect.wav")
                            print("deselected same box")
                            reset_highlight_params()
                        else:
                            print("You must redeploy to whitespace")

            column = 0
    else:
        # They didn't click on the board, check whether they clicked on a button
        for button in buttons:
            if button.check_clicked(x, y):
                button.execute_function()


def redeploy_pawn(column, row):
    """
    Redeploys the users given pawn to the row and column

    :param column: **int** column to move the pawn to
    :param row: **int** row to move the pawn to
    :return:
    """
    global highlight_params

    LAST_CLICK_COLUMN = 1
    LAST_CLICK_ROW = 2
    REDEPLOY_TURTLE = 4

    execute_move((highlight_params[LAST_CLICK_COLUMN] - 1), (highlight_params[LAST_CLICK_ROW] - 1),
                 (column - 1), (row - 1), "♙", "p", True)
    highlight_params[REDEPLOY_TURTLE].clear()

    reset_highlight_params()
    # rebind the saving and loading
    DrawingBoard.screen.onkeyrelease(save_state, "s")
    DrawingBoard.screen.onkeyrelease(load_state, "l")


def process_turn(row, column, current_box):
    """
    Processes a given valid turn for the player and ai, also calls the AI to generate its move here

    :param row: **int** Row the user wants the piece to move to
    :param column: **int** Column the user wants the piece to move to
    :param current_box: **list** Defines the [x, y] coords of the box
    :return:
    """
    global board

    LAST_CLICK_COLUMN = 1
    LAST_CLICK_ROW = 2

    AI = 0
    PLAYER = 1

    screen = DrawingBoard.screen

    # we don't want to let them click again while the AI move is being generated
    screen.onclick(None)

    # generate the AI move
    DrawingBoard.message_queue("Generating AI Move")

    print("GENERATING MINIMAX AI MOVE")

    # Generate the AI move using the global depth level
    AI_obj = AIMove(board)
    generated_ai = AI_obj.findmove(depth_amt)

    # The AI didn't find a move that it determined it would win from, we lower its depth level until one is found
    if generated_ai[1] == float("-infinity"):
        # it didn't find a move that seemed promising at this depth level, lets try to use lower depth levels
        for depth in range(depth_amt-1, 0, -1):
            print("Generating at a depth level of " + str(depth))
            generated_ai = AI_obj.findmove(depth)

            if generated_ai[1] != float("-infinity"):
                # we found a move that could work, break out of the loop
                break
        if generated_ai[1] == float("-infinity"):
            # just add a penalty point, we've found absolutely no valid moves, oh well :(
            # forcing a penalty
            generated_ai[0] = False

    print(generated_ai)

    # Set the AI move to the actual move and not the score value
    ai_val = generated_ai[0]
    print("AI MOVE: " + str(ai_val))

    # If the move isn't false, extract the actual move offsets from it
    if ai_val is not False:
        ai_val = ai_val[0]
        ai_type_val = get_piece(ai_val[0], ai_val[1])
    else:
        ai_type_val = "W"

    print("DONE GENERATING MINIMAX AI MOVE")

    # Values are minus 1 since the board is from 0-4, not 1-5
    # Determine whether the player move is valid
    player_validity = valid_move((highlight_params[LAST_CLICK_ROW] - 1), (highlight_params[LAST_CLICK_COLUMN] - 1),
                                 (row - 1), (column - 1), "p")
    player_type_val = get_piece((highlight_params[LAST_CLICK_ROW] - 1), (highlight_params[LAST_CLICK_COLUMN] - 1))

    # check whether to upgrade the pawn to knight for the AI
    if ai_val is not False and ai_type_val == "P" and ai_val[2] == 4 and knight_amount(board, AI) < 2:
        print("Upgraded AI pawn to knight")
        board[ai_val[0]][ai_val[1]] = "K"

    process_movements(ai_val, player_validity, row, column)

    # rebind the onscreenclick since the user cannot click fast enough now to influence the game
    screen.onclick(onclick_board_handler)

    # check whether the player has moved to the end row with a pawn
    if player_type_val == "p" and (row - 1) == 0 and player_validity is True:
        print("Player pawn got to the last rank, checking how many knights they have")
        if knight_amount(board, PLAYER) >= 2:
            redeploy_player_pawn(current_box, row, column)
        else:
            print("Changing piece to a knight")
            execute_move((highlight_params[LAST_CLICK_COLUMN] - 1), (highlight_params[LAST_CLICK_ROW] - 1),
                         column - 1, row - 1, "♘", "k", False)
            reset_highlight_params()
    else:
        reset_highlight_params()

    # check whether the AI deleted a piece when redeploying
    if ai_val is not False and len(generated_ai[0][1]) > 0:
        print(generated_ai[0][1])
        redeploy_location = generated_ai[0][1]
        delete_piece(redeploy_location[3], redeploy_location[2])


def process_movements(ai_val, player_validity, row, column):
    """
    Processes penalty logic for the moves, if they don't have a penalty, move the corresponding pieces

    :param ai_val: **multi-dimensional list** Defines the move that the AI decided to make (False if no move)
    :param player_validity: **bool** Whether the player's move is true or not
    :param row: **int** row of the click
    :param column: **int** column of the click
    :return:
    """
    global board

    LAST_CLICK_COLUMN = 1
    LAST_CLICK_ROW = 2

    if ai_val is not False and player_validity is True:
        # both made valid moves, we'll process them
        move_logic((highlight_params[LAST_CLICK_COLUMN] - 1), (highlight_params[LAST_CLICK_ROW] - 1), (column - 1),
                   (row - 1), ai_val[1], ai_val[0], ai_val[3], ai_val[2])
    elif ai_val is False and player_validity is False:
        print("AI and Player Penalty")
        DrawingBoard.message_queue("Player Penalty")
        DrawingBoard.message_queue("AI Penalty")
        board = penalty_add("a")
        board = penalty_add("p")
    elif ai_val is False:
        # give the ai a penalty, and process the move
        print("AI Penalty")
        DrawingBoard.message_queue("AI Penalty")
        board = penalty_add("a")
        move_logic((highlight_params[LAST_CLICK_COLUMN] - 1), (highlight_params[LAST_CLICK_ROW] - 1), (column - 1),
                   (row - 1), -1, 0, 0, 0)
    elif player_validity is False:
        # Player penalty, process AI move
        print("Player Penalty")
        DrawingBoard.message_queue("Player Penalty")
        board = penalty_add("p")
        move_logic(-1, 0, 0, 0, ai_val[1], ai_val[0], ai_val[3], ai_val[2])


def redeploy_player_pawn(current_box, row, column):
    """
    When a pawn gets to the last rank, if they have 2 or more knights, have to redeploy to a vacant square
    This function creates the orange box and applies proper logic

    :param current_box: **list** x, y coords of the top left of the redeploy box
    :param row: **int** row of the piece to redeploy
    :param column: **int** column of the piece to redeploy
    :return:
    """
    global highlight_params, box_selected

    LAST_CLICK_COLUMN = 1
    LAST_CLICK_ROW = 2
    REDEPLOYING_PAWN = 3
    REDEPLOY_TURTLE = 4

    X_COORD = 0
    Y_COORD = 1

    print("Allowing them to redeploy pawn, disabling saving")

    # Unbind the keybinds to prevent the user manipulating game mechanics
    DrawingBoard.screen.onkeyrelease(None, "s")
    DrawingBoard.screen.onkeyrelease(None, "l")

    # Modify the corresponding indexes of highlight_params
    highlight_params[REDEPLOYING_PAWN] = True
    highlight_params[LAST_CLICK_COLUMN] = column
    highlight_params[LAST_CLICK_ROW] = row
    box_selected = 0

    new_redeploy_turtle = turtle.Turtle()

    highlight_params[REDEPLOY_TURTLE] = new_redeploy_turtle
    new_redeploy_turtle._tracer(False)
    new_redeploy_turtle.hideturtle()
    new_redeploy_turtle.color("#FF9500")
    new_redeploy_turtle.up()

    # Move to the box location and draw an orange square
    new_redeploy_turtle.goto(current_box[X_COORD], current_box[Y_COORD])
    new_redeploy_turtle.down()
    for i2 in range(4):
        new_redeploy_turtle.forward(DrawingBoard.BOARD_DIMENSION/5)
        new_redeploy_turtle.right(90)
    new_redeploy_turtle.up()

    # Give the user an indication in the messages
    DrawingBoard.message_queue("Redeploy Pawn to")
    DrawingBoard.message_queue("a Vacant Square")


def reset_highlight_params():
    """
    Reset the values of highlight_params and box_selected

    :return:
    """
    global highlight_params, box_selected

    highlight_params[0] = 0
    highlight_params[1] = 0
    highlight_params[2] = 0
    highlight_params[3] = False
    box_selected = 0


def button_event(x, y):
    """
    Handles user click events on screens that have buttons

    :param x: **numeric** The x coordinate of a user's click
    :param y: **numeric** The y coordinate of a user's click
    :return:
    """
    for button in buttons:
        if button.check_clicked(x, y):
            button.execute_function()


"""

Game State Functions

"""


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


def modify_difficulty(level):
    """
    Modifies a global to change the ai difficulty for future move calculations

    :param level: **numeric** Specifies the difficulty level (ai move depth)
    :return:
    """
    global depth_amt
    depth_amt = level


"""

Miscellaneous Functions

"""


def main_menu():
    """
    Main function call, immediately draws the main menu screen and sets the proper scaling values of the screen

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
    global DrawingBoard

    # Create the board drawing object
    DrawingBoard = BoardDraw()

    # Draw the main screen
    DrawingBoard.draw_main_screen()

    turtle.done()


def play_sound(sound_file):
    """
    Plays a given sound on Windows and Mac OSX

    :param sound_file: **string** name of the sound to play
    :return:
    """
    try:
        if platform.system() == "Windows":
            winsound.PlaySound(sound_file, winsound.SND_FILENAME)
        elif platform.system() == "Darwin":
            os.system("afplay " + sound_file + "&")
        else:
            print("Sounds not supported")
    except:
        # Broad except statement since we don't fully know the possible errors of these sound functions
        print("Error playing sound")


def print_board():
    print("Board:")
    for row in range(5):
        print(board[row])


"""

Main Function Call

"""

if __name__ == '__main__':
    main_menu()
