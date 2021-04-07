# Color Seeker game
### Tile-based platformer coded using Python's Arcade library!

This game is a passion project that came about after hours of indulging in a variety of hobbies, including drawing, painting, coding in Python, watching tech videos on Youtube, and playing instruments. After some time of thinking, "what can I do that allows me to combine most my interests into one workable package?" I decided that I could work on a simple 2D platformer game! It's simple, really: there is code to be written, assets to be rendered, sounds to be created, and levels to be designed! To combine most of my interests into one, this should be fun.

The name "Color Seeker" is a working title. It is a hint to what the gameplay will be like in the future (Puzzles, revealing hidden platforms, etc). 

Color Seeker is coded in Python 3.8 primarily using the Arcade module. The structure of the code is Object-Oriented with Player, Window, View and Game objects. The player progresses through levels linearly, getting color keys to activate hidden platforms while avoiding dangerous obstacles. Game levels are designed and created in Tiled using original spritesheets. The main code loads the resulting .tmx levels into the window, where the user can then control the player character. 

Here's a quick screenshot of how it looks as of April 2021:
![Color Seeker game screenshot](https://github.com/Krizeon/Color-seeker-game/blob/master/game%20screenshot.png)

Here it is in action:
![Color Seeker game gif](https://github.com/Krizeon/Color-seeker-game/blob/master/color-seeker-key.gif)

All assets in the screenshot above have been drawn by me in Adobe Photoshop. The player character (in grey) has animations when being controlled via WASD or Arrow keys, most notably a 14-frame walking animation. More animations are to come in time for enemy characters as well. Game tile design is still in an iterative phase, so what you see in the screenshot above may be subject to change in the future. There are also non-interactive detail assets also being designed to furnish the game world with more life, such as alien-looking trees and tall grass. 

If you are interested in which other features and enhancements are being planned, check out the Issues tab!

#### How to run:
Currently, this project is not a standalone app, so you must run main.py after installing the required packages. Luckily, you can do this easily with the included requirements.txt file! Just follow these steps:

1) Clone this repo to a folder of your choice
2) Create your own Virtual Environment (venv)
3) Run pip install -r requirements.txt in a terminal/cmd in the project folder
4) Done!

After that, just run main.py to see Color Seeker in action. Enjoy!


 
 
