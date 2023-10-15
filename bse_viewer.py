import os
from tkinter import Scale
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import datetime
import json


# Author: Martin Svensson / Nooobservatory
# Version: 0.12.2-alhpa
#



# Global variables to store selected folder, date, time, and text filter
selected_folder = ""
current_index = 0
selected_date = None
selected_time = None
text_filter = ""  # Initialize the text filter to an empty string

# Global variables for "Follow Latest" functionality
follow_latest_enabled = False
after_id = None  # Variable to store the after ID for scheduled updates
current_image_path = ""     #Current image file shown

slider_pressed = False

def save_config():
    config = {
        "selected_folder": selected_folder,
        "selected_date": selected_date.get(),
        "selected_time": selected_time.get(),
        "text_filter": text_filter  # Save the text filter in the configuration
    }
    with open("config.json", "w") as config_file:
        json.dump(config, config_file)


def show_latest_image():

    global current_index, current_image_path
    #print("show_latest_image() executed")
    if selected_folder:
        # Get a list of image files in the selected folder
        image_files = [file for file in os.listdir(selected_folder) if
                       os.path.splitext(file)[1].lower() in image_extensions]
        image_files.sort(key=lambda x: os.path.getmtime(os.path.join(selected_folder, x)))

        if not image_files:
            label.config(image='')
            print("no image in selected folder")
            label.config(
                text="No images found matching the image filter and modified after the selected date and time.")
            label.config(text="No image files found in the selected folder.")
            date_time_label.config(text="Filename:  Date Time:")
            return

        # Convert strings to datetime
        selected_date_str = selected_date.get()
        selected_time_str = selected_time.get()
        selected_date_obj = datetime.datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        selected_time_obj = datetime.datetime.strptime(selected_time_str, "%H:%M").time()
        selected_datetime = datetime.datetime.combine(selected_date_obj, selected_time_obj)
        filtered_images = []
        

        for image_file in image_files:
            image_path = os.path.join(selected_folder, image_file)
            image_datetime = datetime.datetime.fromtimestamp(os.path.getmtime(image_path))

            # Check if the image file name contains the text filter
            if text_filter.lower() in image_file.lower():
                # Also, check if the image datetime is after the selected datetime
                if image_datetime >= selected_datetime:
                    filtered_images.append(image_path)
      
        print(f"Filtered images images: {len(filtered_images)}")
        
    
        #reset image if no filtered images exist 
        if (not filtered_images) or (len(filtered_images) < 1):
            label.config(image='')
            label.config(
                text="No images found matching the filter criteria.")
            print("no image found that match filter criteria")

            date_time_label.config(text="Filename:  Date Time:")
            return

        #print(f"Current index: {current_index}")
        if current_index is None:
            current_index = 0
        elif current_index < 0:
            current_index = 0
        elif current_index >= len(filtered_images):
            current_index = len(filtered_images) - 1

        #update slider
        index_slider.config(to=len(filtered_images),from_=1)
        #index_slider.set(current_index)


        # Save the selected date, time, and text filter
        save_config()

        latest_image_path = filtered_images[current_index]

        #Check if current image shown is the same as latest filtered. Add image processing call here:
        if current_image_path != latest_image_path:
            current_image_path = latest_image_path

        # Display the latest image using tkinter
        image = Image.open(latest_image_path)
        image.thumbnail((1000, 1000))  # Resize the image if it's too large
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.photo = photo
        label.pack()

        # Display the date and time of the image file
        image_date_time = datetime.datetime.fromtimestamp(os.path.getmtime(latest_image_path))
        date_time_label.config(text=f"Image Index: {current_index+1}/{len(filtered_images)}          Filename: {os.path.basename(latest_image_path)}       Date Time: {image_date_time.strftime('%Y-%m-%d %H:%M:%S')}")

    else:
        label.config(text="No folder selected.")
        folder_label.config(text="Selected Folder:")
        date_time_label.config(text="Filename:  Date Time:")
        print("no folder selected")


