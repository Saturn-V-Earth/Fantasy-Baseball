import pyxel

# Initialize Pyxel with a window size of 160x120
pyxel.init(160, 120)

# Load an image file into image bank 0 at position (0, 0)
pyxel.images[0].load(0, 0, r"C:\Users\mcurt\OneDrive\Pictures\OIP_resized.png")

# Define the update function
def update():
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

# Define the draw function
def draw():
    pyxel.cls(0)
    # Draw the image from image bank 0 at position (10, 10) on the screen
    pyxel.blt(0, 0, 0, 0, 0, 200, 200)

# Run the Pyxel application
pyxel.run(update, draw)
