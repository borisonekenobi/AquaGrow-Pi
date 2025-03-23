import random
from tkinter import *

from PIL import Image, ImageTk

plant_name: str = 'Apple'

soil_moisture: float = random.uniform(0.0, 0.80)
min_moisture: float = 0.21
max_moisture: float = 0.60


def main() -> None:
    root: Tk = Tk()
    root.attributes('-fullscreen', True)

    status_bar: Frame = Frame(root)
    status_bar.pack(side=TOP, fill=X)

    status_bar_plant_img: PhotoImage = ImageTk.PhotoImage(Image.open(r'images/leaf.gif').resize((20, 20)))
    panel = Label(status_bar, image=status_bar_plant_img)
    panel.pack(side=LEFT, fill=BOTH, expand=NO)

    status_bar_plant: Label = Label(status_bar, text=plant_name, font=('Arial', 9))
    status_bar_plant.pack(side=LEFT, fill=X)

    status_bar_moisture_img: PhotoImage = ImageTk.PhotoImage(Image.open(r'images/drop.gif').resize((20, 20)))
    panel = Label(status_bar, image=status_bar_moisture_img)
    panel.pack(side=RIGHT, fill=BOTH, expand=NO)

    status_bar_moisture: Label = Label(status_bar, text=f'{soil_moisture * 100:.2f}%', font=('Arial', 9))
    status_bar_moisture.pack(side=RIGHT, fill=X)

    image_file: str
    text_color: str

    if soil_moisture < min_moisture or soil_moisture > max_moisture:
        image_file = r'images/sad.gif'
        text_color = 'red'
    elif soil_moisture <= min_moisture + 0.05 or soil_moisture >= max_moisture - 0.05:
        image_file = r'images/neutral.gif'
        text_color = 'orange'
    else:
        image_file = r'images/happy.gif'
        text_color = 'green'

    photo: PhotoImage = PhotoImage(file=image_file)
    panel = Label(root, image=photo)
    panel.pack(side=TOP, fill=BOTH, expand=YES)

    label: Label = Label(root, text=f'{soil_moisture * 100:.2f}%', font=('Arial', 20), foreground=text_color)
    label.pack(side=TOP, pady=10)

    # photo = PhotoImage(file=r"images/apple.gif")
    # photo_image = photo.subsample(3, 3)
    # Button(root, text='Apple', image=photo_image, compound=TOP).pack(side=TOP)

    root.mainloop()


if __name__ == '__main__':
    main()
