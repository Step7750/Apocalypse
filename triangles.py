import turtle
import math

"""
This program will ask for 4 triangle leg lengths (in pixels) and will
draw the proper triangle on the turtle screen
"""

# Initiate turtle and screen, make the turtles color red
cur_screen = turtle.Screen()
cur_turtle = turtle.Turtle()

# Distance between each triangle
offset = 30

cur_turtle.color("red")

# Move the turtle to the left side of the screen for better formatting
# Add 10 pixels from the edge of the screen

# Rob Kremer said we could :)
cur_turtle.up()
cur_turtle.setx(-cur_screen.window_width()/2 + 10)
cur_turtle.down()


def hypotenuse(adjacent, opposite):
    """
    This function will return the hypotenuse length when given the adjacent and opposite length of a triangle
    """
    # Pythagorean theorem
    # a**2 + b**2 = c**2
    return math.sqrt(adjacent**2 + opposite**2)


def compute_top_angle(hypotenuse, opposite):
    """
    This function will return the angle (in degrees) of the top left of the triangle

    Sin**-1 = opp/hyp
    Then convert radians to degrees
    """
    return math.degrees(math.asin(opposite/hypotenuse))


def draw_triangle(adj, opp, hyp, angle):
    """
    Draws the triangle on the screen in red
    """

    cur_turtle.begin_fill()

    # Start turtle facing north, move forward the distance of adjacent
    cur_turtle.setheading(90)
    cur_turtle.forward(adj)

    # Set heading to facing east, move right 90 minus the calculated angle
    cur_turtle.setheading(0)
    cur_turtle.right(90-angle)

    # Move the distance of hypotenuse, look west and move the distance of opposite
    cur_turtle.forward(hyp)
    cur_turtle.setheading(180)
    cur_turtle.forward(opp)

    cur_turtle.end_fill()

    # Move the turtle to the bottom right vertex, take into account the offset between triangles
    cur_turtle.up()
    cur_turtle.goto(cur_turtle.xcor() + opp + offset, 0)
    cur_turtle.down()

# Iterate 4 times
for i in range(4):
    # Ask for the adj and opp lengths in pixels, call proper functions and draw the triangle
    print("\nPlease enter the appropriate triangle lengths\n")
    adj = int(input("What is the adjacent length? (px)"))
    opp = int(input("What is the opposite length? (px)"))

    # call the proper functions and store the return value
    hyp = hypotenuse(adj, opp)
    angle = compute_top_angle(hyp, opp)
    draw_triangle(adj, opp, hyp, angle)

print("\nDone drawing the triangles")

turtle.exitonclick()
