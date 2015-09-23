import turtle

"""
This program will create a smiley face using turtle graphics
and utilizes relative positioning to have dynamic scaling based
upon the set diameter

sety and setx is the same as goto(x, y), but sets the values independently
https://docs.python.org/3.5/library/turtle.html
"""

# Initialize turtle and screen
cur_screen = turtle.Screen()
cur_turtle = turtle.Turtle()

# set diameter (px) of the smile (change this to whatever you want!)
diameter = 400


cur_turtle.up()

# Set y coord of the turtle to negative half the diameter, create and fill the outer circle
cur_turtle.sety(-(diameter/2))
cur_turtle.color("yellow")
cur_turtle.begin_fill()
cur_turtle.circle(diameter/2)
cur_turtle.end_fill()

# change the direction of the head to 90 degrees right
cur_turtle.right(90)

# set the x coord to 70% of the radius and the y coord to 0
cur_turtle.setx(-((diameter/2) * 0.7))
cur_turtle.sety(0)
cur_turtle.color("black")

# create mouth with width of 70% of the circle, https://docs.python.org/3.5/library/turtle.html#turtle.circle
cur_turtle.down()
cur_turtle.circle((diameter/2) * 0.7, 180)

cur_turtle.up()

# displace eyes x coord 30% to the right and left of the radius of the circle from the center
# displace eyes y coord to 40% of the radius above 0
# Utilize the "dot" function to create the eyes
cur_turtle.setx((diameter/2) * 0.3)
cur_turtle.sety((diameter/2) * 0.4)
cur_turtle.dot(diameter * 0.10)
cur_turtle.setx(-(diameter/2) * 0.3)
cur_turtle.dot(diameter * 0.10)


turtle.exitonclick()
