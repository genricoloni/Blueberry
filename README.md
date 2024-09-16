# SpotifySyncWall

 Currently Playing Spotify Song As Wallpaper **only for Gnome Desktop**

 Once you stop the script, the wallpaper will be reset to the default one.

 NOTE: if you wanna contribute, please, read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## Images

There are 6 modes: Album Cover, Gradient (up-down and center-out), Blurred, Waveform, Controller and Lyric card. From now, you can choose which one to use by setting them using the `settings` command in the CLI. Here are some examples:

![Album Cover mode](src/img/AlbumCover.png)

![Gradient mode](src/img/gradient.png)

![Blurred mode](src/img/blurred.png)

![Waveform mode](src/img/Waveform.png)

![Gradient mode from the center](src/img/centeredGradient.png)

![Controller mode](src/img/controller.png)

![Lyric card mode](src/img/lyric_card.png)

## Usage

1. Download the repo
2. Run `pip install -r requirements.txt` in terminal to install dependencies
3. Start listening to music on Spotify
4. Create and fill 'creds.txt' in the main directory (more info below)
5. Run src/main.py file
6. Log in if web page comes up
7. Copy link of web page after signing in and paste into terminal
8. Enjoy!

### creds.txt

Create a file called `creds.txt` in the main directory and fill it with the following:

``` txt
client_id = your_client_id
client_secret = your_client_secret
spot_username = your_spotify_username
```

### How to get client_id and client_secret

1. Go to <https://developer.spotify.com/dashboard/applications>
2. Log in with your Spotify account
3. Select 'Create an app'
4. Choose a name and description for your app, then click 'Create'
5. Click con 'Edit Settings' and set '<https://www.google.com/>' as new redirect URI, then Save
6. In the app page, copy the Client ID and Client Secret and paste them in the `creds.txt` file
7. Write your Spotify username in the `creds.txt` file
8. Save the file

### Note on display dimension

Script automatically retrieve display dimension, using the first available in `xrandr`: if your system doesn't have `xrandr` installed, you can:

- Install it
- Modify the command the `WallpaperGenerator/wallpaper_generator.py` file, line `39`, by adjusting the line with your preferred command to get the display dimension
- Manually set the display dimension in the `WallpaperGenerator/wallpaper_generator.py` file, changing the line `39` with your display dimension. For example, if your display is 1920x1080, you should change the line with `self.display = (1920, 1080)` or `self.display = ("1920", "1080")`.

## TODO

### Short term

- [ ] ~~Find a better way to check if colors are too similar~~
- [ ] ~~Function that choose which color use as second one in each mode, based on some magic *distance* between colors~~
- [ ] ~~Find a better way to leveling levels of loudness in waveform mode, so peaks are not too high compared to the rest of the image~~
- [ ] Add new fonts

### Medium term

- [ ] Add new modes
- [ ] Let user choose some parameters (ex. colors, gradient direction, etc.) without editing the code or stop the script (WIP)
- [ ] Implement an actual control of the music, so you can pause, skip, etc. directly from the CLI

### Long term

- [ ] ~~General optimization of the code~~
- [ ] Add a GUI (too far from now, I think)
- [ ] Compatibility with other desktop environments (same as above)
- [ ] Convert the script in a GNOME extension
- [ ] Mobile version for Android
