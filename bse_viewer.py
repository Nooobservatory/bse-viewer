import os
from tkinter import Scale
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import datetime
import json
import shutil
import cv2
import numpy as np

# Author: Martin Svensson / Nooobservatory
# Version: 0.12.2-alhpa
#



# Global variables to store selected folder, date, time, and text filter
selected_folder = ""
filtered_images = []
current_index = 0
from_sel_date = None
from_sel_time = None
to_sel_date = None
to_sel_time = None
text_filter = ""  # Initialize the text filter to an empty string
timelapse_filename = ""
selected_fps = int(0)
include_overlay = False

# Global variables for "Follow Latest" functionality
follow_latest_enabled = False
after_id = None  # Variable to store the after ID for scheduled updates
current_image_path = ""     #Current image file shown

slider_pressed = False

def save_config():
    config = {
        "selected_folder": selected_folder,
        "from_sel_date": from_sel_date.get(),
        "from_sel_time": from_sel_time.get(),
        "to_sel_date": to_sel_date.get(),
        "to_sel_time": to_sel_time.get(),
        "text_filter": text_filter,  # Save the text filter in the configuration
        "basename": basename_input.get().strip(), # Save basenmame from input
        "selected_fps": fps_combobox.get()
    }
    with open("config.json", "w") as config_file:
        json.dump(config, config_file)


def show_latest_image():

    global current_index, current_image_path, filtered_images, include_overlay, to_sel_date, to_sel_time
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
        from_sel_date_str = from_sel_date.get()
        from_sel_time_str = from_sel_time.get()
        from_sel_date_obj = datetime.datetime.strptime(from_sel_date_str, "%Y-%m-%d").date()
        from_sel_time_obj = datetime.datetime.strptime(from_sel_time_str, "%H:%M").time()
        from_sel_datetime = datetime.datetime.combine(from_sel_date_obj, from_sel_time_obj)

        to_sel_date_str = to_sel_date.get()
        to_sel_time_str = to_sel_time.get()

        if to_sel_date_str.lower() == "now":
            to_sel_date_obj = datetime.date.today()
        else:
            to_sel_date_obj = datetime.datetime.strptime(to_sel_date_str, "%Y-%m-%d").date()
        
        if to_sel_time_str.lower() == "now":  
            to_sel_time_obj = datetime.datetime.now().time()
        else:
            to_sel_time_obj = datetime.datetime.strptime(to_sel_time_str, "%H:%M").time()

        to_sel_datetime = datetime.datetime.combine(to_sel_date_obj, to_sel_time_obj)            

        filtered_images = []
        

        for image_file in image_files:
            image_path = os.path.join(selected_folder, image_file)
            image_datetime = datetime.datetime.fromtimestamp(os.path.getmtime(image_path))

            # Check if the image file name contains the text filter
            if text_filter.lower() in image_file.lower():
                # Also, check if the image datetime is after the selected datetime
                if to_sel_datetime >= image_datetime >= from_sel_datetime:
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
        follow_latest_button.config(text="Follow Latest", bg="#DCDCDC")
        follow_latest_enabled = False
        if after_id:
            root.after_cancel(after_id)  # Cancel the scheduled updates


def follow_latest_image():
    global after_id,current_index  # Add after_id to the global declaration
    if follow_latest_enabled:
        set_from_now()
        current_index = 100000000000                               #Set index to something big to show latest image
        show_latest_image()
        print("updating latest")
        after_id = root.after(1000, follow_latest_image)  # Assign the after ID


def next_image():
    global current_index, after_id  # Add after_id to the global declaration
    if current_index is not None:
        current_index += 1 
        #index_slider.set(current_index)
        print("next pressed")
        toggle_follow_latest(True)
        show_latest_image()
        index_slider.set(current_index+1)
        if after_id:
            root.after_cancel(after_id)  # Cancel the scheduled updates

def previous_image():
    global current_index, after_id  # Add after_id to the global declaration
    if current_index is not None:
        current_index -= 1  
        toggle_follow_latest(True)
        show_latest_image()
        index_slider.set(current_index+1)
        if after_id:
            root.after_cancel(after_id)  # Cancel the scheduled updates

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
            root.after_cancel(after_id)  # Cancel the scheduled updates

