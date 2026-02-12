import turtle
from turtle import forward
t=turtle.Turtle()
t.speed(0)
t.forward(100)
t.left(90)
def draw_square(turtle_obj, size=100):
    """Draw a square with the gien size"""
    for _ in range(4):
        turtle_obj.forward(size)
        turtle_obj.left(90)

def draw_spiral(t):
    """"""
    for i in range(36):
        draw_square(t, 50)
        t.left(10)

def main():
    t=turtle.Turtle()
    t.speed(0)
    #draw_square(t)
    #draw_sqiare(t, size=50)
    draw_spiral(t)
    turtle.mainloop()


draw_square()
draw_spiral(t)
main()