def select_folder():
    global selected_folder
    selected_folder = filedialog.askdirectory(title="Select a folder")
    if selected_folder:
        global current_index
        current_index = None  # Reset the current_index when a new folder is selected
        # Update the folder label
        folder_label.config(text=f"Selected Folder: {selected_folder}")
        show_latest_image()

        # Save the selected folder
        save_config()


def apply_text_filter():
    global text_filter
    text_filter = text_input.get()  # Get the text from the input box
    save_config()
    show_latest_image()  # Trigger image filtering


def toggle_follow_latest(stop_follow=False):
    global follow_latest_enabled, after_id  # Add after_id to the global declaration
    follow_latest_enabled = not follow_latest_enabled
    print(f"stop_follow= {stop_follow}")

    if follow_latest_enabled and not stop_follow:
        follow_latest_button.config(text="Stop", bg="#F16F58")
        follow_latest_image()
        index_slider.set(current_index+1)

    else:
        follow_latest_button.config(text="Follow Latest Layer", bg="#DCDCDC")
        follow_latest_enabled = False
        if after_id:
            window.after_cancel(after_id)  # Cancel the scheduled updates


def follow_latest_image():
    global after_id,current_index  # Add after_id to the global declaration
    if follow_latest_enabled:
        current_index = 100000000000                               #Set index to something big to show latest image
        show_latest_image()
        print("updating latest")
        after_id = window.after(1000, follow_latest_image)  # Assign the after ID


def next_image():
    global current_index, after_id  # Add after_id to the global declaration
    if current_index is not None:
        current_index += 1  # Reversed behavior for the next button
        #index_slider.set(current_index)
        print("next pressed")
        toggle_follow_latest(True)
        show_latest_image()
        index_slider.set(current_index+1)
        if after_id:
            window.after_cancel(after_id)  # Cancel the scheduled updates

def previous_image():
    global current_index, after_id  # Add after_id to the global declaration
    if current_index is not None:
        current_index -= 1  # Reversed behavior for the previous button
        toggle_follow_latest(True)
        show_latest_image()
        index_slider.set(current_index+1)
        if after_id:
            window.after_cancel(after_id)  # Cancel the scheduled updates

# Function to handle slider changes when the mouse is pressed
def handle_slider_click(event):
    global slider_pressed
    slider_pressed = True

# Function to handle slider changes when the mouse is released
def handle_slider_release(event):
    global slider_pressed
    slider_pressed = False
    index_slider.set(current_index+1)
    


def slider_changed_event(event):
    if slider_pressed:
        slider_changed(event)

def slider_changed(event):
    global current_index, after_id, slider_pressed  # Add after_id to the global declaration
    if current_index is not None and slider_pressed:
        current_index = index_slider.get() - 1 
        toggle_follow_latest(True)
        print(f"slider value:{current_index}")
        show_latest_image()
        if after_id:
            window.after_cancel(after_id)  # Cancel the scheduled updates

# Create a tkinter window
window = tk.Tk()
window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)
window.title("BSE Image Viewer")


ctrl_window = tk.Tk()
window.title("Controls")

# Create a label to display the image
label = tk.Label(window)
label.pack(pady=10)

# Create a frame to hold the control buttons
control_frame = tk.Frame(ctrl_window)
control_frame.pack(side=tk.TOP, padx=10, pady=10)

#----------------------------------------------------------------------------------------------------------------#

# Create a frame to hold image and information
image_frame = tk.Frame(window)
image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Create another frame inside image_frame for resizing
#inner_image_frame = tk.Frame(image_frame)
#inner_image_frame.pack(fill=tk.BOTH, expand=True)

# Prevent automatic resizing of inner_image_frame
#inner_image_frame.pack_propagate(False)


# Create a label to display the date and time of the image
date_time_label = tk.Label(window, text="Filename:  Date Time:", font=("TkDefaultFont", 14))
date_time_label.pack(side=tk.BOTTOM, padx=10, pady=10)

