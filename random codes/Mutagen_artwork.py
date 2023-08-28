from mutagen.id3 import ID3
from PIL import Image, ImageTk
from io import BytesIO
from typing import Optional


def artwork(filename: str) -> Optional[ImageTk.PhotoImage]:

    # get the file metadata
    songdet = ID3(filename)
    try:
        # get the picture data
        data = songdet.get("APIC:").data
        # convert to PIL image object
        pil_img = Image.open(BytesIO(data))
        # convert to a format for tk
        return ImageTk.PhotoImage(image=pil_img)

        print(pil_img.size)
    except Exception as e:
        print(e.__repr__())
        return


if __name__ == '__main__':

    from tkinter import Label, Tk
    root = Tk()
    label = Label(root)
    label.pack(expand=True)
    pil_image = artwork(
        "C:\\Users\\code\\Music\\Faouzia - You Don t Even Know Me (Official Music Video).mp3")
    label.config(image=pil_image)
    print(type(pil_image))
    root.mainloop()
