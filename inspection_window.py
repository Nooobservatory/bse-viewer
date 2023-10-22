import tkinter as tk
from tkinter import filedialog
from tkinter import Entry
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import re
import numpy as np

# Create a Tkinter window
root = tk.Tk()
root.title("Image Viewer")
toolbar = None

# Initialize img as None
img = None
points = []
original_xlim = 1.1
original_ylim = 1.0
image_origin = [0,0]
image_scale = 0

white_point = 1.1   # grayscale images
color_map="Greys_r" # for gfreyscale images

# Function to open an image
def open_image():
    global img, points
    file_path = filedialog.askopenfilename()
    if file_path:
        img = plt.imread(file_path)
        ax.clear()

        points = []  # Clear the points list
        scale_subplot()
        canvas.draw()

def new_scale_entry(event):

    new_entry = image_scale_entry.get()
    if re.match(r'^\d*\.?\d*$', new_entry):
        print(f"New scale value:{new_entry} mm/pixel")
    else:
        print("Scale input not valid")
        image_scale_entry.delete(0,'end')
        image_scale_entry.insert(0, "1.0")
        
    scale_subplot()

def new_origin_entry(event):

    new_entry = origin_entry.get()
    if re.match(r'^-?\d+(\.\d+)?\s*,\s*\-?\d+(\.\d+)?$', new_entry):
        print(f"New origin value: {new_entry} [x,y]")
    else:
        print("Scale input not valid")
        origin_entry.delete(0,'end')
        origin_entry.insert(0, "0.0 , 0.0")
    
    scale_subplot()

def on_toolmanager_tool_change(event):
    active_tool = event.tool_name
    if active_tool == 'pan':
        print("Pan tool is active.")
    elif active_tool == 'zoom':
        print("Zoom tool is active")

# Function to update the plot based on mm/pixel input and origin offset
def scale_subplot():
    global original_xlim, original_ylim, color_map, white_point, image_origin, image_scale

    print("HEJ")

    #Origin offset, Expression to extract y and x values. Example:(x = "0.0",y = "0.0")
    match = re.match(r'^(-?\d+(\.\d+)?)\s*,\s*(-?\d+(\.\d+)?)$',origin_entry.get())
    if match:
        # Extract and convert the first and second values to floats
        image_origin = [float(match.group(1)), float(match.group(3))]
    else:
        image_origin = [0,0]
    ax_coord = []
    ax.clear()

    image_scale = float(image_scale_entry.get())

    print(f"New scale: {image_scale} mm/pixel, New origin offset: {image_origin} mm")
    #calculate the xy axis based on origo and mm/pixel
    #X-axis
    if img is not None:  
        ax_coord.append(image_origin[0] - (img.shape[1]*image_scale/2))
        ax_coord.append(image_origin[0] + (img.shape[1]*image_scale/2))
        #Y-axis
        ax_coord.append(image_origin[1] - (img.shape[0]*image_scale/2))
        ax_coord.append(image_origin[1] + (img.shape[0]*image_scale/2))
        ax.imshow(img, extent=(ax_coord[0], ax_coord[1], ax_coord[2], ax_coord[3]),cmap=color_map, vmax=white_point)
        original_xlim = ax.get_xlim()
        original_ylim = ax.get_ylim()

    canvas.draw()

# Function to update the plot based on mm/pixel input and origin offset
def clear_point_plot():
    global color_map, white_point

    current_xlim = ax.get_xlim()
    current_ylim = ax.get_ylim()
    
    ax_coord = []
    ax.clear()

    if img is not None:  
        ax_coord.append(image_origin[0] - (img.shape[1]*image_scale/2))
        ax_coord.append(image_origin[0] + (img.shape[1]*image_scale/2))
        #Y-axis
        ax_coord.append(image_origin[1] - (img.shape[0]*image_scale/2))
        ax_coord.append(image_origin[1] + (img.shape[0]*image_scale/2))
        ax.imshow(img, extent=(ax_coord[0], ax_coord[1], ax_coord[2], ax_coord[3]),cmap=color_map, vmax=white_point)

    ax.set_xlim(current_xlim)
    ax.set_ylim(current_ylim)
    canvas.draw()

