# pretresene-crke-py


## Description
This game shows letters in a grid 4x4. All players write down as many words as they
can find. Letters may follow in a vertical, horizontal or diagonal way.

Points:
3 letters: 1 point
4 - 2
5 - 3
6 - 4
...

When the timer expires (90 seconds) you stop, then count points. Words, which
all players found, bring 0 points.

## Visuals

Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see
GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation

Linux: Make sure you have tkinter installed:

    sudo apt update
    sudo apt install python3-tk

It is recommended to create venv and then install the app from the downloaded whl file:

    python -m venv pretres_venv
    source pretres_venv/bin/activate
    pip install pretres-<version>.whl


## Usage
Activate the venv, then run the script as:

    source pretres_venv/bin/activate
    pretres

## Support
Send an email.

## Roadmap
1. Create GUI in Tkinter oz PzSide with rotated letters.

## Contributing
Send email or make pull request.

## Authors and acknowledgment
Marko Klopčič

## License
GPL V2

## How to deploy

    python -m pip install --upgrade pip build twine

