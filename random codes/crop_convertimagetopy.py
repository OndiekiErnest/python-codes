__author__ = "Ernesto"
__email__ = "ernestondieki12@gmail.com"


from PIL import Image, ImageOps
# from images import *
from os import listdir


def make_thumbnail(size: int, files):
    """ make image tiny without losing quality or being distorted """

    for file in files:
        i = Image.open(file)
        i.thumbnail((size, size), Image.ANTIALIAS)
        # overwrite original
        i.save(file)


# make_thumbnail(32, ("open.png", ))


def writeToPy(files: tuple):
    """ save image to python variables in a python file """
    for file in files:
        with open("images.py", "a") as f:
            f.write('\n\n{} = {}'.format(file.split(".")[
                    0].upper() + '_img'.upper(), open(file, 'rb').read()))


# writeToPy(("sixth.png",))
# writeToPy(("first.png", "second.png", "third.png",
#            "fourth.png", "fifth.png", "seventh.png"))


def writeFromPy(files):

    for i, file in enumerate(files):
        with open(str(i) + ".png", "wb") as f:
            f.write(file)


# image_files = (PREVIOUS_IMG, PLAY_IMG, PAUSE_IMG, NEXT_IMG,
#                ADDFOLDER_IMG, REPEATFOLDER_IMG, SHUFFLE_IMG,
#                REPEAT_IMG, DARKSHUFFLE_IMG, DARKREPEAT_IMG,
#                APP_IMG, SOKORO_IMG, DARKPOINTER_IMG)
# writeFromPy((DARKPOINTER_IMG,))


def invertPaletteTransparentImage(file):
    """ negate color """
    image = Image.open(file)
    if image.mode == "P":
        image = image.convert("RGBA")
    # confirm the conversion was successful
    if image.mode == "RGBA":
        r, g, b, a = image.split()
        rgb_image = Image.merge("RGB", (r, g, b))
        inverted_image = ImageOps.invert(rgb_image)
        r2, g2, b2 = inverted_image.split()
        final_transparent_image = Image.merge("RGBA", (r2, g2, b2, a))
        final_transparent_image.save("I" + file)
    else:
        print(f"Image ({file}) is not a Transparent Image. Skipping...")
    #     # get image mode
        # mode = image.mode
        # # convert to a supported mode
        # image = image.convert("L")
        # inverted_image = ImageOps.invert(image)
        # # convert back to its original mode
        # inverted_image = inverted_image.convert(mode)
        # inverted_image.save("I" + file)


def rotateImage(file: str, angle: int):
    """ rotate clockwise """
    image = Image.open(file)
    rotated_image = image.rotate(angle)
    rotated_image.save(file)


def mirrorImage(file: str):
    """ horizontal flip """
    image = Image.open(file)
    mirrored_image = ImageOps.mirror(image)
    mirrored_image.save(file)


# for i in ("show.png", "hide.png"):
#     invertPaletteTransparentImage(i)