# Create a label with the default font
folder_label = tk.Label(window, text="Selected Folder:", font=("TkDefaultFont", 9))  # Change font here
folder_label.pack(side=tk.BOTTOM, padx=10, pady=10)

# Create a label and entry for text input
text_input_label = tk.Label(control_frame, text="Image Filter:")
text_input_label.pack(side=tk.TOP, padx=10, pady=0)
text_input = tk.Entry(control_frame)
text_input.pack(side=tk.TOP, padx=10, pady=7)
apply_text_filter_button = tk.Button(control_frame, text="Apply Selection Filters", command=apply_text_filter)
apply_text_filter_button.pack(side=tk.TOP, padx=10, pady=10)

# Create a button to select a folder
select_folder_button = tk.Button(control_frame, text="Select Folder", command=select_folder)
select_folder_button.pack(side=tk.BOTTOM, padx=10, pady=40)  # Anchored to the bottom with margin

# Create a button to toggle "Follow Latest" mode
follow_latest_button = tk.Button(control_frame, text="Follow Latest Layer", width=16, height=1, command=toggle_follow_latest)
follow_latest_button.pack(side=tk.BOTTOM, padx=10, pady=10)

# Create a scale widget to set the current index
index_slider = Scale(control_frame, from_=0, to=100, orient="horizontal", label="Select Index", length=400, command=slider_changed)
index_slider.pack(side=tk.BOTTOM, padx=10, pady=10)

# Bind the functions to the slider events
index_slider.bind("<ButtonPress-1>", handle_slider_click)
index_slider.bind("<ButtonRelease-1>", handle_slider_release)
#index_slider.bind("<Motion>", slider_changed_event)

# Create a label and combo boxes for date and time selection
date_label = tk.Label(control_frame, text="From Date (YYYY-MM-DD):")
date_label.pack(side=tk.TOP, padx=10, pady=0)
selected_date = ttk.Combobox(control_frame)
selected_date.pack(side=tk.TOP, padx=10, pady=0)
selected_date["values"] = [str((datetime.datetime.now() - datetime.timedelta(days=i)).date()) for i in range(7)]
selected_date.set(str(datetime.date.today()))

time_label = tk.Label(control_frame, text="From Time (HH:MM):")
time_label.pack(side=tk.TOP, padx=10, pady=0)
selected_time = ttk.Combobox(control_frame)
selected_time.pack(side=tk.TOP, padx=10, pady=0)
selected_time["values"] = [str(datetime.time(i, 0).strftime("%H:%M")) for i in range(24)]
selected_time.set("00:00")

# Create a button to apply date and time filter
#apply_filter_button = tk.Button(control_frame, text="Apply Filter", command=show_latest_image)
#apply_filter_button.pack(side=tk.TOP, padx=10, pady=14)

# Create navigation buttons with reversed behavior
next_button = tk.Button(control_frame, text="Next", command=next_image)  # Swap commands
next_button.pack(side=tk.TOP, padx=10, pady=20)  # Anchored to the bottom with margin
previous_button = tk.Button(control_frame, text="Previous", command=previous_image)  # Swap commands
previous_button.pack(side=tk.TOP, padx=10, pady=0)  # Anchored to the bottom with margin

image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']  # Supported image extensions

# Load config
if os.path.exists("config.json"):
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        selected_folder = config.get("selected_folder")
        selected_date.set(config.get("selected_date", str(datetime.date.today())))
        selected_time.set(config.get("selected_time", "00:00"))
        text_filter = config.get("text_filter", "")  # Load the text filter

    # Update the text input box with the loaded text filter
    text_input.delete(0, tk.END)  # Clear the current text in the input box
    text_input.insert(0, text_filter)  # Insert the loaded text filter

# Change label to selected folder in config file
folder_label.config(text=f"Selected Folder: {selected_folder}")
show_latest_image()

# Run the tkinter main loop
window.mainloop()
