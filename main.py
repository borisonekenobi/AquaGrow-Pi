import json
import random
from tkinter import *

from PIL import Image, ImageTk
from PIL.ImageFile import ImageFile

from plant import *

# Global variables
clicked = True
plants = []
plant = Plant(0, 'None', 0, 0, 'None')
soil_moisture = random.uniform(0.0, 0.80)

# Store image references to prevent garbage collection
image_references = {}


def create_status_bar(root: Tk) -> None:
    global plant, image_references

    status_bar: Frame = Frame(root)
    status_bar.pack(side=TOP, fill=X)

    # Keep reference to prevent garbage collection
    leaf_img: PhotoImage = ImageTk.PhotoImage(Image.open('images/leaf.gif').resize((20, 20)))
    image_references['leaf'] = leaf_img

    panel: Label = Label(status_bar, image=leaf_img)
    panel.pack(side=LEFT, fill=BOTH, expand=NO)

    status_bar_plant: Label = Label(status_bar, text=plant.name, font=('Arial', 9))
    status_bar_plant.pack(side=LEFT, fill=X)

    # Keep reference to prevent garbage collection
    drop_img: PhotoImage = ImageTk.PhotoImage(Image.open('images/drop.gif').resize((20, 20)))
    image_references['drop'] = drop_img

    panel: Label = Label(status_bar, image=drop_img)
    panel.pack(side=RIGHT, fill=BOTH, expand=NO)

    status_bar_moisture: Label = Label(status_bar, text=f'{soil_moisture * 100:.2f}%', font=('Arial', 9))
    status_bar_moisture.pack(side=RIGHT, fill=X)


def show_select_screen(root: Tk) -> None:
    global plants, image_references

    create_status_bar(root)

    categories: dict[str, Frame] = {}

    for p in plants:
        if p.category not in categories:
            Label(root, text=p.category, font=('Arial', 20), bg='white').pack(side=TOP, fill=X)
            sb: Scrollbar = Scrollbar(root, orient=HORIZONTAL)
            sb.pack(side=TOP, fill=X)
            canvas: Canvas = Canvas(root, xscrollcommand=sb.set)
            canvas.pack(side=TOP, fill=X)
            sb.config(command=canvas.xview)

            # Create a frame inside the canvas to hold the buttons
            frame: Frame = Frame(canvas)
            canvas.create_window((0, 0), window=frame, anchor=NW)

            categories[p.category] = frame

        # Open image and resize it using PIL before converting to PhotoImage
        original_img: ImageFile = Image.open("images/apple.gif")
        resized_img: ImageFile = original_img.resize((original_img.width // 3, original_img.height // 3))
        photo_image: PhotoImage = ImageTk.PhotoImage(resized_img)

        # Store reference with unique key
        image_key: str = f"plant_{p.id}"
        image_references[image_key] = photo_image

        # Create button with plant selection callback
        def make_callback(plant_obj: Plant) -> callable:
            return lambda: select_plant(root, plant_obj)

        Button(categories[p.category], text=p.name, image=photo_image, compound=TOP, command=make_callback(p)).pack(
            side=LEFT)

    # Update canvas scroll region after adding all buttons
    for category, frame in categories.items():
        frame.update_idletasks()
        canvas = frame.master
        canvas.config(scrollregion=canvas.bbox("all"))


def select_plant(root: Tk, selected_plant: Plant) -> None:
    global plant, clicked
    plant = selected_plant
    clicked = False

    # Clear the current window content
    for widget in root.winfo_children():
        widget.destroy()

    show_plant_info(root)


def show_plant_info(root: Tk) -> None:
    global plant, soil_moisture, image_references

    create_status_bar(root)

    if plant is None or plant.name == 'None':
        show_select_screen(root)
        return

    main_frame: Frame = Frame(root, bg='white')
    main_frame.pack(side=TOP, fill=BOTH, expand=YES)

    happy_level: str = plant.get_happy_level(soil_moisture)

    if happy_level == SAD:
        image_file: str = 'images/sad.gif'
        text_color: str = 'red'
    elif happy_level == NEUTRAL:
        image_file: str = 'images/neutral.gif'
        text_color: str = 'orange'
    else:
        image_file: str = 'images/happy.gif'
        text_color: str = 'green'

    # Keep reference to prevent garbage collection
    photo: PhotoImage = ImageTk.PhotoImage(file=image_file)
    image_references['mood'] = photo

    panel: Label = Label(main_frame, image=photo, bg='white')
    panel.pack(side=TOP)

    label: Label = Label(main_frame, text=f'{soil_moisture * 100:.2f}%', font=('Arial', 20), fg=text_color, bg='white')
    label.pack(side=TOP, pady=10)

    # Add a button to go back to plant selection
    back_button: Button = Button(main_frame, text="Select Different Plant", command=lambda: back_to_selection(root))
    back_button.pack(side=TOP, pady=20)


def back_to_selection(root: Tk) -> None:
    global clicked
    clicked = True

    # Clear the current window content
    for widget in root.winfo_children():
        widget.destroy()

    show_select_screen(root)


def read_plant_data() -> None:
    global plants
    with open('plants.json') as f:
        data = json.load(f)

    plants = []  # Clear the list before adding new plants
    for k, v in data.items():
        for p in v:
            plants.append(Plant(p['id'], p['name'], p['min'], p['max'], k))


def main() -> None:
    read_plant_data()

    root: Tk = Tk()
    root.attributes('-fullscreen', True)
    root.title("Plant Monitor")

    # Set white background
    root.configure(bg='white')

    if clicked:
        show_select_screen(root)
    else:
        show_plant_info(root)

    # Add escape key to exit fullscreen
    root.bind('<Escape>', lambda e: root.destroy())

    root.mainloop()


if __name__ == '__main__':
    main()
