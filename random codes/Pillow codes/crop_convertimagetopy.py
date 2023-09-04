__author__ = "Ernesto"
__email__ = "ernestondieki12@gmail.com"


from PIL import Image, ImageOps
import numpy as np
import os


def make_color_transparent(filename: str, color: str = (1, 1, 1)):
    """ make color in image transparent """

    img = Image.open(filename)  # n x m x 3
    imga = img.convert("RGBA")  # n x m x 4

    imga = np.asarray(imga)
    r, g, b, a = np.rollaxis(imga, axis=-1)  # split into 4 n x m arrays
    r_m = r != color[0]  # binary mask for red channel, True for all non color[0] values
    g_m = g != color[1]  # binary mask for green channel, True for all non color[1] values
    b_m = b != color[2]  # binary mask for blue channel, True for all non color[2] values

    # combine the three masks using the binary "or" operation
    # multiply the combined binary mask with the alpha channel
    a = a * ((r_m == 1) | (g_m == 1) | (b_m == 1))

    # stack the img back together
    imga = Image.fromarray(np.dstack([r, g, b, a]), 'RGBA')
    imga.save(filename)


# make_color_transparent()


def make_thumbnail(size: int, files):
    """ make image tiny without losing quality or being distorted """

    open_i = Image.open
    res = Image.Resampling.LANCZOS  # keep aspect ratio

    for file in files:
        try:
            i = open_i(file)
            i.thumbnail((size, size), res)
            # overwrite original
            i.save(file, optimize=True)
        except Exception as e:
            print(e)


image_names = ()
# make_thumbnail(64, image_names)


def writeToPy(files):
    """ save image to python variables in a python file """
    base = os.path.basename
    splixt = os.path.splitext

    with open("images.py", "a") as f:
        for file in files:
            variable = f"{splixt(base(file))[0]}_img".upper()
            f.write('\n\n{} = {}'.format(variable, open(file, 'rb').read()))


image_names = ()
# writeToPy(image_names)


def writeFromPy(files):

    for i, file in enumerate(files):
        with open(str(i) + ".png", "wb") as f:
            f.write(file)



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
        # get image mode
        # mode = image.mode
        # # convert to a supported mode
        # image = image.convert("L")
        # inverted_image = ImageOps.invert(image)
        # # convert back to its original mode
        # inverted_image = inverted_image.convert(mode)
        # inverted_image.save("I" + file)


# for i in ("mute.png", "sound.png"):
#     invertPaletteTransparentImage(i)


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
