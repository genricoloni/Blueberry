import io
import sys
import threading
import requests, colorgram, os, platform
import time
import spotipy.util as util
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from spotipy.oauth2 import SpotifyOAuth
import random, json
from cachetools import TTLCache
import math
from urllib.parse import urlencode
from PIL import Image
from cairosvg import svg2png
from lxml import etree

# Get creds please enter your creds in creds.txt

global spotify_token, client_id, client_secret, username, display, original_wallpaper, command, modes, environment
client_id = ""
client_secret = ""
spotify_token = ""
username = ""
scope = "user-read-currently-playing"
display = ""
cacheOn = True
environment = ''
modes = ["gradient", "blurred", "waveform", "albumImage", "controllerImage"]
#set up an array of available environments and commando to test
availableEnvironment = [
    {'envName': 'gnome',
     'testCommand' : 'gnome-session',
     'command' : 'gsettings set org.gnome.desktop.background picture-uri ' if ('dark' if 'dark' in (os.popen("gsettings get org.gnome.desktop.interface gtk-theme").read()) else 'light') == 'light' else 'gsettings set org.gnome.desktop.background picture-uri-dark '
     }]


cache = TTLCache(maxsize=100, ttl=3600)


#check if gnome is in dark mode or light mode

#set the command to change the wallpaper: it changes depending on the mode

#get the path of the original wallpaper
original_wallpaper = os.popen("gsettings get org.gnome.desktop.background picture-uri-dark").read()

def getEnvironment():
    """
    Get the environment of the user, and the command to change the wallpaper
    
    Returns:
        None: the environment and the command are stored in global variables"""
    global environment, command

    for env in availableEnvironment:
        result = os.popen(env['testCommand']).read().strip()
        if not result:
            environment, command = env['envName'], env['command']
            break

def get_token_refresh():
    """
    Get the Spotify refresh token from the cache file

    Returns:
        str: The Spotify refresh token
    """
    filename = f".cache-{username}"
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data['refresh_token']
    except:
        return None
    

def write_token_refresh(refresh_token):
    """
    Write the Spotify refresh token to the cache file

    Args:
        refresh_token (str): The Spotify refresh token to write to the cache file

    Returns:
        None: The Spotify refresh token is written to the cache file
    """
    filename = f".cache-{username}"
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            data['refresh_token'] = refresh_token
            with open(filename, 'w') as file:
                json.dump(data, file)
    except:
        return None
    

def write_token(spotify_token):
    """
    Write the Spotify token to the cache
    
    Args:
        spotify_token (str): The Spotify token to write to the cache file
        
    Returns:
        None: The Spotify token is written to the cache file"""
    filename = f".cache-{username}"
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            data['access_token'] = spotify_token
            with open(filename, 'w') as file:
                json.dump(data, file)
    except:
        return None


def token_refresh():
    """
    Refresh the Spotify token using the refresh token

    Returns:
        str: The new Spotify token
    """
    refresh_token = get_token_refresh()
    url = "https://accounts.spotify.com/api/token"

    if refresh_token:
        payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, headers=headers, data=urlencode(payload))

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the new access and refresh tokens from the response
            response_data = response.json()
            spotify_token = response_data.get('access_token')
            new_refresh_token = response_data.get('refresh_token', refresh_token)  # Use the same refresh token if a new one isn't provided

            # Here you would update your storage mechanism with the new tokens
            # Since Python scripts don't have direct access to browser's localStorage,
            # you need to adapt this part to your application's environment.
            print("New access token:", spotify_token)
            print("New refresh token:", new_refresh_token)

            # Write the new tokens to the cache
            write_token(spotify_token)
            write_token_refresh(new_refresh_token)

            return spotify_token

            
        else:
            print("Failed to refresh the token, status code:", response.status_code)
            print("Trying to authenticate again")
            spotify_authenticate()
            return 
    else:
        print("No refresh token found, trying to authenticate again")
        spotify_authenticate()
        return


def  init():
    """
    Initialize the program, by getting the credentials, the environment, and the original wallpaper

    Returns:
        None: the credentials, the environment, and the original wallpaper are stored in global variables"""
    
    # Get variables from the credentials file
    datadict = get_variables()
    #check if the environment is available
    getEnvironment()

    #check if 'src/songCheck.txt' exists, if not create it
    if not os.path.exists("src/songCheck.txt"):
        f = open("src/songCheck.txt", "w")
        f.close()

    #check if 'ImageCache' directory exists, if not create it
    if not os.path.exists("ImageCache"):
        os.mkdir("ImageCache")

    if not os.path.exists("src/savedConfigs"):
        os.mkdir("src/savedConfigs")

    # Declare global variables to be used in other functions
    global client_secret, colors, client_id, username, display

    # Assign values from the data dictionary to the global variables
    client_id = datadict["client_id"]
    client_secret = datadict["client_secret"]
    username = datadict["spot_username"]
    display = os.popen("xrandr").read().split("\n")[2].split()[0].split("x")
    #display = ['yourWidth', 'yourHeight']
    # DON'T REMOVE THE ''

    # Authenticate with Spotify API
    spotify_authenticate()



