from PIL import Image, ImageDraw
import random
from utils.images import generate_text_image, find_darkest_color, paste_and_save_album_image

def generate_gradient_image(colors, display, album_image_width, song_title, artist_name, image):
    """
    Generate a gradient image based on the colors of the album image.
    
    Args:
        colors (list): A list of two color objects.
        display (tuple): The dimensions of the display.
        album_image_width (int): The width of the album image.
        
    Returns:
        Image: A gradient image with the colors of the album image.
    """

    if random.choice([True, False]):
        # standard gradient
        bg = create_standard_gradient(colors, display)
        text = generate_text_image(song_title, 
                                   artist_name, 
                                   colors,
                                   display)
    else:   
        bg = create_centered_gradient(colors, display, album_image_width)
        text = generate_text_image(song_title, 
                artist_name, 
                find_darkest_color(colors),
                    display,
                    positionX = 50,
                    positionY = 50)
        
    paste_and_save_album_image(bg, image, display, text)


def create_standard_gradient(colors, display):
    """
    Generate a gradient image based on the colors of the album image.
    
    Args:
        colors (list): A list of two color objects.
        display (tuple): The dimensions of the display.
        
    Returns:
        Image: A gradient image with the colors of the album image.
    """
    # Create a gradient image with the colors of the album image
    width = int(display[0])
    height = int(display[1])
    gradient = Image.new('RGB', (width, height))

    # Create a draw object
    draw = ImageDraw.Draw(gradient)

    # The first color will be the first color of the album image
    firstColor = colors[0].rgb
    # The second color will be the second color of the album image
    secondColor = colors[1].rgb

    # Draw the gradient
    for i in range(height):
        draw.line((0, i, width, i), fill = (int(firstColor[0] + (secondColor[0] - firstColor[0]) * i / height), int(firstColor[1] + (secondColor[1] - firstColor[1]) * i / height), int(firstColor[2] + (secondColor[2] - firstColor[2]) * i / height)))

    return gradient

def create_centered_gradient(colors, display, album_image_width):

    width = int(display[0])
    height = int(display[1])

    # determine the number of ellipses to draw
    ellipses = 300

    # Create a new image with the dimensions of the display
    gradient = Image.new('RGB', (width, height))

    # Create a draw object
    draw = ImageDraw.Draw(gradient)

    minDim = min(width, height)
    maxDim = max(width, height)
    # Calculate the optimal number of ellipses
    ellipses = int(ellipses * (minDim / maxDim))

    #find the optimal width for the ellipses to be drawn
    optimalWidth = int(minDim / ellipses)+2

    # Draw the ellipses
    for i in range(ellipses):
        #skip all the ellipses that would be drawn inside the album image
        if i / ellipses * min(width, height) < album_image_width/2:
            continue
        # Calculate the radius of the current ellipse
        radius = int((i / ellipses) * min(width, height))
        # Calculate the color for the current ellipse
        color = calculate_gradient_color(radius, 0, min(width, height), colors)
        # Draw the ellipse
        draw.ellipse([(width / 2 - radius, height / 2 - radius), (width / 2 + radius, height / 2 + radius)], width=optimalWidth, outline=color)

    return gradient


def calculate_gradient_color(radius, startRadius, endRadius, colors):

    position = (radius - startRadius) / (endRadius - startRadius)

    color = []

    for i in range(3):
        # Calculate the color value for the current position
        colorValue = int(colors[0].rgb[i] + (colors[1].rgb[i] - colors[0].rgb[i]) * position)
        # Ensure the color value is within the valid range
        colorValue = max(0, min(255, colorValue))
        # Update the color list with the new value
        color.append(colorValue)

    #make a tuple with the color values
    color = (color[0], color[1], color[2])

    return color