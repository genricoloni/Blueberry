from PIL import Image, ImageDraw
import random
from utils.images import generate_text_image, find_darkest_color, paste_and_save_album_image

def generate_gradient_image(colors, display, album_image_width, song_title, artist_name, image):
    """
    Generate a gradient image based on the colors of the album image.
    
    Args:
        colors (list): A list of two color objects. Each color should have an RGB attribute.
        display (tuple): A tuple containing the display's width and height (width, height).
        album_image_width (int): The width of the album cover image.
        song_title (str): The title of the current song.
        artist_name (str): The name of the artist.
        image (PIL.Image): The album cover image.

    Returns:
        None: The function saves the final image to the disk instead of returning it.
    """
    # Randomly decide between standard or centered gradient
    if random.choice([True, False]):
        # Generate standard gradient background
        bg = create_standard_gradient(colors, display)
        # Generate text to overlay on the gradient
        text = generate_text_image(song_title, artist_name, colors, display)
    else:
        # Generate centered gradient background
        bg = create_centered_gradient(colors, display, album_image_width)
        # Generate text with the darkest color
        text = generate_text_image(
            song_title, artist_name, find_darkest_color(colors), display, positionX=50, positionY=50
        )
    
    # Paste the album image and save the final image
    paste_and_save_album_image(bg, image, display, text)


def create_standard_gradient(colors, display):
    """
    Create a vertical gradient image transitioning between two colors.
    
    Args:
        colors (list): A list of two color objects with RGB values.
        display (tuple): A tuple containing the display's width and height (width, height).
        
    Returns:
        PIL.Image: The generated gradient image.
    """
    width, height = int(display[0]), int(display[1])
    gradient = Image.new('RGB', (width, height))

    draw = ImageDraw.Draw(gradient)
    first_color, second_color = colors[0].rgb, colors[1].rgb

    # Draw vertical gradient by interpolating between the two colors
    for i in range(height):
        color = (
            int(first_color[0] + (second_color[0] - first_color[0]) * i / height),
            int(first_color[1] + (second_color[1] - first_color[1]) * i / height),
            int(first_color[2] + (second_color[2] - first_color[2]) * i / height)
        )
        draw.line((0, i, width, i), fill=color)

    return gradient


def create_centered_gradient(colors, display, album_image_width):
    """
    Create a radial gradient centered on the screen, with ellipses expanding outwards.
    
    Args:
        colors (list): A list of two color objects with RGB values.
        display (tuple): A tuple containing the display's width and height (width, height).
        album_image_width (int): The width of the album cover image.

    Returns:
        PIL.Image: The generated centered gradient image.
    """
    width, height = int(display[0]), int(display[1])
    ellipses = 300
    min_dim = min(width, height)

    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)

    # Adjust the number of ellipses based on display dimensions
    ellipses = int(ellipses * (min_dim / max(width, height)))
    optimal_width = int(min_dim / ellipses) + 2

    for i in range(ellipses):
        if i / ellipses * min(width, height) < album_image_width / 2:
            continue

        radius = int((i / ellipses) * min(width, height))
        color = calculate_gradient_color(radius, 0, min(width, height), colors)
        draw.ellipse(
            [(width / 2 - radius, height / 2 - radius), (width / 2 + radius, height / 2 + radius)],
            width=optimal_width, outline=color
        )

    return gradient


def calculate_gradient_color(radius, start_radius, end_radius, colors):
    """
    Calculate the interpolated color for the current position in the gradient.

    Args:
        radius (int): The current radius of the ellipse.
        start_radius (int): The starting radius (typically 0).
        end_radius (int): The maximum radius (typically the height or width of the display).
        colors (list): A list of two color objects with RGB values.
    
    Returns:
        tuple: A tuple representing the calculated RGB color at the given position.
    """
    position = (radius - start_radius) / (end_radius - start_radius)
    color = []

    for i in range(3):  # Iterate over RGB channels
        color_value = int(colors[0].rgb[i] + (colors[1].rgb[i] - colors[0].rgb[i]) * position)
        color_value = max(0, min(255, color_value))  # Ensure the value is within 0-255
        color.append(color_value)

    return tuple(color)
