# Timetable

This script retrieves your timetable from Firefly.

[![asciicast](https://asciinema.org/a/qwucsSXemoLbaCgvBsIu7p4VI.svg)](https://asciinema.org/a/qwucsSXemoLbaCgvBsIu7p4VI)

## Requirements
- libxml2 and libxslt
- Python 3.6 or higher
- Python dependencies listed in `requirements.txt` (`pip install -r requirements.txt`)

## Usage
1. You'll need to create a `timetable.conf` within a directory named `ff-timetable` in your home directory.
2. Within the config file, specify your Firefly credentials under a section labelled with your Firefly hostname.  
    Example:

    ```ini
    [firefly.example.com]
    Username: jdrift
    Password: 5jMFKEPrjUNb
    ```
3. Run the script. It'll log you in automatically.
    ```bash
    python timetable.py
    ```