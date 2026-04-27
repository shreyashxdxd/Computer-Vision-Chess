import cv2
import mediapipe as mp
import pygame
import chess
import chess.engine
import time

# ================= ENGINE =================

engine = chess.engine.SimpleEngine.popen_uci("stockfish-windows-x86-64-avx2.exe")


# ================= PYGAME =================

pygame.init()
WIDTH = 640
HEIGHT = 700
SQ_SIZE = 640 // 8
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture Chess – Opposite Thumb Confirm")

font = pygame.font.SysFont("Arial", 22)

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
TEXT_COLOR = (20, 20, 20)

board = chess.Board()

pieces = {}

def load_images():
    names = ["wp","wr","wn","wb","wq","wk",
             "bp","br","bn","bb","bq","bk"]
    for name in names:
        img = pygame.image.load(f"assets/{name}.png")
        pieces[name] = pygame.transform.scale(img, (SQ_SIZE, SQ_SIZE))

def draw_board():
    for row in range(8):
        for col in range(8):
            color = LIGHT if (row + col) % 2 == 0 else DARK
            pygame.draw.rect(screen, color,
                             pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces():
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            key = ("w" if piece.color else "b") + piece.symbol().lower()
            screen.blit(pieces[key], (col*SQ_SIZE, row*SQ_SIZE))

def draw_text(state, detected, src, dst):
    y = 650
    lines = [
        f"STATE: {state}",
        f"Detected: {detected if detected else '-'}",
        f"SRC: {src}",
        f"DST: {dst}",
        f"TURN: {'White' if board.turn else 'Black'}"
    ]
    for i, line in enumerate(lines):
        render = font.render(line, True, TEXT_COLOR)
        screen.blit(render, (10, y - (100 - i*25)))

# ================= MEDIAPIPE =================

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)

FINGER_TIPS = [8,12,16,20]
FINGER_PIPS = [6,10,14,18]
THUMB_TIP = 4
THUMB_IP = 3

cap = cv2.VideoCapture(0)

# ================= STATE =================

state = "SRC_FILE"
src = ""
dst = ""

prev_thumb = {"Left":False, "Right":False}
last_confirm_time = 0
COOLDOWN = 0.5

def count_fingers(hand):
    count = 0
    for tip,pip in zip(FINGER_TIPS,FINGER_PIPS):
        if hand.landmark[tip].y < hand.landmark[pip].y:
            count += 1
    return count

def thumb_up(hand):
    return hand.landmark[THUMB_TIP].y < hand.landmark[THUMB_IP].y

def reset_selection():
    global state, src, dst
    state = "SRC_FILE"
    src = ""
    dst = ""

# ================= MAIN LOOP =================

load_images()
running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame,1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    cv2.imshow("Camera Debug", frame)
    cv2.waitKey(1)

    detected = None
    selecting_hand = None
    current_thumb = {"Left":False, "Right":False}

    if result.multi_hand_landmarks:
        for hand_lms, hand_info in zip(result.multi_hand_landmarks,
                                       result.multi_handedness):

            label = hand_info.classification[0].label
            fingers = count_fingers(hand_lms)

            # FILE
            if state in ["SRC_FILE","DST_FILE"]:
                if fingers in [1,2,3,4]:
                    selecting_hand = label
                    if label == "Left":
                        detected = chr(ord('a') + fingers - 1)
                    else:
                        detected = chr(ord('e') + fingers - 1)

            # RANK
            elif state in ["SRC_RANK","DST_RANK"]:
                if fingers in [1,2,3,4]:
                    selecting_hand = label
                    if label == "Right":
                        detected = str(fingers)
                    else:
                        detected = str(fingers + 4)

            current_thumb[label] = thumb_up(hand_lms)

    current_time = time.time()

    # ===== OPPOSITE THUMB CONFIRM =====
    for side in ["Left","Right"]:
        if (current_thumb[side] and not prev_thumb[side]
            and detected is not None
            and selecting_hand is not None
            and side != selecting_hand
            and current_time - last_confirm_time > COOLDOWN
            and board.turn == chess.WHITE):

            last_confirm_time = current_time
            print("Confirmed:", detected)

            if state == "SRC_FILE":
                src = detected
                state = "SRC_RANK"

            elif state == "SRC_RANK":
                src += detected
                state = "DST_FILE"

            elif state == "DST_FILE":
                dst = detected
                state = "DST_RANK"

            elif state == "DST_RANK":
                dst += detected
                move_string = src + dst
                print("Move:", move_string)

                try:
                    move = chess.Move.from_uci(move_string)
                    if move in board.legal_moves:
                        board.push(move)
                        print("White played:", move_string)

                        result_engine = engine.play(board, chess.engine.Limit(time=0.3))
                        board.push(result_engine.move)
                        print("Black played:", result_engine.move)
                    else:
                        print("Illegal move")
                except:
                    print("Invalid move")

                reset_selection()

    prev_thumb = current_thumb.copy()

    draw_board()
    draw_pieces()
    draw_text(state, detected, src, dst)

    pygame.display.flip()

cap.release()
engine.quit()
cv2.destroyAllWindows()
pygame.quit()
