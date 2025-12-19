# Where's Wind Meet Xiangqi/Chess to FEN

Automatic Xiangqi (Chinese Chess) board recognition system using computer vision.

⚠️ **Important Notes:**
- **Dynamic Scaling:** The tool now automatically adapts to any resolution (1080p, 2K, 4K, etc.).
- **Aspect Ratio Support:** Fully supports **Ultra-Wide (21:9)**, standard (16:9), and even **Vertical (Portrait)** monitors by automatically centering the detection grid.
- **Windowed Mode:** Works in both full-screen and windowed modes, provided the game board remains centered in the captured image.

## 📋 Requirements

- Python 3.8+
- OpenCV
- NumPy
- Pyperclip
- Pillow (PIL)

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

The program reads the image directly from your **clipboard**.

* **Single monitor:** Press `Print Screen` to capture the full screen.
* **Active Window:** Press `Alt + Print Screen` to capture only the game window (recommended if playing in windowed mode).
* **Region:** You can also use `Win + Shift + S` to capture the board area specifically.

### Step 3: Run

After capturing the screenshot, run:

```bash
python main.py
```

The program will:
- Detect your screen resolution and aspect ratio.
- Calculate offsets to find the centered board.
- Match pieces using scaled templates.
- **Generate FEN notation** and copy it to your clipboard automatically.

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

* **UPPERCASE** = Red pieces
* **lowercase** = Black pieces

## 🔧 Technologies

- **OpenCV**: Template matching for piece recognition
- **NumPy**: Array and matrix manipulation
- **Pillow**: Clipboard image capture
- **Pyperclip**: Automatic clipboard copying