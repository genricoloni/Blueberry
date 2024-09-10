# How to contribute to this project

## Add a new mode

If you want to add a new mode, please make sure to check the following:

- [] Create a new `.py` file in `WallpaperGenerator` folder with the name of the mode;
- [] Import the new method in the `WallpaperGenerator` class, making sure to follow the same alias pattern;
- [] Add `generate_methodName` method inside the WallPaperGenerator class;
- [] add the new mode in the `modes` array in the `main.py` file, line `36`;
- [] Add the `elif` statement in `main.py` file, function `change_wallpaper_periodically`;
- [] If needed, add any new dependency in the `requirements.txt` file. It would be better to use a virtual environment and add the dependency by running `pip freeze > requirements.txt` in the terminal.
- [] Add a new image in the `src/img` folder, with the same name of the mode file, but with a `.png` extension;
- [] Add the image in the `README.md` file, adding it also in the paragraph that describes the mode;

## Add a new Desktop Environment

Frankly, I'm not sure yet how the script should handle different desktop environments. Currently, the workflow is handled by `handler.py` file:

- there is a `self.availableEnvironments` array, in which every element is a dictionary with the following
  - `envName`: the name of the desktop environment
  - `testCommand`: the command to check if the desktop environment is installed
  - `command`: the command to set the wallpaper
  - `wallpaperPath`: the path where the original wallpaper is stored
- the `getEnvironment` method checks which desktop environment is installed and returns the corresponding dictionary by checking the `testCommand` command

I don't know if this is the best way to handle different desktop environments, so I'm open to suggestions. However, if you want to add a new desktop environment, you should:

- [] Add a new dictionary in the `self.availableEnvironments` array in the `handler.py` file, following the same pattern. Please pay attention to support also the dark mode, in case the desktop environment handle it differently from the light one;
- Test it! I don't have the possibility to test all the desktop environments, so please make sure that the script works on your specific desktop environment, even by running it in different machines if applicable.
- Remember that all the logic to create the wallpaper is independent from the desktop environment, so you don't have to worry about that. The only thing to do change is the way the wallpaper is set.

## Other contributions

If you have other ideas, bigger than the previous ones (such as the GUI, the GNOME extension, Android compatibility, etc.), please open an issue and let's discuss it together. I'm open to any kind of contribution, so don't be shy!