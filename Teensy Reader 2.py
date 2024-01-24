# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 21:00:31 2024

@author: Josiah Hamilton
"""

import tkinter as tk
from tkinter import filedialog, messagebox, Canvas
import matplotlib.pyplot as plt
import serial.tools.list_ports
import time
import csv
from datetime import datetime

# Variable to store the sampled data
sampled_data = []
array_counter = 0

def draw_bar_chart(values, sample_name, plot=False):
    canvas.delete("all")  # Clear the canvas
    num_values = len(values)
    max_intensity = max(values) * 1.01

    # Calculate the dynamic bar width
    bar_width = canvas_width / num_values

    for i in range(num_values):
        x1 = i * bar_width
        x2 = (i + 1) * bar_width
        y1 = canvas_height - (values[i] / max_intensity) * canvas_height
        y2 = canvas_height

        canvas.create_rectangle(x1, y1, x2, y2, fill="blue")

    canvas.create_text(canvas_width / 2, canvas_height + 10, text=f"Sample: {sample_name}")

    if plot:
        plt.bar(range(num_values), values)
        plt.xlabel('Pixel')
        plt.ylabel('Intensity')
        plt.title(f'{sample_name}')
        plt.show()

def plot_chart():
    if not sampled_data:
        messagebox.showwarning("Warning", "No sample available. Take a sample first.", parent=window)
        return

    draw_bar_chart(sampled_data, sample_name, plot=True)


def read_data():
    global array_counter
    global sample_name

    selected_com_port = com_port_var.get()
    try:
        ser = serial.Serial(selected_com_port, baudrate=9600)
    except serial.SerialException:
        messagebox.showerror("Error",
                             "Failed to open the selected COM port. "
                             "Make sure the Teensy is connected properly, "
                             "or try selecting a different COM port.", parent=window)
        return

    num_values = 3648
    try:
        data = ser.read(3 * num_values)
    except serial.SerialException:
        messagebox.showerror("Error", "Failed to read data from the Teensy.", parent=window)
        ser.close()
        return

    values = []
    for i in range(0, len(data), 3):
        value = ((data[i + 1] & 0x0F) << 8) | data[i]
        values.append(value)

    array_counter += 1
    current_time = datetime.now().strftime("%d-%m-%Y %H%M%S")
    sample_name = f"Sample - {current_time}"
    print(array_counter, sample_name, ":", values)

    ser.close()

    draw_bar_chart(values, sample_name)

    # Update the sampled_data variable
    global sampled_data
    sampled_data = values

    time.sleep(0)

def save_array():
    if not sampled_data:
        messagebox.showwarning("Warning", "No sample available. Take a sample first.", parent=window)
        return

    # Open a file dialog to select the save location
    filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV Files", "*.csv")],
                                            initialfile=sample_name if sample_name else None)
    if not filename:
        return  # User canceled the save operation

    # Save the array to the selected file
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(sampled_data)

    print("Sample saved to:", filename)


def show_instructions():
    instructions = """
    Instructions:

    1. Select the COM port from the dropdown menu.
    2. Click on the 'Take Sample' button to read data from the Teensy. This will retrieve a set of values from the Teensy device.
    3. The retrieved data will be displayed in the console and shown as a graph on the screen.
    4. Click on the 'Save Sample' button to save the data as a CSV file. You can also save the graph by clicking on the save icon located in the figure window.

    Troubleshooting Tips:

    - Make sure the Teensy device is connected properly to your computer. If the correct COM port is not appearing in the drop down menu, this could mean that the device is not connected properly. Connect the device and restart the program.
    - Check the baud rate of the Teensy. It should be set to 9600.
    - Ensure that you have the required libraries installed on your computer. The required libraries are:
        - tkinter
        - serial
        - matplotlib
        - csv
        - datetime

    - If you encounter any issues, try restarting the program or the Teensy device. (Try turning it off an on again!)

    """

    messagebox.showinfo("Instructions", instructions)

# Create the main window
window = tk.Tk()
window.title("Teensy Reader")

# Create a button for instructions
instructions_btn = tk.Button(window, text="Instructions and Troubleshooting", command=show_instructions)
instructions_btn.grid(row=0, column=0, pady=5)

# Create a dropdown menu for selecting the COM port
com_ports = [port.device for port in serial.tools.list_ports.comports()]
com_port_var = tk.StringVar()
com_port_var.set(com_ports[0])  # Set the default COM port
com_port_label = tk.Label(window, text="Select COM Port:")
com_port_label.grid(row=0, column=1)
com_port_menu = tk.OptionMenu(window, com_port_var, *com_ports)
com_port_menu.grid(row=0, column=2, pady=10)

# Create a label for functions
functions_label = tk.Label(window, text="Functions:")
functions_label.grid(row=0, column=3, pady=10)

# Create a button for reading data
read_data_btn = tk.Button(window, text="Take New Sample", command=read_data)
read_data_btn.grid(row=0, column=4, padx=5, pady=5)

# Create a button for saving the array
save_array_btn = tk.Button(window, text="Save Current Sample", command=save_array)
save_array_btn.grid(row=0, column=5, padx=5, pady=5)

# Create a button for plotting the chart
plot_chart_btn = tk.Button(window, text="Plot Chart", command=plot_chart)
plot_chart_btn.grid(row=0, column=6, padx=5, pady=5)

# Create a canvas for drawing the bar chart
canvas_width = 1000
canvas_height = 300
canvas = Canvas(window, width=canvas_width, height=canvas_height, bg="white")
canvas.grid(row=1, column=0, columnspan=7, pady=10)

# Start the Tkinter event loop
window.mainloop()
