# pibooth-forget-button

Plugin for [pibooth](https://github.com/pibooth/pibooth) adding a third button to "forget" photos.

## Features

- Dedicated GPIO button to move photos to a "forget" folder
- LED indicator that blinks during print state
- Displays "Photo oubliee !" on screen when a photo is forgotten
- Works during both print and wait states

## Installation

```bash
pip install pibooth-forget-button
```

## Configuration

In the file `~/.config/pibooth/pibooth.cfg`, add:

```ini
[FORGET_BUTTON]
# GPIO IN pin for the button (BOARD numbering, 0 to disable)
forget_btn_pin = 36

# GPIO OUT pin for the LED (0 to disable)
forget_led_pin = 37

# Button press duration in seconds
debounce_delay = 0.3
```

## Usage

1. Take a photo with pibooth
2. During the print screen (when the LED blinks), press the forget button
3. The photo will be moved to the `forget/` subfolder and "Photo oubliee !" message will be displayed

## License

MIT
