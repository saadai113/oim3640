
import turtle

def koch_curve(t, length, depth):
    """
    Draw a single Koch curve segment.

    Parameters:
        t      - turtle object
        length - length of the current segment
        depth  - recursion depth (0 = straight line)
    """
    if depth == 0:
        t.forward(length)
    else:
        koch_curve(t, length / 3, depth - 1)
        t.left(60)
        koch_curve(t, length / 3, depth - 1)
        t.right(120)
        koch_curve(t, length / 3, depth - 1)
        t.left(60)
        koch_curve(t, length / 3, depth - 1)

turtle.tracer(0)        # turns off animation, draws all at once
t = turtle.Turtle()

t.penup()
t.goto(-150, 0)
t.pendown()

koch_curve(t, 300, 2)

turtle.update()          # renders everything in one shot
turtle.mainloop()

import turtle

def sierpinski(t, length, depth):
    if depth == 0:
        for _ in range(3):
            t.forward(length)
            t.left(120)
    else:
        sierpinski(t, length / 2, depth - 1)
        t.forward(length / 2)
        sierpinski(t, length / 2, depth - 1)
        t.backward(length / 2)
        t.left(60)
        t.forward(length / 2)
        t.right(60)
        sierpinski(t, length / 2, depth - 1)
        t.left(60)
        t.backward(length / 2)
        t.right(60)

turtle.tracer(0)
t = turtle.Turtle()

t.penup()
t.goto(-200, -170)
t.pendown()

sierpinski(t, 400, 5)

turtle.update()
turtle.mainloop()