def is_zoom_mode(toolbar):
    # Check if the Zoom button is currently active (indicates zoom mode)
    return toolbar.mode == "zoom rect"

def is_pan_mode(toolbar):
    # Check if the Pan button is currently active (indicates pan mode)
    return toolbar.mode == "pan/zoom"

# Function to handle mouse click events
def on_click(event):
    global toolbar, points
    zoom_state = is_zoom_mode(toolbar)
    pan_state = is_pan_mode(toolbar)


    print(f"Zoom mode: {zoom_state}")
    print(f"Zoom mode: {zoom_state}")

    if zoom_state or pan_state:
        print("Measurement inhibited when paning or zooming")
        return
    if event.xdata == None or event.ydata == None:
        print("invalid point data")
        return

    points.append([event.xdata, event.ydata])

    if len(points) == 2:
        #scale_subplot()  # Update the plot    
        distance = ((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2)**0.5
        ax.plot([points[0][0], points[1][0]], [points[0][1], points[1][1]], 'r-',linewidth=1)
        legend_text = f'Measurement: {distance:.2f} mm'
        ax.legend([legend_text], loc='upper center', bbox_to_anchor=(0.5, 1.06))
        plt.draw()

       # Create a line from point1 to point2
        x_values = np.linspace(points[0][0], points[1][0], num=100)
        y_values = np.linspace(points[0][1], points[1][1], num=100)
        # Extract pixel values along the line from the image
        
        #brightness_values = [img[int(y), int(x)] for x, y in zip(x_values, y_values)]
        #print(x_values)
        #print(brightness_values)
        #ax.plot(brightness_values)

        print(f"Distance: {distance:.2f} mm")
    if len(points) > 2:
        points = []
        clear_point_plot()
        points.append([event.xdata, event.ydata])

    print(points)
    ax.plot(event.xdata, event.ydata, 'ro',markersize=2)  # Plot the selected point
    canvas.draw()

def restore_zoom():
    # You can perform zoom or pan operations here if needed
    # Update your plot here as well if necessary
    ax.set_xlim(original_xlim)
    ax.set_ylim(original_ylim)
    # Redraw the canvas to restore the original view
    canvas.draw()

# Create a button to open an image
open_button = tk.Button(root, text="Open Image", command=open_image)
open_button.pack()

# Create an Entry widget for mm/pixel input
image_scale_label = tk.Label(root, text="Scale [mm/pixel]")
image_scale_label.pack()
image_scale_entry = Entry(root)
image_scale_entry.pack()
image_scale_entry.insert(0, "1.0")  # Default value
image_scale_entry.bind("<Return>", new_scale_entry)

# Create a label and entry for Origin input
origin_label = tk.Label(root, text="Origin offset: X [mm] , Y [mm]")
origin_label.pack()
origin_entry = tk.Entry(root, validate="key")
origin_entry.insert(0, "0.0 , 0.0")
origin_entry.pack()
origin_entry.bind("<Return>", new_origin_entry)


# Create a button to update the view
update_button = tk.Button(root, text="Restore Zoom", command=restore_zoom)
update_button.pack()

# Create a Figure with a specific size (width, height) in inches
fig = Figure(figsize=(8, 6))  # Adjust the width and height as needed
# Reduce the padding around the subplot
fig.subplots_adjust(top=0.95, bottom=0.05, left=0.1, right=0.95)
# Add a subplot to the figure
ax = fig.add_subplot(111)

# Create a canvas for Matplotlib figure
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Create Matplotlib navigation toolbar
toolbar = NavigationToolbar2Tk(canvas, root)
canvas.get_tk_widget().pack(side=tk.TOP)
toolbar.update()

# Connect the mouse click event to the function
canvas.mpl_connect('button_press_event', on_click)
scale_subplot()


# Start the Tkinter main loop
root.mainloop()
