# Where's Wind Meet Xiangqi/Chess to FEN

Automatic Xiangqi (Chinese Chess) board recognition system using computer vision.

⚠️ **Important:** This tool only works with the game running at **1920x1080 resolution (1080p)**. Other resolutions are not supported.

## 📋 Requirements

- Python 3.8+
- OpenCV
- NumPy
- Pyperclip

## 🚀 Installation

1. Clone or extract the project
2. Create a virtual environment (optional):
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📂 Project Structure

```
xiangqichess/
├── main.py              # Main script
├── templates/           # Piece images (templates)
│   ├── red_chariot.png
│   ├── black_horse.png
│   └── ...
├── image.png            # Board image to analyze
└── requirements.txt     # Dependencies
```

## 🎯 How to Use

### Step 0: Capture Screenshot

**Important:** The board image must be captured correctly:

- **Single monitor (1920x1080):** Press `Print Screen` to capture the full screen
- **Dual monitors:** Press `Alt + Print Screen` to capture only the active window
- Save the screenshot as `image.png` in the project folder

### Step 1: Configure Coordinates

Edit `main.py` (lines 10-13) with the board corner coordinates:

```python
START_POINT_X = 177    # Top-left corner
START_POINT_Y = 103
END_POINT_X   = 920    # Bottom-right corner
END_POINT_Y   = 930
```

### Step 2: Run

Place the board image as `image.png` and run:

```bash
python main.py
```

The program will:
- Detect all pieces on the board
- Generate FEN notation
- Automatically copy to clipboard

## ⚙️ Configuration

In `main.py`:

- `THRESHOLD`: Minimum confidence (0.70 = 70%)
- `CROP_SIZE`: Size of extracted square (in pixels)
- `DEBUG_VISUAL`: Shows window with visual detection

## 📝 Output Format

Standard Xiangqi FEN notation:
```
rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1
```

- **UPPERCASE** = Red pieces
- **lowercase** = Black pieces
- **Numbers** = Empty squares

## 🔧 Technologies

- **OpenCV**: Template matching for piece recognition
- **NumPy**: Array and matrix manipulation
- **Pyperclip**: Automatic clipboard copying
