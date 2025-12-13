# Where's Wind Meet Xiangqi/Chess to FEN

Automatic Xiangqi (Chinese Chess) board recognition system using computer vision.

⚠️ **Important:** This tool only works with the game running at **1920x1080 resolution (1080p)**. Other resolutions are not supported yet.

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
└── requirements.txt     # Dependencies
```

## 🎯 How to Use

### Step 1: Configure Game Board

In "Where's Wind Meet", set the chess board to **Icons Chess Board** mode.

### Step 2: Capture Screenshot

**Important:** Press `Print Screen` to capture the board:

- **Single monitor (1920x1080):** Press `Print Screen` to capture the full screen
- **Dual monitors:** Press `Alt + Print Screen` to capture only the active window

The program will automatically read the image from your clipboard.

### Step 3: Run

After capturing the screenshot, run:

```bash
python main.py
```

The program will:
- Read the image directly from clipboard
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
- **Pillow**: Clipboard image capture
- **Pyperclip**: Automatic clipboard copying
