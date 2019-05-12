# Spotify Networks
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/v715/Spotify-Net/master)

Spoti-Graph allows you to construct and analyze networks of related artists on Spotify! 

## Overview
Spoti-Graph interfaces with the [Spotify Web API](https://developer.spotify.com/documentation/web-api/) to obtain all related artists.
You provide a starting artist, and the program executes a depth-first search to find neighbors. 
Two artists are conneced by an edge if they have collaborated on a popular song or if Spotify lists them as related.

## Demo
To run install the package and run the demo, execute the following:
```
git clone https://github.com/v715/Spoti-Graph
cd Spoti-Graph
pip install -r requirements.txt
python main.py
```

This is what we get:

![demo](derivatives/demo.png)
