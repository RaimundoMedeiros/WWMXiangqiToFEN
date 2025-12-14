import cv2
import numpy as np
import pyperclip
from PIL import ImageGrab
import tkinter as tk
import sys
import os

# ==========================================
#              CONFIGURATION
# ==========================================

# Get base path 
def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()

# Base resolution (1080p) - templates were created at this resolution
BASE_RESOLUTION = (1920, 1080)
BASE_COORDS = {
    'start_x': 177,
    'start_y': 103,
    'end_x': 920,
    'end_y': 930,
    'crop_size': 55
}

# Detection parameters
THRESHOLD = 0.70       # Minimum confidence (0.70 = 70%)
DEBUG_VISUAL = True    # Shows window with squares and detected pieces

# Template mapping (UPPERCASE=Red, lowercase=Black)
templates_map = {
    'R': os.path.join(BASE_PATH, 'templates', 'red_chariot.png'),
    'N': os.path.join(BASE_PATH, 'templates', 'red_horse.png'),
    'B': os.path.join(BASE_PATH, 'templates', 'red_elephant.png'),
    'A': os.path.join(BASE_PATH, 'templates', 'red_advisor.png'),
    'K': os.path.join(BASE_PATH, 'templates', 'red_general.png'),
    'C': os.path.join(BASE_PATH, 'templates', 'red_cannon.png'),
    'P': os.path.join(BASE_PATH, 'templates', 'red_soldier.png'),
    'r': os.path.join(BASE_PATH, 'templates', 'black_chariot.png'),
    'n': os.path.join(BASE_PATH, 'templates', 'black_horse.png'),
    'b': os.path.join(BASE_PATH, 'templates', 'black_elephant.png'),
    'a': os.path.join(BASE_PATH, 'templates', 'black_advisor.png'),
    'k': os.path.join(BASE_PATH, 'templates', 'black_general.png'),
    'c': os.path.join(BASE_PATH, 'templates', 'black_cannon.png'),
    'p': os.path.join(BASE_PATH, 'templates', 'black_soldier.png'),
}

# ==========================================
#           MAIN FUNCTIONS
# ==========================================

def calculate_scale_factor(img_width, img_height):
    """Calculate scale factor based on current resolution vs base resolution."""
    scale_x = img_width / BASE_RESOLUTION[0]
    scale_y = img_height / BASE_RESOLUTION[1]
    # Use average to handle non-uniform scaling
    return (scale_x + scale_y) / 2.0

def scale_coordinates(scale_factor):
    """Scale board coordinates based on resolution."""
    return {
        'start_x': int(BASE_COORDS['start_x'] * scale_factor),
        'start_y': int(BASE_COORDS['start_y'] * scale_factor),
        'end_x': int(BASE_COORDS['end_x'] * scale_factor),
        'end_y': int(BASE_COORDS['end_y'] * scale_factor),
        'crop_size': int(BASE_COORDS['crop_size'] * scale_factor)
    }

def load_templates(scale_factor=1.0):
    """Loads and scales template images based on resolution."""
    loaded = {}
    print(f"Loading templates (scale: {scale_factor:.2f}x)...")
    for code, path in templates_map.items():
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is not None:
            # Scale template if resolution is different from base
            if scale_factor != 1.0:
                new_width = int(img.shape[1] * scale_factor)
                new_height = int(img.shape[0] * scale_factor)
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            loaded[code] = img
    return loaded

def detect_piece_color(crop):
    """Detects if the piece is red or black based on dominant color."""
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    
    # Red color masks (Hue split: 0-10 and 170-180)
    mask_red1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
    mask_red2 = cv2.inRange(hsv, np.array([170, 50, 50]), np.array([180, 255, 255]))
    mask_red = mask_red1 + mask_red2
    
    # Black color mask (low value)
    mask_black = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 70]))
    
    # Compare pixel count
    return 'red' if cv2.countNonZero(mask_red) > cv2.countNonZero(mask_black) else 'black'

