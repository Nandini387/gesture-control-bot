import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '2'

import cv2
import mediapipe as mp
import socket
import time

# ── WiFi settings ─────────────────────────────────────────
ESP32_IP   = '10.97.26.67'   # your ESP32 IP
ESP32_PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"Sending commands to {ESP32_IP}:{ESP32_PORT}")

# ── MediaPipe setup ───────────────────────────────────────
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
hands    = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.65
)

cap          = cv2.VideoCapture(0)
last_cmd     = ''
stable_count = 0
STABLE_FRAMES = 8   # increased for stability

# ── Finger counter (fixed for flipped camera) ─────────────
def count_fingers(lm):
    tips  = [8, 12, 16, 20]
    count = sum(1 for t in tips if lm.landmark[t].y < lm.landmark[t - 2].y)
    # Thumb fix for mirrored/flipped camera
    if lm.landmark[4].x > lm.landmark[2].x:
        count += 1
    return count

# ── Gesture → command ─────────────────────────────────────
def gesture_to_cmd(fingers):
    if fingers == 0: return 'S', 'STOP'
    if fingers == 1: return 'F', 'FORWARD'
    if fingers == 2: return 'B', 'BACKWARD'
    if fingers == 3: return 'L', 'TURN LEFT'
    if fingers == 4: return 'R', 'TURN RIGHT'
    return 'S', 'STOP'

# ── Send UDP command ──────────────────────────────────────
def send_cmd(cmd):
    try:
        sock.sendto(cmd.encode(), (ESP32_IP, ESP32_PORT))
        print(f"Sent: {cmd}")
    except Exception as e:
        print(f"UDP error: {e}")

# ── Gesture label colors ──────────────────────────────────
CMD_COLOR = {
    'F': (0, 220, 0),
    'B': (0, 100, 255),
    'L': (255, 180, 0),
    'R': (255, 60, 200),
    'S': (80, 80, 80),
}

print("Press Q to quit")
print("Gestures: Fist=STOP | 1 finger=FORWARD | 2=BACKWARD | 3=LEFT | 4=RIGHT")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame  = cv2.flip(frame, 1)
    h, w   = frame.shape[:2]
    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    pending_cmd   = 'S'
    pending_label = 'STOP'
    fingers       = 0

    if result.multi_hand_landmarks:
        for hl in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)
            fingers = count_fingers(hl)
            pending_cmd, pending_label = gesture_to_cmd(fingers)

            # Finger count badge
            cv2.putText(frame, f'Fingers: {fingers}', (30, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # Stability buffer — only send after 8 consistent frames
    if pending_cmd == last_cmd:
        stable_count += 1
    else:
        stable_count = 0
        last_cmd     = pending_cmd

    if stable_count == STABLE_FRAMES:
        send_cmd(pending_cmd)
        stable_count = STABLE_FRAMES + 1  # prevent repeat sending

    # Progress bar showing stability
    bar_w = int((min(stable_count, STABLE_FRAMES) / STABLE_FRAMES) * 200)
    cv2.rectangle(frame, (30, 125), (230, 140), (50, 50, 50), -1)
    color = CMD_COLOR.get(pending_cmd, (255, 255, 255))
    cv2.rectangle(frame, (30, 125), (30 + bar_w, 140), color, -1)
    cv2.putText(frame, 'Stability', (235, 138),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

    # Command label
    cv2.putText(frame, pending_label, (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.6, color, 3)

    # ESP32 IP watermark
    cv2.putText(frame, f'ESP32: {ESP32_IP}', (30, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)

    # Gesture guide bottom right
    guide = ['0=STOP', '1=FWD', '2=BWD', '3=LEFT', '4=RIGHT']
    for i, g in enumerate(guide):
        cv2.putText(frame, g, (w - 110, 30 + i * 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

    cv2.imshow('Hand Gesture Motor Control (WiFi)', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        send_cmd('S')
        break

cap.release()
sock.close()
cv2.destroyAllWindows()
print("Done.")