# to refactor without using spotipy library
def spotify_authenticate():
    """
    Authenticate with the Spotify API using the credentials from the creds.txt file.
    The authentication token is stored in the global variable spotify_token.
    """
    # Get the Spotify access token for authentication
    global spotify_token
    token = util.prompt_for_user_token(username, scope, client_id, client_secret, "https://www.google.com/")
    if token:
        spotify_token = token
    else:
        print("Couldn't get proper Spotify authentication")
        exit()



def get_variables():
    """
    Get the variables from the creds.txt file.

    Returns:
        dict: A dictionary containing the variables from the creds.txt file.

    """
    dicti = {}
    with open('creds.txt', 'r') as file:
        content = file.readlines()
        for line in content:
            if "=" in line:
                v = line.split("=")
                if len(v) == 2:
                    dicti[v[0].strip()] = v[1].strip()
                else:
                    print("Please fill in your information on the creds.txt file")
                    exit()
        return dicti






def download_image(image_url):
    """
    Downloads an image from the given URL and stores its data in the cache.
    The image data is cached using the image URL as the key.
    
    Args:
        image_url (str): URL of the image to download.
    
    Returns:
        bytes: The image data, or None if the download fails.
    """
    
    if image_url in cache:
        return cache[image_url]
    
    try: 
        response = requests.get(image_url)
        response.raise_for_status()  # Check if the request was successful

        # Cache the image data
        image_data = response.content
        cache[image_url] = image_data

        #save the image in the ImageCache directory
        with open('ImageCache/albumImage.png', 'wb') as file:
            file.write(image_data)

        return image_data
    except requests.exceptions.RequestException as e:
        print(f"Failed to download image: {e}")
        return None


