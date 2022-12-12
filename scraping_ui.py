# Import necessary modules
import tkinter as tk
import csv
from tkinter import filedialog

# Create a Tkinter window
window = tk.Tk()
window.title("CSV Reader")

# Function to load and read a CSV file
def load_csv():
    # Ask the user to select a CSV file to load
    filename = filedialog.askopenfilename(title="Select a CSV file", filetypes=[("CSV files", "*.csv")])
    if not filename:
        return

    # Clear the current contents of the text widget
    text_widget.delete("1.0", "end")

    # Open the selected CSV file
    with open(filename, "r") as file:
        reader = csv.reader(file)
        # Iterate over rows in the CSV file
        for row in reader:
            # Add each row to the text widget
            text_widget.insert("end", ",".join(row) + "\n")

# Create a button to load a CSV file
button = tk.Button(window, text="Load CSV", command=load_csv)
button.pack(side="top")

# Create a text widget to display the CSV file
text_widget = tk.Text(window)
text_widget.pack(side="bottom")

# Start the Tkinter event loop
window.mainloop()
