import random
import json
from tkinter import *

from PIL import Image, ImageTk

from plant import *

clicked: bool = True

plants: list[Plant] = []
plant: Plant = Plant(0, 'None', 0, 0, 'None')
soil_moisture: float = random.uniform(0.0, 0.80)


def create_status_bar(root: Tk) -> None:
    global plant

    status_bar: Frame = Frame(root)
    status_bar.pack(side=TOP, fill=X)

    status_bar_plant_img: PhotoImage = ImageTk.PhotoImage(Image.open(r'images/leaf.gif').resize((20, 20)))
    panel = Label(status_bar, image=status_bar_plant_img)
    panel.pack(side=LEFT, fill=BOTH, expand=NO)

    status_bar_plant: Label = Label(status_bar, text=plant.name, font=('Arial', 9))
    status_bar_plant.pack(side=LEFT, fill=X)

    status_bar_moisture_img: PhotoImage = ImageTk.PhotoImage(Image.open(r'images/drop.gif').resize((20, 20)))
    panel = Label(status_bar, image=status_bar_moisture_img)
    panel.pack(side=RIGHT, fill=BOTH, expand=NO)

    status_bar_moisture: Label = Label(status_bar, text=f'{soil_moisture * 100:.2f}%', font=('Arial', 9))
    status_bar_moisture.pack(side=RIGHT, fill=X)


def show_select_screen(root: Tk) -> None:
    global plants

    categories: dict[str, Canvas] = {}

    for p in plants:
        if p.category not in categories:
            Label(root, text=p.category, font=('Arial', 20), bg='white').pack(side=TOP, fill=X)
            sb = Scrollbar(root, orient=HORIZONTAL)
            sb.pack(side=TOP, fill=X)
            categories[p.category] = Canvas(root, xscrollcommand=sb.set)
            categories[p.category].pack(side=TOP, fill=X)
            sb.config(command=categories[p.category].xview)

        photo = PhotoImage(file=r"images/apple.gif")
        photo_image = photo.subsample(3, 3)
        Button(categories[p.category], text=p.name, image=photo_image, compound=TOP).pack(side=LEFT)


def show_plant_info(root: Tk) -> None:
    global plant

    if plant is None:
        show_select_screen(root)
        return

    main_frame: Frame = Frame(root, bg='white')
    main_frame.pack(side=TOP, fill=BOTH, expand=YES)
    # main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    image_file: str
    text_color: str

    happy_level: str = plant.get_happy_level(soil_moisture)
    if happy_level == SAD:
        image_file = r'images/sad.gif'
        text_color = 'red'
    elif happy_level == NEUTRAL:
        image_file = r'images/neutral.gif'
        text_color = 'orange'
    else:
        image_file = r'images/happy.gif'
        text_color = 'green'

    photo: PhotoImage = PhotoImage(file=image_file)
    panel = Label(main_frame, image=photo, bg='white')
    panel.pack(side=TOP)

    label: Label = Label(main_frame, text=f'{soil_moisture * 100:.2f}%', font=('Arial', 20), fg=text_color, bg='white')
    label.pack(side=TOP, pady=10)


def read_plant_data() -> None:
    data: dict[str, list[dict[str, str | int | float]]]
    with open('plants.json') as f:
        data = json.load(f)

    global plants
    for k, v in data.items():
        for p in v:
            plants.append(Plant(p['id'], p['name'], p['min'], p['max'], k))


def main() -> None:
    read_plant_data()

    root: Tk = Tk()
    root.attributes('-fullscreen', True)

    create_status_bar(root)
    if clicked:
        show_select_screen(root)
    else:
        show_plant_info(root)

    root.mainloop()


if __name__ == '__main__':
    main()
