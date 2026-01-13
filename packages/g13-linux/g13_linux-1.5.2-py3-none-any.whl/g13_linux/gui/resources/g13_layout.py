"""
G13 Button Layout Geometry

Defines the visual positions and sizes of all G13 buttons for the GUI.
Coordinates match the device background image (800x680 pixels - landscape).

The G13 is wider than tall. This layout matches the actual device proportions
with the LCD at top, key grid in center, and thumbstick area at bottom-right.
"""

# Overall dimensions - landscape orientation matching real G13
KEYBOARD_WIDTH = 800
KEYBOARD_HEIGHT = 680

# Key sizing
KEY_W = 48  # Standard G-key width
KEY_H = 40  # Standard G-key height
M_KEY_W = 44  # M-key width
M_KEY_H = 22  # M-key height
KEY_GAP = 4  # Gap between keys

# Layout starting positions
KEYS_LEFT = 95  # Left edge of G-key area
KEYS_TOP = 195  # Top of first G-key row

G13_BUTTON_POSITIONS = {
    # M-keys row (below LCD, horizontal row of mode buttons)
    "M1": {"x": 245, "y": 160, "width": M_KEY_W, "height": M_KEY_H},
    "M2": {"x": 295, "y": 160, "width": M_KEY_W, "height": M_KEY_H},
    "M3": {"x": 345, "y": 160, "width": M_KEY_W, "height": M_KEY_H},
    "MR": {"x": 395, "y": 160, "width": M_KEY_W, "height": M_KEY_H},

    # G-keys Row 1 (G1-G7) - top row, curved (edges slightly lower)
    "G1": {"x": KEYS_LEFT, "y": KEYS_TOP + 8, "width": KEY_W, "height": KEY_H},
    "G2": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 1, "y": KEYS_TOP + 4, "width": KEY_W, "height": KEY_H},
    "G3": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 2, "y": KEYS_TOP, "width": KEY_W, "height": KEY_H},
    "G4": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 3, "y": KEYS_TOP, "width": KEY_W, "height": KEY_H},
    "G5": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 4, "y": KEYS_TOP, "width": KEY_W, "height": KEY_H},
    "G6": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 5, "y": KEYS_TOP + 4, "width": KEY_W, "height": KEY_H},
    "G7": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 6, "y": KEYS_TOP + 8, "width": KEY_W, "height": KEY_H},

    # G-keys Row 2 (G8-G14)
    "G8": {"x": KEYS_LEFT, "y": KEYS_TOP + KEY_H + KEY_GAP + 8, "width": KEY_W, "height": KEY_H},
    "G9": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 1, "y": KEYS_TOP + KEY_H + KEY_GAP + 4, "width": KEY_W, "height": KEY_H},
    "G10": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 2, "y": KEYS_TOP + KEY_H + KEY_GAP, "width": KEY_W, "height": KEY_H},
    "G11": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 3, "y": KEYS_TOP + KEY_H + KEY_GAP, "width": KEY_W, "height": KEY_H},
    "G12": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 4, "y": KEYS_TOP + KEY_H + KEY_GAP, "width": KEY_W, "height": KEY_H},
    "G13": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 5, "y": KEYS_TOP + KEY_H + KEY_GAP + 4, "width": KEY_W, "height": KEY_H},
    "G14": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 6, "y": KEYS_TOP + KEY_H + KEY_GAP + 8, "width": KEY_W, "height": KEY_H},

    # G-keys Row 3 (G15-G19) - 5 keys, offset right
    "G15": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 1, "y": KEYS_TOP + (KEY_H + KEY_GAP) * 2 + 4, "width": KEY_W, "height": KEY_H},
    "G16": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 2, "y": KEYS_TOP + (KEY_H + KEY_GAP) * 2, "width": KEY_W, "height": KEY_H},
    "G17": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 3, "y": KEYS_TOP + (KEY_H + KEY_GAP) * 2, "width": KEY_W, "height": KEY_H},
    "G18": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 4, "y": KEYS_TOP + (KEY_H + KEY_GAP) * 2, "width": KEY_W, "height": KEY_H},
    "G19": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 5, "y": KEYS_TOP + (KEY_H + KEY_GAP) * 2 + 4, "width": KEY_W, "height": KEY_H},

    # G-keys Row 4 (G20-G22) - 3 wider keys (spacebar-like row)
    "G20": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 2, "y": KEYS_TOP + (KEY_H + KEY_GAP) * 3, "width": KEY_W + 8, "height": KEY_H + 4},
    "G21": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 3 + 4, "y": KEYS_TOP + (KEY_H + KEY_GAP) * 3, "width": KEY_W + 8, "height": KEY_H + 4},
    "G22": {"x": KEYS_LEFT + (KEY_W + KEY_GAP) * 4 + 8, "y": KEYS_TOP + (KEY_H + KEY_GAP) * 3, "width": KEY_W + 8, "height": KEY_H + 4},

    # Thumb buttons (left of joystick on palm rest)
    "LEFT": {"x": 540, "y": 450, "width": 44, "height": 36},
    "DOWN": {"x": 540, "y": 495, "width": 44, "height": 36},

    # Joystick click (STICK) - center of joystick area
    "STICK": {"x": 615, "y": 460, "width": 55, "height": 55},
}

# Joystick area (for visual indicator drawing)
JOYSTICK_AREA = {"x": 600, "y": 445, "width": 85, "height": 85}

# LCD display area (green screen at top of device)
# 160x43 pixel monochrome display, scaled up for visibility
LCD_AREA = {"x": 220, "y": 50, "width": 280, "height": 95}
