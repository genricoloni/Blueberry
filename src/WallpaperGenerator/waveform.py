from PIL import Image, ImageDraw
import utils.images

def create_waveform_image(audio_analysis, display, cover_image, artist_name, song_title, colors):
    loudness = extract_loudness_data(audio_analysis, audio_analysis['track']['duration'])

    width = int(display[0])
    height = int(display[1])

    loudness = [loud * 0.75 for loud in loudness]

    waveform_image = generate_waveform_image(loudness, (width, height), colors)

    text_image = utils.images.generate_text_image(song_title, artist_name, colors, display, positionX=50, positionY=height - 150)

    final_image = Image.new('RGB', (width, height), colors[0].rgb)

    final_image.paste(waveform_image, (width // 2 - waveform_image.width // 2, height // 2 - waveform_image.height // 2))

    final_image.paste(text_image, (0, 0), mask=text_image)

    final_image.save('ImageCache/finalImage.png')





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