# Function to export filtered images
def export_images():
    global filtered_images, text_filter
    save_config()
    prefix="Index"
    filtername=""
    basename = basename_input.get().strip() 
    if filtered_images:
        export_folder = filedialog.askdirectory(title="Select a folder to export images")
        if export_folder:
            if text_filter:
                export_folder = os.path.join(export_folder, text_filter)
                filtername="_"+text_filter
                os.makedirs(export_folder, exist_ok=True)
                #Get basename from GUI
                
            for i, image_path in enumerate(filtered_images):
                image_filename = os.path.basename(image_path)
                #Replace original filename with basename and datetime if specified
                if basename:
                    modification_date = os.path.getmtime(image_path)
                    modification_date_str = datetime.datetime.fromtimestamp(modification_date).strftime("%Y%m%d-%H%M%S")
                    image_name_without_extension, extension = os.path.splitext(image_filename)
                    new_filename = f"{modification_date_str}_{basename}{extension}"
                else:
                    new_filename = f"{image_filename}"
                export_path = os.path.join(export_folder, f"{prefix}{i+1}{filtername}_{new_filename}")
                shutil.copy(image_path, export_path)
            print(f"Images exported to {export_folder}")
    else:
        print("No images to export.")

# Function to set the filename based on user input
def export_timelapse():
    save_config()
    global filtered_images, timelapse_filename
    file_path = filedialog.asksaveasfilename(defaultextension=".mp4",initialfile=f"{basename_input.get().strip()}_{text_filter}_Layers{len(filtered_images)}" , filetypes=[("MP4 files", "*.mp4")])
    if file_path:
        timelapse_filename=file_path
        print(f"Filepath input:{file_path}")
        create_timelapse()

    else:
        print("No filepath")


