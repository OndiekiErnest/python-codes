import turtle


def draw_heart():
    turtle.color("red")
    turtle.begin_fill()
    turtle.pensize(3)
    turtle.left(50)
    turtle.forward(113)
    turtle.circle(50, 200)
    turtle.right(140)
    turtle.circle(50, 200)
    turtle.forward(133)
    turtle.end_fill()


if __name__ == '__main__':
    draw_heart()
