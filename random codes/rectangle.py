""" find the area of intersection of two rectangles """
__author__ = "Ernesto"


def getArea(rect1Coords, rect2Coords, rect1WidthHeight, rect2WidthHeight) -> int:
    """ x1 is the first x-coordinate for the first rectangle,
        x21 is the first for the second rectangle,
        x22 is the second x-coordinate for the second rectangle and so on
    """
    x1, x21 = rect1Coords[0], rect2Coords[0]
    y1, y21 = rect1Coords[1], rect2Coords[1]
    x2, x22 = x1 + rect1WidthHeight[0], x21 + rect2WidthHeight[0]
    y3, y23 = y1 - rect1WidthHeight[1], y21 - rect2WidthHeight[1]
    x_axis = [x1, x21, x2, x22]
    y_axis = [y1, y21, y3, y23]
    x_axis.sort(reverse=True)
    y_axis.sort(reverse=True)
    total_height = y_axis[0] - y_axis[-1]
    total_width = x_axis[0] - x_axis[-1]
    # check if the two rectangles intersect
    if (x2, y1) > (x21, y21) and x22 > x1:
        # get the units for the area that is left out
        outH = (y_axis[0] - y_axis[1]) + (y_axis[2] - y_axis[3])
        outW = (x_axis[0] - x_axis[1]) + (x_axis[2] - x_axis[3])
        if outH > 0 and outW > 0:
            # subtract the units for the area that is left out,
            # and return the product of the results
            return (total_height - outH) * (total_width - outW)
    # return 0 if they don't intersect
    return 0


area = getArea((0, 5), (1, 4), (3, 4), (3, 3))
print(area, "units")