# Function to export a timelapse video
def create_timelapse(target_resolution=(1920, 1080)):
    global filtered_images, timelapse_filename,selected_fps,include_overlay
    print(selected_fps)
    if not filtered_images:
        print("No images available for creating a timelapse.")
        return

    if not timelapse_filename:
        print("Please set the timelapse filename first.")
        return
    
    if not selected_fps:
        print("Please select the frames per second (fps) first.")
        return

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(timelapse_filename, fourcc, selected_fps, target_resolution)
   
    try:
        for i, image_path in enumerate(filtered_images):

            print(f"{i+1}/{len(filtered_images)} images processed")
            
            frame = cv2.imread(image_path)

            # Calculate the aspect ratio of the original image
            height, width, _ = frame.shape
            aspect_ratio = width / height

            if aspect_ratio >= (target_resolution[0] / target_resolution[1]):
                new_width = target_resolution[0]
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = target_resolution[1]
                new_width = int(new_height * aspect_ratio)

            # Resize the frame to fit inside the target resolution while preserving the aspect ratio
            frame = cv2.resize(frame, (new_width, new_height))

            # Create a black canvas of the target resolution
            canvas = np.zeros((target_resolution[1], target_resolution[0], 3), dtype=np.uint8)

            # Calculate the position to paste the resized image at the center of the canvas
            x_offset = (target_resolution[0] - new_width) // 2
            y_offset = (target_resolution[1] - new_height) // 2

            # Paste the resized image onto the canvas
            canvas[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = frame
            
            if include_overlay:
                # Add text overlay for the image index in the lower left corner
                text = f"{i:04}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1.2
                font_color = (255, 255, 255)  # White text
                font_thickness = 2
                text_x = 15
                text_y = target_resolution[1] -25  # Adjust this to control text position
                cv2.putText(canvas, text, (text_x, text_y), font, font_scale, font_color, font_thickness)

            out.write(canvas)

        out.release()
        print(f"Timelapse video saved as {timelapse_filename}")
    except Exception as e:
        print(f"An error occurred while creating the timelapse: {e}")

def get_selected_fps(event):
    global selected_fps
    selected_fps = int(fps_combobox.get())
    if type(selected_fps) != int:
        selected_fps=int(30)
    if selected_fps >= 120:
        selected_fps=120
    fps_combobox.set(selected_fps)
    save_config()
    calculate_timelapse_duration()


def calculate_timelapse_duration():
    selected_fps = int(fps_combobox.get())
    num_images = len(filtered_images)

    if selected_fps == 0:
        duration = "N/A"
    else:
        duration = f"{num_images / selected_fps:.1f} seconds"

    duration_label.config(text=f"Duration: {duration}")

def toggle_overlay():
    global include_overlay
    include_overlay = not include_overlay   

# Create a function to be called when "now" is selected
def to_date_selection(event):
    global to_sel_date
    selected_value = to_sel_date.get().lower()  # Convert to lowercase
    print(selected_value)
    if selected_value == "now":
        set_from_now()

# Create a function to be called when "now" is selected
def to_time_selection(event):
    global to_sel_time
    selected_value = to_sel_time.get().lower()  # Convert to lowercase
    if selected_value == "now":
       set_from_now()

def set_from_now():
    global to_sel_time, to_sel_date
    to_sel_date.set("Now")
    to_sel_time.set("Now")


#*************************************************************************************************************#
#****************************************     GUI     ********************************************************#
#*************************************************************************************************************#


#---------------------------------------- Setup root window --------------------------------------------------#

#Placement parameters
border_pading = 5


# Create Main window
root = tk.Tk()
root.title("BSE Image Viewer")

#test = tk.Tk()

# Create a frame to hold the control buttons
control_frame = tk.Frame(root)
control_frame.pack(side=tk.LEFT, padx=(border_pading,5), pady=0)
control_frame.configure(bg="light green")



# Create a frame to hold the control buttons and image information 
image_control_frame = tk.Frame(root)
image_control_frame.pack(side=tk.BOTTOM, padx=(0,border_pading), pady=(0,border_pading))
image_control_frame.configure(bg="light blue")
# Configure the row and column to expand when the window is resized
image_control_frame.grid_rowconfigure(1, weight=1)
image_control_frame.grid_columnconfigure(0, weight=1)



# Create a frame to hold image and information
image_frame = tk.Frame(root)
image_frame.pack(fill=tk.BOTH, expand=True, padx=(0,border_pading), pady=(0,0))
image_frame.configure(bg="dark grey")
#image_control_frame.grid_rowconfigure(1, weight=1)
#image_control_frame.grid_columnconfigure(0, weight=1)


#---------------------------------- Create image frame content ----------------------------------------------#

# Create a label to display the image
label = tk.Label(image_frame)
label.pack(pady=10)

#-------------------------------- Create Lower control frame content ----------------------------------------#

# Create navigation buttons next, prev
previous_button = tk.Button(image_control_frame, text="Previous",width=8, height=1, command=previous_image)
previous_button.grid(row=0, column=0, padx=0, pady=0)

next_button = tk.Button(image_control_frame, text="Next",width=8,height=1, command=next_image)
next_button.grid(row=0, column=0, padx=(150,0), pady=0)

# Create a button to toggle "Follow Latest" mode
follow_latest_button = tk.Button(image_control_frame, text="Follow Latest", width=16, height=1, command=toggle_follow_latest)
follow_latest_button.grid(row=0, column=0, padx=(500,0), pady=0)

# Create a scale widget to set the current index
index_slider = Scale(image_control_frame, from_=0, to=100, orient="horizontal", length=1000, command=slider_changed)
index_slider.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

# Bind the functions to the slider events
index_slider.bind("<ButtonPress-1>", handle_slider_click)
index_slider.bind("<ButtonRelease-1>", handle_slider_release)

# Create a label to display the date and time of the image
date_time_label = tk.Label(image_control_frame, text="Filename:  Date Time:", font=("TkDefaultFont", 14))
date_time_label.grid(row=2, column=0, columnspan=2, padx=10, pady=0)

# Create a label with the default font
folder_label = tk.Label(image_control_frame, text="Selected Folder:", font=("TkDefaultFont", 9))
folder_label.grid(row=3, column=0, columnspan=2, padx=10, pady=0)







#-------------------------------- Create Left control frame content -----------------------------------------#
# Create a label and entry for text input
text_input_label = tk.Label(control_frame, text="Image Filter:")
text_input_label.pack(side=tk.TOP, padx=10, pady=0)
text_input = tk.Entry(control_frame)
text_input.pack(side=tk.TOP, padx=10, pady=7)

# Create a checkbox for enabling/disabling the overlay
overlay_checkbox_var = tk.BooleanVar()
overlay_checkbox = ttk.Checkbutton(control_frame, text="Add index overlay", variable=overlay_checkbox_var, command=toggle_overlay)
overlay_checkbox.pack(side=tk.BOTTOM, padx=10, pady=10)
overlay_checkbox.state(['!alternate'])

#Duration label
duration_label = tk.Label(control_frame, text="Duration:")
duration_label.pack(side=tk.BOTTOM, padx=10, pady=0)

# Create a label and combo box for selecting the frames per second (fps)
fps_values = [1,2,5,10,15,24,30,60,90,120]  # Example fps values
fps_combobox = ttk.Combobox(control_frame, values=fps_values, width=5)
fps_combobox.set(fps_values[3])  # Set a default value (e.g., 30 fps)
fps_combobox.pack(side=tk.BOTTOM, padx=10, pady=0)
fps_combobox['justify'] = 'center'
fps_combobox.bind("<Return>", get_selected_fps)
fps_combobox.bind("<<ComboboxSelected>>", get_selected_fps)

fps_label = tk.Label(control_frame, text="Frames Per Second (FPS):")
fps_label.pack(side=tk.BOTTOM, padx=10, pady=0)

# Create a button to set the timelapse filename and export folder
set_filename_button = tk.Button(control_frame, text="Export Timelapse", command=export_timelapse)
set_filename_button.pack(side=tk.BOTTOM, padx=10, pady=10)

# Create a button to export images
export_button = tk.Button(control_frame, text="Export Images", command=export_images)
export_button.pack(side=tk.BOTTOM, padx=10, pady=10)

# Add a basename entry widget to the UI
basename_input = tk.Entry(control_frame)
basename_input.pack(side=tk.BOTTOM, padx=10, pady=0)
basename_label = tk.Label(control_frame, text="Filename: _Suffix:")
basename_label.pack(side=tk.BOTTOM, padx=10, pady=7)

# Create a button to select a folder
select_folder_button = tk.Button(control_frame, text="Select Folder", command=select_folder)
select_folder_button.pack(side=tk.BOTTOM, padx=10, pady=40)  # Anchored to the bottom with margin



# *FROM* date and time selection
date_label = tk.Label(control_frame, text="From Date (YYYY-MM-DD):")
date_label.pack(side=tk.TOP, padx=10, pady=0)
from_sel_date = ttk.Combobox(control_frame,width=12)
from_sel_date.pack(side=tk.TOP, padx=10, pady=0)
from_sel_date["values"] = [str((datetime.datetime.now() - datetime.timedelta(days=i)).date()) for i in range(7)]
from_sel_date.set(str(datetime.date.today()))
from_sel_date['justify'] = 'center'

from_time_label = tk.Label(control_frame, text="From Time (HH:MM):")
from_time_label.pack(side=tk.TOP, padx=10, pady=0)
from_sel_time = ttk.Combobox(control_frame, width=12)
from_sel_time.pack(side=tk.TOP, padx=10, pady=0)
from_sel_time["values"] = [str(datetime.time(i, 0).strftime("%H:%M")) for i in range(24)]
from_sel_time.set("00:00")
from_sel_time['justify'] = 'center'

# *TO* date and time selection
date_label = tk.Label(control_frame, text="To Date (YYYY-MM-DD):")
date_label.pack(side=tk.TOP, padx=10, pady=0)
to_sel_date = ttk.Combobox(control_frame,width=12)
to_sel_date.pack(side=tk.TOP, padx=10, pady=0)
to_date_values = ["Now"] + [str((datetime.datetime.now() - datetime.timedelta(days=i)).date()) for i in range(7)]
to_sel_date["values"] = to_date_values
to_sel_date.set(str(datetime.date.today()))
to_sel_date['justify'] = 'center'

to_time_label = tk.Label(control_frame, text="To Time (HH:MM):")
to_time_label.pack(side=tk.TOP, padx=10, pady=0)
to_sel_time = ttk.Combobox(control_frame, width=12)
to_sel_time.pack(side=tk.TOP, padx=10, pady=0)
to_time_values = ["Now"] + [str(datetime.time(i, 0).strftime("%H:%M")) for i in range(24)]
to_sel_time["values"] = to_time_values
to_sel_time.set("00:00")
to_sel_time['justify'] = 'center'

to_sel_date.bind("<<ComboboxSelected>>",to_date_selection)
to_sel_time.bind("<<ComboboxSelected>>",to_time_selection)

#Apply button 
apply_text_filter_button = tk.Button(control_frame, text="Apply Selection Filters", command=apply_text_filter)
apply_text_filter_button.pack(side=tk.TOP, padx=10, pady=20)




#---------------------------------- Configure GUI ----------------------------------------------#
image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']  # Supported image extensions

# Load config
if os.path.exists("config.json"):
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        selected_folder = config.get("selected_folder")
        from_sel_date.set(config.get("from_sel_date", str(datetime.date.today())))
        from_sel_time.set(config.get("from_sel_time", "00:00"))
        to_sel_date.set(config.get("to_sel_date","Now")),
        to_sel_time.set(config.get("to_sel_time","Now")),
        text_filter = config.get("text_filter", "")  # Load the text filter
        basename=config.get("basename","")
        selected_fps=int(config.get("selected_fps",30))


    #update fps combobox
    fps_combobox.set(selected_fps)
    # Update the text input box with the loaded text filter  
    basename_input.delete(0,tk.END)    
    basename_input.insert(0, basename) 
    # Update the text input box with the loaded text filter
    text_input.delete(0, tk.END)  # Clear the current text in the input box
    text_input.insert(0, text_filter)  # Insert the loaded text filter

# Change label to selected folder in config file
folder_label.config(text=f"Selected Folder: {selected_folder}")
show_latest_image()
calculate_timelapse_duration()
# Run the tkinter main loop
root.mainloop()