def get_song_details(spotify_token, retry_delay=2, max_retries=3):
    """
    Fetches and downloads details of the currently playing song from Spotify, including downloading the cover image.
    
    Args:
        spotify_token (str): Spotify API token.
        retry_delay (int): Time in seconds to wait before retries.
        max_retries (int): Maximum number of retries for the request.
    
    Returns:
        tuple or None: Returns a tuple with song details (name, status, local image path, artistName, songId)
                       or None if the request fails or data is incomplete.
    """
    header = {"Authorization": f"Bearer {spotify_token}"}
    url = "https://api.spotify.com/v1/me/player/currently-playing"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=header)
            status = int(response.status_code)
            song_content = response.json()

            if status == 401:
                # Token has expired, reauthenticate
                spotify_token = token_refresh()
                print("Token refreshed")
                
                continue
            
            if status == 429:
                retry_after = int(response.headers.get('Retry-After', retry_delay))
                print(f"\nRate limited. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
                continue

            # Check if the response has the necessary information
            if 'item' not in song_content or not song_content['item']:
                #print("No song information found. Retrying...")
                time.sleep(retry_delay)
                continue

            status = "paused" if 'is_playing' not in song_content or not song_content['is_playing'] else "playing"
            item = song_content['item']
            name = item.get('name')
            artistName = item['album']['artists'][0].get('name')
            imageUrl = item['album']['images'][0].get('url')  # Using the first image (usually the largest)
            songId = item.get('id')
            songLength = item.get('duration_ms')


            if not all([name, artistName, imageUrl, songId]):
                print("Incomplete song information. Retrying...")
                time.sleep(retry_delay)
                continue

            return name, status, imageUrl, artistName, songId, songLength

        except requests.exceptions.RequestException as e:
            #print(f"Request failed: {e}. Retrying in {retry_delay} seconds...")
             
            time.sleep(retry_delay)
        except KeyError as e:
            #print(f"Missing expected data: {e}. Retrying...")
            time.sleep(retry_delay)  

    print("Maximum retries reached. Exiting function.")
    return None




def create_color_background(baseWidth, baseHeight, colors):
    """
    Create a background image with two colors.
    
    Args:
        baseWidth (int): The width of the background image.
        baseHeight (int): The height of the background image.
        colors (list): A list of two colors to use for the background.
        
    Returns:
        Image: A new background image with two colors."""
    colorImageOne = Image.new('RGB', (baseWidth, int(baseHeight / 2)), colors[0].rgb)
    colorImageTwo = Image.new('RGB', (baseWidth, int(baseHeight / 2)), colors[1].rgb)

    background = Image.new('RGB', (colorImageOne.width, colorImageOne.height + colorImageTwo.height))
    background.paste(colorImageOne, (0, 0))
    background.paste(colorImageTwo, (0, colorImageOne.height))

    return background

def albumImage(display, songTitle, artistName, imageUrl):
    """
    Generate a wallpaper based on the album image and song details.
    
    Args:
        display (tuple): The dimensions of the display.
        songTitle (str): The title of the currently playing song.
        artistName (str): The name of the artist of the currently playing song.
        imageUrl (str): The URL of the song's cover image.
        
    Returns:
        None: The generated wallpaper is saved to the 'ImageCache' directory."""
    image = setup_album_image(display, imageUrl)
    text = generate_text_image(songTitle, artistName, getColors(imageUrl), display)

    background = create_color_background(int(display[0]), int(display[1]), getColors(imageUrl))

    paste_and_save_album_image(background, image, display, text)
    


def calculate_relative_luminance(color):
    """
    Calculate the relative luminance of a color using the formula:
    L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    
    Args:
        color (Color): A color object.
        
    Returns:
        float: The relative luminance of the color."""
    r, g, b = color.rgb

    # Calculate relative luminance using the specified formula
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def calculate_contrast_ratio(color1, color2):
    # Calculate relative luminance for both colors
    luminance1 = calculate_relative_luminance(color1)
    luminance2 = calculate_relative_luminance(color2)

    # Ensure that the lighter color's luminance is in luminance1
    if luminance2 > luminance1:
        luminance1, luminance2 = luminance2, luminance1

    # Calculate contrast ratio with "+ 0.05" for adjustment
    return (luminance1 + 0.05) / (luminance2 + 0.05)

def getColors(imageUrl):
    """
    Get the two most prominent colors from the album image.
    
    Returns:
        list: A list of two color objects extracted from the album image.
        """
    
    #retrieve the image from the cache
    image = get_image_from_cache(imageUrl)
    image = Image.open(io.BytesIO(image))
    # Setup Background Colors
    colors = colorgram.extract('ImageCache/albumImage.png', 13)

    if len(colors) < 2:
        # In this case, the function will return
        return [colors[0], colors[0]]

    # Check if colors are too similar
    for i in range(1, len(colors)):
        if calculate_contrast_ratio(colors[0], colors[i]) >= 2:
            # Colors are different enough, so return them
            return [colors[0], colors[i]]
    else:
        return [colors[0], colors[1]]
    # For loop will end only if we run out of colors, so return the first two


def checkSong():
    """
    Get the song title from the file 'src/songCheck.txt'
    
    Returns:
        str: The song title from the file.
    """

    with open("src/songCheck.txt", "r") as f:
        return f.read().split(",")[0]
    
def get_image_from_cache(imageUrl):
    try:
        image =  cache[imageUrl]
        return image
    except KeyError:
        download_image(imageUrl)
        return cache[imageUrl]
    except:
        print("Error: couldn't get image from cache")
        return None
    
def resetSong():
    """
    Reset the song title in the file 'src/songCheck.txt'
    
    Returns:
        None: The file 'src/songCheck.txt' is reset.
    """
    with open("src/songCheck.txt", "w") as f:
        f.write("")
        f.close()



def setup_album_image(display, imageUrl):
    """
    Setup the album image for the wallpaper.
    
    Args:
        display (tuple): The dimensions of the display.
        imageUrl (str): The URL of the album image.
        
        Returns:
        Image: The album image, resized and saved to the 'ImageCache' directory.
        """
    width = int(int(display[0]) / 5)

    image = get_image_from_cache(imageUrl)
    image = Image.open(io.BytesIO(image))

    wpercent = (width/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    image = image.resize((width,hsize), Image.LANCZOS)
    return image


def generate_gradient_image(colors, display):
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

    gradient.save('ImageCache/gradient.png')
    return gradient



def generate_text_image(songTitle, artistName, colors, display, positionX = 50, positionY = 50):
    """
    Generate a text image with the song title and artist name.
    
    Args:
        songTitle (str): The title of the currently playing song.
        artistName (str): The name of the artist of the currently playing song.
        colors (list): A list of two color objects.
        display (tuple): The dimensions of the display.
        positionX (int): The x-coordinate of the text.
        positionY (int): The y-coordinate of the text.
        
    Returns:
        Image: A new image with the song title and artist name, and transparent background."""
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
    #draw the text
    draw.text((positionX,positionY), (songTitle + "\n" + artistName), font = myFont, fill = (textColor[0],textColor[1],textColor[2]))

    #save the text image
    return text


def generate_centered_text_image(songTitle, artistName, colors, display):
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
    draw.text((0,0), (songTitle + "\n" + artistName), font = myFont, fill = (textColor[0],textColor[1],textColor[2]), align="center")
    #save the text image as 'text.png'

    cropped = text.crop(text.getbbox())
    
    return cropped

def paste_and_save_album_image(bg, cover, display, text):
    """
    Paste the album image in the center of the background image and save the final image.

    Args:
        bg (Image): The background image.
        cover (Image): The album image.
        display (tuple): The dimensions of the display.
        text (Image): The text image.
    """

    width = int(display[0])
    height = int(display[1])
    # Paste the album image, bigger of 120% of the size, in the center of the gradient image
    bg.paste(cover, ((int(bg.width/2) - int(cover.width / 2)), int((bg.height/2) - int(cover.height / 2))))

    #save the final image

    background = Image.new('RGB', (width, height))
    background.paste(bg, (0, 0))
    background.paste(text, (0, 0), mask = text)
    background.save("ImageCache/finalImage.png")



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

def find_darkest_color(colors):
    """
    Find the darkest color in a list of colors.

    Args:
        colors (list): A list of color objects.

    Returns:
        Color:s: A list of color objects.

    """
    #distance from black
    distance1 = math.sqrt(colors[0].rgb[0]**2 + colors[0].rgb[1]**2 + colors[0].rgb[2]**2)
    distance2 = math.sqrt(colors[1].rgb[0]**2 + colors[1].rgb[1]**2 + colors[1].rgb[2]**2)

    if distance1 > distance2:
        return [colors[0], colors[1]]
    else:
        return [colors[1], colors[0]]


def generate_gradient_from_center(colors, display, albumImageWidth):
    """
    Generate a gradient image with the colors of the album image, from t    header = {"Authorization": f"Bearer {spotify_token}"}
    url = "https://api.spotify.com/v1/me/player/currently-playing"he center to the edges.
    
    Args:
        colors (list): A list of two color objects.
        display (tuple): The dimensions of the display.
        
    Returns:
        Image: A gradient image with the colors of the album image, from the center to the edges."""
    
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
        if i / ellipses * min(width, height) < albumImageWidth/2:
            continue
        # Calculate the radius of the current ellipse
        radius = int((i / ellipses) * min(width, height))
        # Calculate the color for the current ellipse
        color = calculate_gradient_color(radius, 0, min(width, height), colors)
        # Draw the ellipse
        draw.ellipse([(width / 2 - radius, height / 2 - radius), (width / 2 + radius, height / 2 + radius)], width=optimalWidth, outline=color)

    gradient.save('ImageCache/gradient.png')

    return gradient

def gradient(songTitle, imageUrl, artistName):
    """
    Generate a gradient wallpaper based on the song details.

    Args:
        songTitle (str): The title of the currently playing song.
        status (str): The status of the song (e.g., "playing" or "paused").
        imageUrl (str): The URL of the song's cover image.
        artistName (str): The name of the artist of the currently playing song.
        songId (str): The ID of the currently playing song.

    Returns:
        None: The generated wallpaper is saved to the 'ImageCache' directory.
    """
    # Retrieve and set-up the image from the cache using imageUrl as the key
    image = setup_album_image(display, imageUrl)

    albumImageWidth = image.width

    #choose randomly from standard or from center to the edges

    if random.choice([True, False]):
        # Create a gradient image with the colors of the album image, starting from the top to the bottom
        gradient = generate_gradient_image(getColors(imageUrl), display)
        text = generate_text_image(songTitle, artistName, getColors(imageUrl), display)

    else:
        # Create a gradient image with the colors of the album image, starting from the center to the edges
        gradient = generate_gradient_from_center(find_darkest_color(getColors(imageUrl)), display, albumImageWidth)
        text = generate_text_image(songTitle, artistName, find_darkest_color(getColors(imageUrl)), display)

    #generate the text image

    paste_and_save_album_image(gradient, image, display, text)


def resize_and_center_image(image, target_width, target_height):
    """
    Resizes an image to a target width, and centers it vertically.

    Args:
        image (Image): The image to resize.
        target_width (int): The target width of the image.
        target_height (int): The target height of the image.

    Returns:
        Image: The resized and centered image.
    """
    # Resize with preserved aspect ratio
    aspect_ratio = image.width / image.height
    new_height = target_height
    new_width = int(int(aspect_ratio) * int(new_height))
    resized_image = image.resize((int(new_width), int(new_height)), Image.LANCZOS)

    target_width = int(target_width)
    # Center the image vertically
    if new_width > target_width:
        x_offset = (new_width - target_width) // 2
        resized_and_centered_image = resized_image.crop((x_offset, 0, x_offset + target_width, new_height))
    else:
        resized_and_centered_image = resized_image

    return resized_and_centered_image


def create_blurred_background(cover_image_data, display_dimensions, blur_radius=20):
    """
    Creates a blurred background image from the cover image data.

    Args:
        cover_image_data (bytes): Image data as bytes.
        display_dimensions (tuple): Dimensions of the display (width, height).
        blur_radius (int): Radius of the Gaussian blur filter.

    Returns:
        Image: A new image with a blurred background and the album cover centered.

    """
    try:
        image = Image.open(io.BytesIO(cover_image_data))


        # Resize, crop, and blur the album image
        base_width, base_height = display_dimensions
        resized_image = resize_and_center_image(image, int(base_width)*2, int(base_height)*2)
        blurred_image = resized_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # Paste the cover image in the center
        cover_image = Image.open(io.BytesIO(cover_image_data))
        cover_width, cover_height = cover_image.size
        cover_image = cover_image.resize((int(1.2 * cover_width), int(1.2 * cover_height)), Image.LANCZOS)
        x_position = (blurred_image.width - cover_image.width) // 2
        y_position = (blurred_image.height - cover_image.height) // 2
        blurred_image.paste(cover_image, (x_position, y_position))

        return blurred_image
    except Exception as e:
        print(f"Error creating blurred background: {e}")
        return None

def blurred(cover_url, display_dimensions):
    """
    Main function to generate a blurred background with the album cover centered.

    Args:
        cover_url (str): URL of the album cover image.
        display_dimensions (tuple): Dimensions of the display (width, height).

    Returns:
        None: The generated wallpaper is saved to the 'ImageCache' directory.
    """
    cover_image_data = get_image_from_cache(cover_url)  # Make sure this returns image data as bytes
    if cover_image_data is None:
        print("Failed to retrieve cover image.")
        return

    final_image = create_blurred_background(cover_image_data, display_dimensions)
    if final_image:
        final_image_path = "ImageCache/finalImage.png"
        final_image.save(final_image_path)
        return True
    else:
        print("Failed to create blurred background.")
        return False





def get_audio_analysis(song_id):
    """SavedCo
    Get the audio analysis for a song from the Spotify API.

    Args:
        song_id (str): The ID of the song.

    Returns:
        dict or None: A dictionary with the audio analysis data, or None if the request fails.
    """


    url = f"https://api.spotify.com/v1/audio-analysis/{song_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {spotify_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:

        print("Error during request")
        return None

def extract_loudness_data(audio_analysis, duration, sample_points=100):
    """
    Extracts loudness data from the audio analysis.

    Args:
        audio_analysis (dict): Audio analysis data from the Spotify API.
        duration (float): Duration of the song in seconds.
        sample_points (int): Number of sample points for the waveform.

    Returns:
        list: A list of normalized loudness levels for the waveform.
    """
    segments = [{
        'start': segment['start'] / duration,
        'duration': segment['duration'] / duration,
        'loudness': 10 ** (segment['loudness_max'] / 20)  # Adjusted for perceptual loudness
    } for segment in audio_analysis['segments']]

    # Simplify to a fixed number of sample points for the waveform
    loudness_levels = [0] * sample_points
    for segment in segments:
        start_index = int(segment['start'] * sample_points)
        end_index = min(sample_points, int((segment['start'] + segment['duration']) * sample_points))
        for i in range(start_index, end_index):
            loudness_levels[i] = max(loudness_levels[i], segment['loudness'])

    # Normalize loudness levels
    max_loudness = max(loudness_levels, default=1)
    return [level / max_loudness for level in loudness_levels]



def generate_waveform_image(levels, display_dimensions, colors):
    """
    Generates a waveform image based on normalized loudness levels.

    Args:
        levels (list): Normalized loudness levels from audio analysis.
        display_dimensions (tuple): Dimensions of the display (width, height).
        colors (tuple): Tuple containing two RGB colors (background, waveform).

    Returns:
        PIL.Image: An image object with the waveform.
    """
    width, height = display_dimensions
    baseHeight = height  # Assuming baseHeight is used for normalization

    # Create a new image with the dimensions of the display
    image = Image.new('RGB', (width, height), colors[0].rgb)

    # Generate schema for the waveform
    schema = [(int(i / 100 * width), int((1/2 + level/2) * height)) for i, level in enumerate(levels)]
    invertedSchema = [(int(i / 100 * width), int((1/2 - level/2) * height)) for i, level in enumerate(levels)]

    # Normalize the schema to the height of the screen
    schema = [(x, int(y * (baseHeight / height))) for x, y in schema]
    invertedSchema = [(x, int(y * (baseHeight / height))) for x, y in invertedSchema]

    # Create a draw object
    draw = ImageDraw.Draw(image)

    # Draw the waveform
    for i in range(len(schema)):
        start_point = schema[i]
        end_point = (invertedSchema[i][0], schema[i][1])  # Adjusted to match start and end y-coordinates

        if abs(start_point[1] - invertedSchema[i][1]) < 32:
            draw.rounded_rectangle([invertedSchema[i][0], height/2 - 16, start_point[0]+16, height/2 + 16], fill=colors[1].rgb, radius=8)
        else:
            draw.rounded_rectangle([invertedSchema[i][0], invertedSchema[i][1], start_point[0]+16, start_point[1]], fill=colors[1].rgb, radius=8)
    # Resize the image to 60% of its size, both horizontally and vertically
    resized_image = image.resize((int(width * 0.6), int(height * 0.6)), Image.LANCZOS)


    return resized_image




def waveform(song_id, display, imageUrl, artistName, songTitle):
    """
    Generate a wallpaper with a waveform based on the audio analysis of the song.

    Args:
        song_id (str): The ID of the song.
        display (tuple): The dimensions of the display.
        imageUrl (str): The URL of the song's cover image.
        artistName (str): The name of the artist of the currently playing song.
        songTitle (str): The title of the currently playing song.

    Returns:
        None: The generated wallpaper is saved to the 'ImageCache' directory.
    """

    # Get audio analysis for the song
    audio_analysis = get_audio_analysis(song_id)
    if audio_analysis is None:
        print("Failed to retrieve audio analysis.")
        return
    
    loudness = extract_loudness_data(audio_analysis, audio_analysis['track']['duration'])
    width, height = display

    loudness = [loud * 0.75 for loud in loudness]
    
    # Generate the waveform image
    waveform_image = generate_waveform_image(loudness, (int(width), int(height)), getColors(imageUrl))
    # Generate the text image in the low-left corner
    text_image = generate_text_image(songTitle, artistName, getColors(imageUrl), display, positionX=50, positionY=int(height) - 150)
    # Create a new image with the first color of the album image as the background
    final_image = Image.new('RGB', (int(width), int(height)), getColors(imageUrl)[0].rgb)
    # Paste the waveform image in the center of the background image, centered vertically and horizontally
    final_image.paste(waveform_image, ((int(final_image.width/2) - int(waveform_image.width / 2)), int((final_image.height/2) - int(waveform_image.height / 2))))
    # Paste the text image 
    final_image.paste(text_image, (0, 0), mask=text_image)

    # Save the image
    final_image.save("ImageCache/finalImage.png")


def fillWithSecondaryColor(color, width, height):
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
    svg2png(url="ImageCache/modified_pause-button.svg", write_to="ImageCache/pause-button.png", output_width=width, output_height=height, background_color="transparent")

    



def drawController(songDetails, display, imageUrl):
    """
    Generate a .png image with the album image, the song details, and a controller with play/pause buttons and a fake progress bar.

    Args:
        songID (str): The ID of the currently playing song.
        display (tuple): The dimensions of the display.
        imageUrl (str): The URL of the song's cover image.

    Returns:
        None: The generated image is saved to the 'ImageCache' directory.
    """

    #request to spotify to get the song details
    songTitle, _, imageUrl, artistName, _, songLength = songDetails
    
    #convert the song length to minutes and seconds
    minutes = int(songLength / 60000)
    seconds = int((songLength % 60000) / 1000)

    #get the first color of the album image
    backgroundColor = getColors(imageUrl)[0].rgb

    displaySize = (int(display[0]), int(display[1]))

    #create a new image with the dimensions of the display
    controllerImage = Image.new('RGBA', displaySize, backgroundColor)

    #create a draw object
    draw = ImageDraw.Draw(controllerImage)

    #set the font
    myFont = ImageFont.truetype("./fonts/Rubik.ttf", 40)

    #put the album image horizontally centered, 30% from the top
    albumImage = setup_album_image(display, imageUrl)
    controllerImage.paste(albumImage, (displaySize[0]//2 - albumImage.width//2, displaySize[1]//6))

    fillWithSecondaryColor(getColors(imageUrl)[1].rgb, 200, 200)

    #get the pause button image 
    pauseButton = Image.open("ImageCache/pause-button.png").convert("RGBA")

    #generate the text image just below the album image
    text = generate_centered_text_image(songTitle, artistName, getColors(imageUrl), display)
    #paste the text image just below the album image, horizontally centered
    controllerImage.paste(text, (displaySize[0]//2 - text.width//2, displaySize[1]//6 + albumImage.height + 50), mask=text)
    
    #paste it horizontally centered, 60% from the top
    controllerImage.paste(pauseButton, (displaySize[0]//2 - pauseButton.width//2, displaySize[1]//6 + albumImage.height + 250), mask=pauseButton)

    #draw the progress bar, filled with the second color of the album image
    draw.rectangle([displaySize[0]//6, displaySize[1]//6 + albumImage.height + 210, displaySize[0] - displaySize[0]//6 + 100, displaySize[1]//6 + albumImage.height + 215], fill=getColors(imageUrl)[1].rgb)

    #choose a random progress for the progress bar
    progress = random.randint(0, 100)
    
    #write 00:00 at the left of the progress bar
    textOffset = (1, 1)  # Offset both horizontally and vertically

    # Draw the text with a slight offset to create a thicker appearance
    draw.text((displaySize[0]//6 - 120 + textOffset[0], displaySize[1]//6 + albumImage.height + 190 + textOffset[1]), "00:00", font=myFont, fill=(0, 0, 0))  # Draw black shadow
    draw.text((displaySize[0]//6 - 120, displaySize[1]//6 + albumImage.height + 190), "00:00", font=myFont, fill=getColors(imageUrl)[1].rgb)  # Draw desired color on top

    #write the song length at the right of the progress bar
    draw.text((displaySize[0] - displaySize[0]//6 + 100 + textOffset[0], displaySize[1]//6 + albumImage.height + 190 + textOffset[1]), f" {minutes if minutes > 9 else '0' + str(minutes)}:{seconds if seconds > 9 else '0' + str(seconds)}", font=myFont, fill=(0, 0, 0))  # Draw black shadow
    draw.text((displaySize[0] - displaySize[0]//6 + 100, displaySize[1]//6 + albumImage.height + 190), f" {minutes if minutes > 9 else '0' + str(minutes)}:{seconds if seconds > 9 else '0' + str(seconds)}", font=myFont, fill=getColors(imageUrl)[1].rgb)  # Draw desired color on top

    #TODO: add the "next" and "previous" buttons

    #save the image
    controllerImage.save("ImageCache/finalImage.png")

def createWriteLock():
    """
    Create a lock file to avoid multiple instances of the program.
    """
    with open("src/songCheck.txt.lock", "w") as f:
        f.close()

def checkWriteLock():
    """
    Check if there is a lock file present.

    Returns:
        bool: True if the lock file is present, False otherwise.
    """
    return os.path.exists("src/songCheck.txt.lock")

def searchConfig(albumCover):
    """
    Search for a configuration in the 'configs.txt' file based on the album cover.

    Args:
        albumCover (str): The URL of the album cover image.

    Returns:
        str: The configuration found in the file, or an empty string if not found.
    """
    #return a list of all the lines in the file that contain the album cover
    dir = "src/savedConfigs"
    images = []
    for file in os.listdir(dir):
        if file.startswith(albumCover):
            images.append(file)

    return images

def changeWallpaper():
    """
    Change the wallpaper based on the currently playing song.
    """

    prev_status = ''

    oldModes = modes

    while True:
        
        #check if the song has been paused
        song_details = get_song_details(spotify_token)
        if song_details is None:
            print("Failed to retrieve song details. Trying again...")
            time.sleep(5)  # Wait a bit before retrying
            continue
        songTitle, status, imageUrl, artistName, songId, _ = song_details
        
        if status == "paused":
            #restore the original wallpaper
            os.system(command + str(original_wallpaper))
            time.sleep(5)
            prev_status = "paused"
            continue

        if status == "playing" and prev_status == "paused":
            #if the song has been paused and then resumed, change the wallpaper
            prev_status = "playing"
            os.system(command + os.getcwd() + "/ImageCache/finalImage.png")
            time.sleep(5)
            continue

        if songId != checkSong() or modes != oldModes:
            #create a lock file to avoid multiple instances of the program
            createWriteLock()
            oldModes = modes
            # Download the image and get its local path
            download_image(imageUrl)
            #change the song title in the file
            with open("src/songCheck.txt", "w") as f:
                f.write(songId)
                f.write(",")
                f.close()

            #check if the configuration for the song is already saved
            saved = searchConfig(songId)
            print("DEBUG>>:", saved)
            print("DEBUG>>:", len(saved))
            if len(saved) > 0:
                #choose randomly between the different configurations
                config = random.choice(saved)
                #copy the configuration to the ImageCache folder
                os.system(f"cp src/savedConfigs/{config} ImageCache/finalImage.png")
                #write the configuration to the file songCheck.txt
                with open("src/songCheck.txt", "w") as f:
                    f.write(songId)
                    f.write(",")
                    f.write(config.split("-")[1].split(".")[0])
                    f.close()
                #remove the lock file
                os.remove("src/songCheck.txt.lock")

                #change the wallpaper
                os.system(command + os.getcwd() + "/ImageCache/finalImage.png")
                time.sleep(1)
                continue
            
            else:
                #choose randomly between the different modes, and generate the wallpaper
                mode = random.choice(modes)

            print("DEBUG>>:", mode)

            if mode == "gradient":
                gradient(songTitle, imageUrl, artistName)
            elif mode == "blurred":
                if blurred(imageUrl, display) == False:
                    # If the blurred background fails, retry the entire process
                    resetSong()
                    continue
            elif mode == "waveform":
                waveform(songId, display, imageUrl, artistName, songTitle)
            elif mode == "albumImage":
                albumImage(display, songTitle, artistName, imageUrl)
            elif mode == "controllerImage":
                drawController(song_details, display, imageUrl)
            #change the wallpaper                           
            os.system(command + os.getcwd() + "/ImageCache/finalImage.png")

            #print on file the url of the cover image and the mode
            with open("src/songCheck.txt", "a") as f:
                f.write(mode)
                f.close()
            #remove the lock file
            os.remove("src/songCheck.txt.lock")

        time.sleep(1)  
    

def modify_modes():
    """
    Modify the modes to be used for generating wallpapers.
    """
    #global variable to store the modes
    global modes
    os.system("clear")
    print("Modes available:")
    print("  1. Gradient")
    print("  2. Blurred")
    print("  3. Waveform")
    print("  4. Album Image")
    print("  5. Controller Image")
    print("  6. All")

    m = input("Enter the mode you want to enable, separated by commas: ")
    modes = []

    #remove any spaces
    m = m.replace(" ", "")
    
    for i in m.split(","):

        if i == "1":
            modes.append("gradient")
        elif i == "2":
            modes.append("blurred")
        elif i == "3":
            modes.append("waveform")
        elif i == "4":
            modes.append("albumImage")
        elif i == "5":
            modes.append("controllerImage")
        elif i == "6":
            modes = ["gradient", "blurred", "waveform", "albumImage", "controllerImage"]
        else:
            print("Invalid mode.")
            continue
    input("Modes updated. Press Enter to continue...")
    
def saveConfig():
    """
    Copy the current configuration to the 'savedConfigs' folder.
    """
    if checkWriteLock():
        print("Configuration has not been saved yet.")
        return False
    #copy ImageCache/finalImage.png to src/savedConfigs/songID-MODE.png
    with open("src/songCheck.txt", "r") as f:
        lines = f.readlines()
        f.close()
    #get the album cover url
    songID = lines[0].split(",")[0]
    #get the mode
    mode = lines[0].split(",")[1]
    #copy the image
    os.system(f"cp ImageCache/finalImage.png src/savedConfigs/{songID}-{mode}.png")



    return True

def cli():
    """
    Command Line Interface for the SpotifySyncWall program.
    
    The CLI allows the user to change the settings and exit the program.
    """
    while True:
        #clear the screen
        os.system("clear")

        print("Welcome to the SpotifySyncWall CLI!")
        print("Type 'help' for a list of commands. \n")

        command = input("Enter a command: ")
        print()

        if command == "help":
            print("Commands:")
            print("   help - Display a list of commands.")
            print("   exit - Exit the program.")
            print("   settings - Change the settings.")
            print("   fav - Add this configuration to favorites. This will apply to every song with the same album cover.")

            #wait for the user to press enter
            input("\nPress Enter to continue...")
            continue

        if command == "exit":
            print("Exiting the program...")
            exit()
        if command == "settings":
            print("Settings:")
            print("  1. Choose which modes to use.")

            setting = input("\nEnter a setting: ")

            if setting == "1":
                modify_modes()
            else:
                print("Invalid setting.")
                continue

        if command == "fav":
            if not saveConfig():
                input("Press Enter to continue...")
                continue
            print("Configuration saved.")
            input("Press Enter to continue...")
            continue

if __name__ == "__main__":
    try:
        #start with initializations
        init()
        #launch a thread that will change the wallpaper
        wallpaperThread = threading.Thread(target=changeWallpaper)
        wallpaperThread.start()

        #launch the thread for the CLI interface
        cliThread = threading.Thread(target=cli)
        cliThread.start()

        cliThread.join()

        raise KeyboardInterrupt
    
    except KeyboardInterrupt:

        os.system(command + str(original_wallpaper))
        resetSong()
        print("Wallpaper restored.")
        
        pid = os.getpid()
        os.system(f"kill -9 {pid}")