def identify_piece(crop, templates):
    """Identifies which piece is in the crop using template matching."""
    best_score = -1
    best_piece = None
    detected_color = detect_piece_color(crop)
    
    for code, temp_img in templates.items():
        # Filter templates by color (UPPERCASE=Red, lowercase=Black)
        if (detected_color == 'red' and code.islower()) or \
           (detected_color == 'black' and code.isupper()):
            continue
        
        # Ensure template is not larger than crop
        if crop.shape[0] < temp_img.shape[0] or crop.shape[1] < temp_img.shape[1]:
            continue

        # Template matching
        result = cv2.matchTemplate(crop, temp_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        
        if max_val > best_score:
            best_score = max_val
            best_piece = code
    
    return (best_piece, best_score) if best_score >= THRESHOLD else (None, 0)

def fit_to_screen(img):
    """Resize image to fit screen if it's larger."""
    try:
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        
        # Leave some margin (90% of screen)
        max_width = int(screen_width * 0.9)
        max_height = int(screen_height * 0.9)
        
        img_height, img_width = img.shape[:2]
        
        # Calculate scale to fit screen
        if img_width > max_width or img_height > max_height:
            scale = min(max_width / img_width, max_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            return cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return img
    except:
        # If tkinter fails, return original image
        return img

def generate_fen(board):
    """Converts the board matrix to FEN notation."""
    fen = ""
    for row in range(10): 
        empty = 0
        for col in range(9): 
            piece = board[row][col]
            if piece is None:
                empty += 1
            else:
                if empty > 0:
                    fen += str(empty)
                    empty = 0
                fen += piece
        if empty > 0:
            fen += str(empty)
        if row < 9:
            fen += "/"
    return fen

# ==========================================
#         BOARD SCANNING FUNCTION
# ==========================================

def scan_board(board_img, verbose=True):
    """
    Scan board and return all detection results.
    
    Args:
        board_img: OpenCV image (BGR format)
        verbose: If True, print detection details
    
    Returns:
        dict with keys: board, fen, debug_img, pieces_info, scale_factor, coords
    """
    height, width = board_img.shape[:2]
    if verbose:
        print(f"✓ Image loaded: {width}x{height} pixels")
    
    # Calculate scale factor and adjust coordinates
    scale_factor = calculate_scale_factor(width, height)
    coords = scale_coordinates(scale_factor)
    
    if verbose:
        print(f"Resolution scale: {scale_factor:.2f}x (base: {BASE_RESOLUTION[0]}x{BASE_RESOLUTION[1]})")
        print(f"Board region: ({coords['start_x']},{coords['start_y']}) to ({coords['end_x']},{coords['end_y']})")
    
    # Load templates with scaling
    templates = load_templates(scale_factor)
    board_logic = [[None for _ in range(9)] for _ in range(10)]
    debug_img = board_img.copy()
    pieces_info = []  # List of (row, col, piece, score)

    # Calculate grid dimensions
    total_width = coords['end_x'] - coords['start_x']
    total_height = coords['end_y'] - coords['start_y']
    if verbose:
        print(f"Scanning board ({total_width}x{total_height} px)...")
    
    # Scan all 90 positions (10 rows × 9 columns)
    for row in range(10):
        percent_y = row / 9.0
        cy = int(coords['start_y'] + (total_height * percent_y))
        
        for col in range(9):
            percent_x = col / 8.0
            cx = int(coords['start_x'] + (total_width * percent_x))
            
            # Extract crop
            half = coords['crop_size'] // 2
            y1, y2 = cy - half, cy + half
            x1, x2 = cx - half, cx + half
            
            if x1 < 0 or y1 < 0 or x2 > board_img.shape[1] or y2 > board_img.shape[0]:
                continue

            crop = board_img[y1:y2, x1:x2]
            
            # Visual debug - draw rectangles
            cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 1)

            # Identify piece
            piece, score = identify_piece(crop, templates)
            
            if piece:
                board_logic[row][col] = piece
                pieces_info.append((row, col, piece, score))
                
                # Draw letter with outline (scaled font size)
                font_scale = 0.8 * scale_factor
                thickness_bg = max(1, int(4 * scale_factor))
                thickness_fg = max(1, int(2 * scale_factor))
                
                cv2.putText(debug_img, piece, (cx-10, cy+5), 
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness_bg)
                cv2.putText(debug_img, piece, (cx-10, cy+5), 
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 255), thickness_fg)
                if verbose:
                    print(f"[{row},{col}] '{piece}' - {score:.2%}")
            else:
                if verbose and score > 0:
                    print(f"[{row},{col}] Empty (score: {score:.2%})")
    
    # Add resolution text to debug image (scaled font)
    res_text = f"{width}x{height}"
    res_font_scale = 0.7 * scale_factor
    res_thickness_bg = max(1, int(3 * scale_factor))
    res_thickness_fg = max(1, int(2 * scale_factor))
    
    cv2.putText(debug_img, res_text, (10, int(25 * scale_factor)),
               cv2.FONT_HERSHEY_SIMPLEX, res_font_scale, (0, 0, 0), res_thickness_bg)
    cv2.putText(debug_img, res_text, (10, int(25 * scale_factor)),
               cv2.FONT_HERSHEY_SIMPLEX, res_font_scale, (0, 255, 0), res_thickness_fg)
    
    # Generate FEN
    fen = generate_fen(board_logic)
    
    return {
        'board': board_logic,
        'fen': fen,
        'debug_img': debug_img,
        'pieces_info': pieces_info,
        'scale_factor': scale_factor,
        'coords': coords,
        'width': width,
        'height': height
    }

# ==========================================
#            MAIN FUNCTION
# ==========================================

def main():
    # Capture image from clipboard
    print("Capturing image from clipboard...")
    pil_img = ImageGrab.grabclipboard()
    
    if pil_img is None:
        print("ERROR: No image found in clipboard!")
        print("Tip: Press Print Screen and try again.")
        return
    
    # Convert PIL image to OpenCV format (BGR)
    board_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # Scan board
    result = scan_board(board_img, verbose=True)

    # Display FEN
    fen_full = result['fen'] + " w - - 0 1"
    print("\n" + "="*40)
    print(" FINAL RESULT (FEN)")
    print("="*40)
    print(fen_full)
    print("="*40)
    
    # Copy to clipboard
    try:
        pyperclip.copy(fen_full)
        print("[OK] FEN copied! Use Ctrl+V to paste.")
    except Exception as e:
        print(f"[WARNING] Copy error: {e}")
    
    print("="*40)
    
    if DEBUG_VISUAL:
        # Resize to fit screen if necessary
        display_img = fit_to_screen(result['debug_img'])
        
        cv2.imshow("Visual Check", display_img)
        print("Press any key to close.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()