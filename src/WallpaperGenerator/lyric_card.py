from PIL import Image, ImageDraw, ImageFont
from utils.lyric_finder import LyricFinderClient
from utils.images import generate_text_image, find_darkest_color

def create_lyric_image(display, artist_name, song_name, colors, cover_image):
    """
    Create a lyric card image with the provided text and colors.

    This function generates a lyric card image with the given text and colors.
    The final image is then saved as a PNG file.

    Args:
        display (tuple): A tuple containing the display's width and height (width, height).
        text (str): The text to be displayed on the lyric card.
        colors (list): A list of two colors used to create the background.
    """
    print("creating lyric image")
    width = int(display[0])
    height = int(display[1])
    lf = LyricFinderClient()

    # Create a color background using the dominant color
    background_color = colors[0].rgb


    background_image = Image.new('RGB', (width, height), background_color)

    # Get the relevant lyrics for the song
    lyric = lf.get_lyric(artist_name + " " + song_name)

    if not lyric:
        raise Exception("Lyrics not found.")

    lyric = lf.find_most_relevant_part(lyric).upper()

    paste_album_image(background_image, cover_image, song_name, artist_name)


    text = generate_header_text_image(song_name, artist_name, colors, display)


    x = background_image.width // 6 + cover_image.width // 2 - text.width // 2
    y = background_image.height // 2 + cover_image.height // 2 + text.height // 2

    #paste the text on the image on x,y position
    background_image.paste(text, (x, y), mask = text)


    lyric_box = generate_lyric_box(display, lyric, colors)


    #create an image with the lyrics

    #coordinates to place the lyric box on the right side of the image, without going out of bounds
    x = background_image.width // 2 + (background_image.width // 2 - lyric_box.width) // 2
    y = background_image.height // 2 - lyric_box.height // 2

    #paste the lyric box on the image
    background_image.paste(lyric_box, (x, y), mask = lyric_box)
    
    background_image.save("ImageCache/finalImage.png")




    



def paste_album_image(background_image, cover_image, song_title, artist_name):
    """
    Paste the album cover image on the left side of the background image.

    This function pastes the album cover image on the left side of the background image.

    Args:
        background_image (PIL.Image): The background image to paste the album cover on.
        cover_image (PIL.Image): The album cover image to be pasted.
    """

    # Calculate the position to paste the album cover image
    x = background_image.width // 6
    y = background_image.height // 2 - cover_image.height // 2

    # Paste the album cover image on the background image
    background_image.paste(cover_image, (x, y))



def generate_header_text_image(song_name, artist_name, colors, display):
    """
    Generate a text image with the song title and artist name, centered on the display.
    
    Args:
        songTitle (str): The title of the currently playing song.
        artistName (str): The name of the artist of the currently playing song.
        colors (list): A list of two color objects.
        display (tuple): The dimensions of the display.
        
    Returns:
        Image: A new image with the song title and artist name, centered on the display."""
    width = int(display[0])
    height = int(display[1])
    # Setup Text: check if the first color is too light or too dark
    textColor = colors[0].rgb

    #if the color is too light, make the text black, otherwise make it white
    if (textColor[0]*0.299 + textColor[1]*0.587 + textColor[2]*0.114) > 186:
        textColor = (int(0), int(0), int(0))
    else:
        textColor = (int(255), int(255), int(255))

    #create a new image with the name of the song and the artist, and transparent background
    text = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    #create a draw object
    draw = ImageDraw.Draw(text)
    #set the font
    myFont = ImageFont.truetype("./fonts/Rubik.ttf", 40)
    #draw the text in the center of the display


    draw.text((0,0), (song_name + "\n" + artist_name), font = myFont, fill = (textColor[0],textColor[1],textColor[2]), align="center")
    #save the text image as 'text.png'
    
    cropped = text.crop(text.getbbox())


    
    return cropped

def generate_lyric_box(display, lyric, colors):
    """
    Generate a text image with the song title and artist name, centered on the display.
    
    Args:
        songTitle (str): The title of the currently playing song.
        artistName (str): The name of the artist of the currently playing song.
        colors (list): A list of two color objects.
        display (tuple): The dimensions of the display.
        
    Returns:
        Image: A new image with the song title and artist name, centered on the display."""
    width = int(display[0])
    height = int(display[1])
    # Setup Text: check if the first color is too light or too dark
    textColor = colors[0].rgb

    #if the color is too light, make the text black, otherwise make it white
    if (textColor[0]*0.299 + textColor[1]*0.587 + textColor[2]*0.114) > 186:
        textColor = (int(0), int(0), int(0))
    else:
        textColor = (int(255), int(255), int(255))


    #create a new image with the name of the song and the artist, and transparent background
    text = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    #create a draw object
    draw = ImageDraw.Draw(text)
    #set the font
    myFont = ImageFont.truetype("./fonts/Rubik.ttf", 40)
    #draw the text in the center of the display as bold
    draw.text((0,0), 
              lyric, font = myFont, 
              fill = (textColor[0],textColor[1],textColor[2]), 
              align="center", 
              stroke_width=2)
    
    cropped = text.crop(text.getbbox())

    #if the text is larger than half the display, resize it to fit
    if cropped.width > width // 2:
        cropped = cropped.resize((width // 2 - width // 100
                                  , cropped.height), Image.LANCZOS)
    
    return cropped