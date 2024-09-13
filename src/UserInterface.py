from tkinter import *
from tkinter import ttk

# declare Variables
main_window_dimension = "960x520"
main_window_name = "TwitchChat"
can_resize = False

# declaring colors from palette
blue_1 = "#1E2328"
blue_2 = "#2A2E34"
blue_3 = "#3B3F45"
yellow_1 = "#F5B301"
yellow_2 = "#FED053"


# creates a Tk() object
master = Tk()
canvas = Canvas()

# Function to create a rounded rectangle on a canvas
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """Draws a rectangle with rounded corners."""
    points = [
        (x1 + radius, y1), (x2 - radius, y1), # Top edge
        (x2, y1), (x2, y1 + radius), # Top-right corner
        (x2, y2 - radius), (x2, y2), # Right edge
        (x2 - radius, y2), (x1 + radius, y2), # Bottom-right corner
        (x1, y2), (x1, y2 - radius), # Bottom-left corner
        (x1, y1 + radius), (x1, y1) # Left edge
    ]

    return canvas.create_polygon(points, smooth=True, **kwargs)
 

#sets all parameters for main window
master.geometry(main_window_dimension)
master.title(main_window_name)
master.resizable(can_resize,can_resize)

# create a Canvas widget and add it to the window
canvas = Canvas(master, bg=blue_1)
canvas.pack(fill=BOTH, expand=True)  # Pack the canvas to fill the window

# draw a rectangle on the canvas
create_rounded_rectangle(canvas,20, 20, 20 + 241, 20 + 479 ,radius= 30, fill=blue_2)
create_rounded_rectangle(canvas,289, 29, 289 + 631, 29 + 441 ,radius= 30, fill=blue_2)



mainloop()