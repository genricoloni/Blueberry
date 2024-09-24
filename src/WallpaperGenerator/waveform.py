"""
Module for generating a waveform image based on the audio analysis data from the Spotify API.
"""
#pylint: disable=import-error, no-member

from PIL import Image, ImageDraw
import utils.images

def create_waveform_image(audio_analysis, display, artist_name, song_title, colors):
    """
    Create and save a waveform image based on the audio analysis data,
    overlaying the song title, artist name, and cover image.

    Args:
        audio_analysis (dict): Audio analysis data from the Spotify API.
        display (tuple): Display dimensions (width, height).
        cover_image (PIL.Image): The album cover image.
        artist_name (str): The name of the artist.
        song_title (str): The title of the song.
        colors (list): List of two colors, 
            where the first is for the background and the second is for the waveform.

    Returns:
        None: The function saves the generated image to the 'ImageCache/finalImage.png' file.
    """
    # Extract normalized loudness data from audio analysis
    loudness = extract_loudness_data(audio_analysis, audio_analysis['track']['duration'])

    width, height = int(display[0]), int(display[1])

    # Adjust loudness for visual scaling
    loudness = [loud * 0.75 for loud in loudness]

    # Generate waveform image based on loudness data
    waveform_image = generate_waveform_image(loudness, (width, height), colors)

    # Generate text image with the song title and artist name
    text_image = utils.images.generate_text_image(
        song_title, artist_name, colors, display, position_x=50, position_y=height - 150
    )

    # Create the final image with the background color
    final_image = Image.new('RGB', (width, height), colors[0].rgb)

    # Paste the waveform image and text image onto the final image
    final_image.paste(waveform_image,
                      (width // 2 - waveform_image.width // 2,
                       height // 2 - waveform_image.height // 2))
    final_image.paste(text_image, (0, 0), mask=text_image)

    # Save the final image
    final_image.save('ImageCache/finalImage.png')


def extract_loudness_data(audio_analysis, duration, sample_points=100):
    """
    Extract loudness levels from the audio analysis data, normalized across the song's duration.

    Args:
        audio_analysis (dict): Audio analysis data from the Spotify API.
        duration (float): Duration of the song in seconds.
        sample_points (int, optional): Number of sample points for the waveform. Defaults to 100.

    Returns:
        list: A list of normalized loudness levels for generating the waveform.
    """
    segments = [{
        'start': segment['start'] / duration,
        'duration': segment['duration'] / duration,
        'loudness': 10 ** (segment['loudness_max'] / 20)  # Adjust loudness for perception
    } for segment in audio_analysis['segments']]

    loudness_levels = [0] * sample_points
    for segment in segments:
        start_index = int(segment['start'] * sample_points)
        end_index = min(sample_points,
                        int((segment['start'] + segment['duration']) * sample_points))
        for i in range(start_index, end_index):
            loudness_levels[i] = max(loudness_levels[i], segment['loudness'])

    # Normalize the loudness levels to a range between 0 and 1
    max_loudness = max(loudness_levels, default=1)
    return [level / max_loudness for level in loudness_levels]


def generate_waveform_image(levels, display_dimensions, colors):
    """
    Generate a waveform image based on the normalized loudness levels.

    Args:
        levels (list): List of normalized loudness levels.
        display_dimensions (tuple): Dimensions of the display (width, height).
        colors (list): List containing two RGB color objects: background color and waveform color.

    Returns:
        PIL.Image: The generated waveform image.
    """
    width, height = display_dimensions
    base_height = height  # Used for scaling the waveform height

    # Create a new image with the background color
    image = Image.new('RGB', (width, height), colors[0].rgb)

    # Create waveform schema for the loudness levels (upper and lower halves)
    schema = [(int(i / 100 * width),
               int((1/2 + level/2) * height)) for i, level in enumerate(levels)]
    inverted_schema = [(int(i / 100 * width),
                        int((1/2 - level/2) * height)) for i, level in enumerate(levels)]

    # Normalize the schema to fit the screen's height
    schema = [(x, int(y * (base_height / height))) for x, y in schema]
    inverted_schema = [(x, int(y * (base_height / height))) for x, y in inverted_schema]

    draw = ImageDraw.Draw(image)

    # Draw the waveform as rounded rectangles
    for i, start_point in enumerate(schema):
        start_point = schema[i]

        if abs(start_point[1] - inverted_schema[i][1]) < 32:
            draw.rounded_rectangle(
                [inverted_schema[i][0], height / 2 - 16, start_point[0] + 16, height / 2 + 16],
                fill=colors[1].rgb, radius=8
            )
        else:
            draw.rounded_rectangle(
                [inverted_schema[i][0], inverted_schema[i][1], start_point[0] + 16, start_point[1]],
                fill=colors[1].rgb, radius=8
            )

    # Resize the waveform image to 60% of its original size for better presentation
    resized_image = image.resize((int(width * 0.6), int(height * 0.6)), Image.LANCZOS)

    return resized_image
