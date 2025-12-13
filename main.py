import cv2
import numpy as np
import pyperclip

# ==========================================
#              CONFIGURATION
# ==========================================

# Calibration points (top-left and bottom-right corners)
START_POINT_X = 177    # Top-left corner X
START_POINT_Y = 103    # Top-left corner Y
END_POINT_X   = 920    # Bottom-right corner X
END_POINT_Y   = 930    # Bottom-right corner Y

# Detection parameters
THRESHOLD = 0.70       # Minimum confidence (0.70 = 70%)
CROP_SIZE = 55         # Size of extracted square (in pixels)
DEBUG_VISUAL = True    # Shows window with squares and detected pieces

# Template mapping (UPPERCASE=Red, lowercase=Black)
templates_map = {
    'R': 'templates/red_chariot.png',
    'N': 'templates/red_horse.png',
    'B': 'templates/red_elephant.png',
    'A': 'templates/red_advisor.png',
    'K': 'templates/red_general.png',
    'C': 'templates/red_cannon.png',
    'P': 'templates/red_soldier.png',
    'r': 'templates/black_chariot.png',
    'n': 'templates/black_horse.png',
    'b': 'templates/black_elephant.png',
    'a': 'templates/black_advisor.png',
    'k': 'templates/black_general.png',
    'c': 'templates/black_cannon.png',
    'p': 'templates/black_soldier.png',
}

# ==========================================
#           MAIN FUNCTIONS
# ==========================================

def load_templates():
    """Loads and resizes all template images."""
    loaded = {}
    print("Loading templates...")
    for code, path in templates_map.items():
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is not None:
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

    # Debug for red cannon with low score
    if best_piece == 'C' and best_score < 0.85:
        print(f"  [DEBUG] Red cannon with low score ({best_score:.2%})")
        temp_cannon = templates.get('C')
        if temp_cannon is not None:
            h = max(crop.shape[0], temp_cannon.shape[0])
            comparison = np.zeros((h, crop.shape[1] + temp_cannon.shape[1], 3), dtype=np.uint8)
            comparison[:crop.shape[0], :crop.shape[1]] = crop
            comparison[:temp_cannon.shape[0], crop.shape[1]:] = temp_cannon
            cv2.putText(comparison, "Crop", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            cv2.putText(comparison, "Template", (crop.shape[1]+5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            cv2.putText(comparison, f"Score: {best_score:.2%}", (5, h-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
            cv2.imwrite("debug_cannon_comparison.png", comparison)
    
    return (best_piece, best_score) if best_score >= THRESHOLD else (None, 0)

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
#            MAIN FUNCTION
# ==========================================

def main():
    # Load image
    image_path = 'image.png'
    board_img = cv2.imread(image_path)
    if board_img is None:
        print(f"Error: Could not open '{image_path}'.")
        return

    templates = load_templates()
    board_logic = [[None for _ in range(9)] for _ in range(10)]
    debug_img = board_img.copy()

    # Calculate grid dimensions
    total_width = END_POINT_X - START_POINT_X
    total_height = END_POINT_Y - START_POINT_Y
    print(f"Scanning board ({total_width}x{total_height} px)...")
    
    # Scan all 90 positions (10 rows × 9 columns)
    for row in range(10):
        percent_y = row / 9.0
        cy = int(START_POINT_Y + (total_height * percent_y))
        
        for col in range(9):
            percent_x = col / 8.0
            cx = int(START_POINT_X + (total_width * percent_x))
            
            # Extract crop
            half = CROP_SIZE // 2
            y1, y2 = cy - half, cy + half
            x1, x2 = cx - half, cx + half
            
            if x1 < 0 or y1 < 0 or x2 > board_img.shape[1] or y2 > board_img.shape[0]:
                continue

            crop = board_img[y1:y2, x1:x2]
            
            # Visual debug
            if DEBUG_VISUAL:
                cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 1)

            # Identify piece
            piece, score = identify_piece(crop, templates)
            
            if piece:
                board_logic[row][col] = piece
                # Draw letter with outline
                cv2.putText(debug_img, piece, (cx-10, cy+5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
                cv2.putText(debug_img, piece, (cx-10, cy+5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                print(f"[{row},{col}] '{piece}' - {score:.2%}")
            else:
                if score > 0:
                    print(f"[{row},{col}] Empty (score: {score:.2%})")

    # Generate and display FEN
    fen = generate_fen(board_logic)
    print("\n" + "="*40)
    print(" FINAL RESULT (FEN)")
    print("="*40)
    print(fen+" w - - 0 1")
    print("="*40)
    
    # Copy to clipboard
    try:
        pyperclip.copy(fen+" w - - 0 1")
        print("[OK] FEN copied! Use Ctrl+V to paste.")
    except Exception as e:
        print(f"[WARNING] Copy error: {e}")
    
    print("="*40)
    
    if DEBUG_VISUAL:
        cv2.imshow("Visual Check", debug_img)
        print("Press any key to close.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()