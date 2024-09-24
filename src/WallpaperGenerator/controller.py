"""
Module for generating a controller image based on the provided song details.
"""

from PIL import Image, ImageDraw, ImageFont
from lxml import etree
from cairosvg import svg2png

#pylint: disable=import-error, too-many-arguments, too-many-positional-arguments, too-many-locals, c-extension-no-member
def create_controller_image(song_title, artist_name, colors, display, song_length, album_image):
    """
    Create a controller image based on the provided song details.
    
    Args:remove
        song_title (str): The title of the song.
        artist_name (str): The name of the artist.
        image_url (str): The URL of the album image.
        display (tuple): The dimensions of the display.
        song_length (int): The length of the song in milliseconds.
        album_image (Image): The album image.
        
    Returns:
        Image: A controller image based on the provided song details.
    """
    # Calculate minutes and seconds from song length
    minutes = int(song_length / 60000)
    seconds = int((song_length % 60000) / 1000)

    # Get display dimensions
    width = int(display[0])
    height = int(display[1])

    # Set background color
    background_color = colors[0].rgb

    # Create a new image with the specified dimensions and background color
    controller_image = Image.new('RGB', (width, height), background_color)

    # Create a draw object for drawing on the image
    draw = ImageDraw.Draw(controller_image)

    # Set the font for text
    font = ImageFont.truetype("./fonts/Rubik.ttf", 40)

    # Paste the album image onto the controller image
    controller_image.paste(album_image, (width // 2 - album_image.width // 2, height // 6))

    # Modify the fill color of specified paths in an SVG and convert it to PNG
    fill_with_secondary_color(colors[1].rgb, 200, 200)

    # Open the pause button image
    pause_button = Image.open("ImageCache/pause-button.png").convert("RGBA")

    # Generate text image with song title and artist name
    text = generate_centered_text_image(song_title, artist_name, colors, display)

    # Paste the pause button image onto the controller image
    controller_image.paste(pause_button,
                           (width // 2 - pause_button.width // 2,
                            height // 6 + album_image.height + 250),
                           mask=pause_button)

    # Draw a rectangle below the pause button
    draw.rectangle([width//6,
                    height//6 + album_image.height + 210,
                    width - width//6 + 100, height//6 + album_image.height + 215],
                    fill=colors[1].rgb)

    # Draw the song length text
    text_offset = (1, 1)
    draw.text((width//6 - 120 + text_offset[0],
               height//6 + album_image.height + 190 + text_offset[1]),
               "00:00", font=font, fill=(0, 0, 0))  # Draw black shadow

    draw.text((width//6 - 120,
               height//6 + album_image.height + 190),
               "00:00", font=font, fill=colors[1].rgb)  # Draw desired color on top

    duration = f"{minutes if minutes > 9 else '0' + str(minutes)}"
    duration += f":{seconds if seconds > 9 else '0' + str(seconds)}"
    draw.text((width - width//6 + 100 + text_offset[0],
                height//6 + album_image.height + 190 + text_offset[1]),
                duration,
                font=font, fill=(0, 0, 0))  # Draw black shadow
    draw.text((width - width//6 + 100,
                    height//6 + album_image.height + 190),
                    duration,
                    font=font, fill=colors[1].rgb)  # Draw desired color on top

    # Paste the text image onto the controller image
    controller_image.paste(text,
                           (width // 2 - text.width // 2,
                            height // 6 + album_image.height + 100),
                            mask=text)

    # Save the final controller image
    controller_image.save("ImageCache/finalImage.png")



def fill_with_secondary_color(color, width, height):
    """
    Modifies the fill color of specified paths in an SVG and converts it to PNG.

    Args:
        color: A tuple representing the desired color (RGB values).
        width: The desired output image width.
        height: The desired output image height.
        svg_filename: The filename of the SVG file to modify.
    """

    with open("src/img/pause-button.svg", 'rb') as f:  # Open in binary mode
        svg_data = f.read()

    #open as xml file
    svg = etree.fromstring(svg_data)

    #find all the 'fill' attributes and change them to the hex value of the color
    for element in svg.iter():
        if 'fill' in element.attrib:
            element.attrib['fill'] = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"

    #save the modified svg
    with open("ImageCache/modified_pause-button.svg", 'wb') as f:
        f.write(etree.tostring(svg))

    #convert the svg to a png image
    svg2png(url="ImageCache/modified_pause-button.svg",
            write_to="ImageCache/pause-button.png",
            output_width=width, output_height=height,
            background_color="transparent")



def generate_centered_text_image(song_title, artist_name, colors, display):
    """
    Generate a text image with the song title and artist name, centered on the display.
    
    Args:
        song_title (str): The title of the currently playing song.
        artist_name (str): The name of the artist of the currently playing song.
        colors (list): A list of two color objects.
        display (tuple): The dimensions of the display.
        
    Returns:
        Image: A new image with the song title and artist name, centered on the display."""
    width = int(display[0])
    height = int(display[1])
    # Setup Text: check if the first color is too light or too dark
    text_olor = colors[0].rgb

    #if the color is too light, make the text black, otherwise make it white
    if (text_olor[0]*0.299 + text_olor[1]*0.587 + text_olor[2]*0.114) > 186:
        text_olor = (int(0), int(0), int(0))
    else:
        text_olor = (int(255), int(255), int(255))

    #create a new image with the name of the song and the artist, and transparent background
    text = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    #create a draw object
    draw = ImageDraw.Draw(text)
    #set the font
    my_ont = ImageFont.truetype("./fonts/Rubik.ttf", 40)
    #draw the text in the center of the display
    draw.text((0,0),
              (song_title + "\n" + artist_name),
              font = my_ont,
              fill = (text_olor[0],text_olor[1],text_olor[2]),
              align="center")
    #save the text image as 'text.png'

    cropped = text.crop(text.getbbox())

    return cropped
