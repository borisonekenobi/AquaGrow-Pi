import json
import threading
import time
from tkinter import *

import serial
from PIL import Image, ImageTk
from PIL.ImageFile import ImageFile

from plant import *

# Global variables
stop_running: bool = False
send_cmd: str = ''

port: str = 'COM5'
baudrate: int = 115200

clicked: bool = True
plants: list[Plant] = []
plant: Plant = Plant('None', 'images/no_image.png', 0, 0, 'None')

soil_moisture: StringVar
soil_moisture_value: float = 0.0

# Store image references to prevent garbage collection
image_references = {}


def create_status_bar(root: Tk) -> None:
    global plant, image_references, soil_moisture

    status_bar: Frame = Frame(root)
    status_bar.pack(side=TOP, fill=X)

    # Keep reference to prevent garbage collection
    leaf_img: PhotoImage = ImageTk.PhotoImage(Image.open('images/leaf.gif').resize((20, 20)))
    image_references['leaf'] = leaf_img

    panel: Label = Label(status_bar, image=leaf_img)
    panel.pack(side=LEFT, fill=BOTH, expand=NO, padx=10)

    status_bar_plant: Label = Label(status_bar, text=plant.name, font=('Arial', 9))
    status_bar_plant.pack(side=LEFT, fill=X, expand=NO)

    if plant is not None and plant.name != 'None':
        # Keep reference to prevent garbage collection
        ideal: Label = Label(status_bar, text=f'Ideal: {plant.min + 5}% - {plant.max - 5}%', font=('Arial', 9))
        ideal.pack(side=LEFT, fill=X, expand=YES)

    # Keep reference to prevent garbage collection
    drop_img: PhotoImage = ImageTk.PhotoImage(Image.open('images/drop.gif').resize((20, 20)))
    image_references['drop'] = drop_img

    panel: Label = Label(status_bar, image=drop_img)
    panel.pack(side=RIGHT, fill=BOTH, expand=NO, padx=10)

    status_bar_moisture: Label = Label(status_bar, textvariable=soil_moisture, font=('Arial', 9))
    status_bar_moisture.pack(side=RIGHT, fill=X, expand=NO)


def show_select_screen(root: Tk) -> None:
    global plants, image_references

    create_status_bar(root)

    categories: dict[str, Frame] = {}

    for p in plants:
        if p.category not in categories:
            Label(root, text=p.category, font=('Arial', 20), bg='white').pack(side=TOP, fill=X)
            sb: Scrollbar = Scrollbar(root, orient=HORIZONTAL, bg='black', activebackground='black',
                                      troughcolor='white')
            sb.pack(side=TOP, fill=X)
            canvas: Canvas = Canvas(root, xscrollcommand=sb.set, bg='white')
            canvas.pack(side=TOP, fill=X)
            sb.config(command=canvas.xview)

            # Create a frame inside the canvas to hold the buttons
            frame: Frame = Frame(canvas)
            canvas.create_window((0, 0), window=frame, anchor=NW)

            categories[p.category] = frame

        # Open image and resize it using PIL before converting to PhotoImage
        original_img: ImageFile = Image.open(p.image)
        resized_img: ImageFile = original_img.resize((original_img.width // 3, original_img.height // 3))
        photo_image: PhotoImage = ImageTk.PhotoImage(resized_img)

        # Store reference with unique key
        image_key: str = f"plant_{p.name}"
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
        canvas.config(scrollregion=canvas.bbox("all"), height=frame.winfo_reqheight())


def select_plant(root: Tk, selected_plant: Plant) -> None:
    global send_cmd, plant, clicked
    plant = selected_plant
    clicked = False

    send_cmd = f'{plant.min + 5}<{plant.max - 5}'

    # Clear the current window content
    for widget in root.winfo_children():
        widget.destroy()

    show_plant_info(root)


def show_plant_info(root: Tk) -> None:
    global plant, soil_moisture, soil_moisture_value, image_references

    create_status_bar(root)

    if plant is None or plant.name == 'None':
        show_select_screen(root)
        return

    main_frame: Frame = Frame(root, bg='white')
    main_frame.pack(side=TOP, fill=BOTH, expand=YES)

    panel: Label = Label(main_frame, bg='white')
    panel.pack(side=TOP)

    label: Label = Label(main_frame, textvariable=soil_moisture, font=('Arial', 20), bg='white')
    label.pack(side=TOP, pady=10)

    def update_image():
        happy_level: str = plant.get_happy_level(soil_moisture_value)

        if happy_level == SAD:
            image_file: str = 'images/sad.gif'
            text_color: str = 'red'
        elif happy_level == NEUTRAL:
            image_file: str = 'images/neutral.gif'
            text_color: str = 'orange'
        else:
            image_file: str = 'images/happy.gif'
            text_color = 'green'

        photo: PhotoImage = ImageTk.PhotoImage(file=image_file)
        image_references['mood'] = photo

        panel.config(image=photo)
        label.config(fg=text_color)
        root.after(1000, update_image)

    update_image()

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
            # Use the default image if none is provided
            if not p.get('image'):
                p['image'] = 'images/no_image.png'
            plants.append(Plant(p['name'], p['image'], p['min'], p['max'], k))


def read_serial_data() -> None:
    global send_cmd, soil_moisture, soil_moisture_value, stop_running, port, baudrate

    ser = serial.Serial(port, baudrate, timeout=0.100, xonxoff=False, rtscts=False, dsrdtr=True)

    while True:
        if send_cmd:
            ser.write(send_cmd.encode())
            send_cmd = ''
        if stop_running:
            break

        data = ser.read(1)
        data += ser.read(ser.in_waiting)
        data = data.decode('latin-1').strip()

        if data:
            try:
                print(data)
                data = float(data)
                if 0 <= data <= 100:
                    soil_moisture.set(f'{data:.2f}%')
                    soil_moisture_value = data

            except ValueError:
                print(data)

        time.sleep(0.1)


def stop(root: Tk) -> None:
    global stop_running
    root.destroy()
    stop_running = True


def main() -> None:
    try:
        read_thread = threading.Thread(target=read_serial_data)
        read_thread.start()

        read_plant_data()

        root: Tk = Tk()
        root.attributes('-fullscreen', True)
        root.title("Plant Monitor")

        # Set white background
        root.configure(bg='white')

        global soil_moisture
        soil_moisture = StringVar()

        if clicked:
            show_select_screen(root)
        else:
            show_plant_info(root)

        # Add escape key to exit fullscreen
        root.bind('<Escape>', lambda e: stop(root))

        root.mainloop()
    except KeyboardInterrupt:
        global stop_running
        stop_running = True


if __name__ == '__main__':
    main()
