import os
import random
import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import drawing_styles, drawing_utils, HandLandmarksConnections
import pyautogui
from pynput.mouse import Button, Controller as MouseController
from pynput import keyboard
import util

pyautogui.FAILSAFE = False
mouse = MouseController()

screen_width, screen_height = pyautogui.size()
last_click_time = 0
last_screenshot_time = 0

# Keyboard tracking
last_key_name = "None"
last_key_time = 0

def on_key_press(key):
    global last_key_name, last_key_time
    try:
        last_key_name = f"'{key.char}'"
    except AttributeError:
        # Special key (e.g. Key.space, Key.enter)
        last_key_name = f"{key.name}".upper()
    last_key_time = time.time()

# Start global keyboard listener in a background thread
key_listener = keyboard.Listener(on_press=on_key_press)
key_listener.daemon = True
key_listener.start()

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hand_landmarker.task')
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)


def find_finger_tip(processed):
    if processed.hand_landmarks:
        hand_landmarks = processed.hand_landmarks[0]
        index_finger_tip = hand_landmarks[8]
        return index_finger_tip
    return None


def move_mouse(index_finger_tip):
    if index_finger_tip is not None:
        x = int(index_finger_tip.x * screen_width)
        y = int(index_finger_tip.y / 2 * screen_height)
        pyautogui.moveTo(x, y)
        return x, y
    return None, None


def is_left_click(landmark_list, thumb_index_dist):
    return (
            util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and
            util.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) > 90 and
            thumb_index_dist > 50
    )


def is_right_click(landmark_list, thumb_index_dist):
    return (
            util.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and
            util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 90 and
            thumb_index_dist > 50
    )


def is_double_click(landmark_list, thumb_index_dist):
    return (
            util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and
            util.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and
            thumb_index_dist > 50
    )


def is_screenshot(landmark_list, thumb_index_dist):
    return (
            util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and
            util.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and
            thumb_index_dist < 50
    )


def detect_gesture(frame, landmark_list, processed):
    global last_click_time, last_screenshot_time
    action = "Neutral"

    if len(landmark_list) >= 21:
        current_time = time.time()
        index_finger_tip = find_finger_tip(processed)
        thumb_index_dist = util.get_distance([landmark_list[4], landmark_list[5]])

        if thumb_index_dist < 50 and util.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 90:
            move_mouse(index_finger_tip)
            action = "Moving Mouse"
        elif is_left_click(landmark_list, thumb_index_dist):
            action = "Left Click"
            if current_time - last_click_time > 0.4:
                mouse.press(Button.left)
                mouse.release(Button.left)
                last_click_time = current_time
        elif is_right_click(landmark_list, thumb_index_dist):
            action = "Right Click"
            if current_time - last_click_time > 0.4:
                mouse.press(Button.right)
                mouse.release(Button.right)
                last_click_time = current_time
        elif is_double_click(landmark_list, thumb_index_dist):
            action = "Double Click"
            if current_time - last_click_time > 0.6:
                pyautogui.doubleClick()
                last_click_time = current_time
        elif is_screenshot(landmark_list, thumb_index_dist):
            action = "Screenshot"
            if current_time - last_screenshot_time > 1.5:
                try:
                    im1 = pyautogui.screenshot()
                    label = random.randint(1, 1000)
                    im1.save(f'my_screenshot_{label}.png')
                    last_screenshot_time = current_time
                except Exception as e:
                    print(f"Screenshot error: {e}")

    return action


def draw_hud(frame, hand_detected, action):
    h, w, _ = frame.shape
    current_time = time.time()

    # --- TOP BANNER (Translucent dark overlay) ---
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 70), (20, 20, 20), -1)
    # --- BOTTOM HINT BAR ---
    cv2.rectangle(overlay, (0, h - 35), (w, h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    # Hand status indicator
    if hand_detected:
        cv2.circle(frame, (25, 35), 8, (0, 255, 0), -1)
        cv2.putText(frame, "HAND: ACTIVE", (40, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    else:
        cv2.circle(frame, (25, 35), 8, (0, 0, 255), -1)
        cv2.putText(frame, "HAND: SEARCHING", (40, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 120, 255), 2)

    # Action / Gesture Badge
    action_color = (200, 200, 200)
    if action == "Left Click":
        action_color = (0, 255, 0)
    elif action == "Right Click":
        action_color = (0, 165, 255)
    elif action == "Double Click":
        action_color = (0, 255, 255)
    elif action == "Screenshot":
        action_color = (255, 0, 255)
    elif action == "Moving Mouse":
        action_color = (255, 200, 0)

    cv2.putText(frame, f"ACTION: {action}", (230, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.65, action_color, 2)

    # Key Press Badge (Highlights brightly for 1.5 seconds)
    time_since_key = current_time - last_key_time
    if time_since_key < 1.5 and last_key_name != "None":
        key_color = (0, 255, 255)
        key_text = f"KEY PRESSED: {last_key_name}"
    else:
        key_color = (160, 160, 160)
        key_text = f"LAST KEY: {last_key_name}"

    # Draw key badge at top-right
    text_size = cv2.getTextSize(key_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
    key_x = max(w - text_size[0] - 25, 450)
    cv2.putText(frame, key_text, (key_x, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.6, key_color, 2)

    # Bottom helper bar text
    hint_text = "Press 'q' to quit | Bend Index: Left Click | Bend Middle: Right Click | Pinch: Screenshot"
    cv2.putText(frame, hint_text, (15, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)


def get_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if cap.isOpened():
        ret, _ = cap.read()
        if ret:
            return cap
        cap.release()
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        return cap
    return None


def main():
    cap = get_camera()

    if cap is None:
        print("Error: Could not access webcam. Please check your camera connection.")
        return

    print("Camera started. Press 'q' in the window to quit.")
    window_name = 'Hand Gesture Mouse & Key Controller'
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    try:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    except Exception:
        pass

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frameRGB)
            processed = detector.detect(mp_image)

            landmark_list = []
            hand_detected = bool(processed.hand_landmarks)

            if hand_detected:
                hand_landmarks = processed.hand_landmarks[0]
                # Draw the skeletal hand connections
                drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks,
                    HandLandmarksConnections.HAND_CONNECTIONS,
                    drawing_styles.get_default_hand_landmarks_style(),
                    drawing_styles.get_default_hand_connections_style()
                )
                for lm in hand_landmarks:
                    landmark_list.append((lm.x, lm.y))

                # Highlight index fingertip with reticle for clear pointer tracking
                h, w, _ = frame.shape
                tip_x = int(hand_landmarks[8].x * w)
                tip_y = int(hand_landmarks[8].y * h)
                cv2.circle(frame, (tip_x, tip_y), 10, (0, 255, 255), -1)
                cv2.circle(frame, (tip_x, tip_y), 15, (0, 200, 255), 2)

            action = detect_gesture(frame, landmark_list, processed)

            # Draw the HUD showing hand status, current action, and keys pressed
            draw_hud(frame, hand_detected, action)

            cv2.imshow('Hand Gesture Mouse & Key Controller', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key != 255:
                # Also catch window-focused keys
                global last_key_name, last_key_time
                last_key_name = f"'{chr(key)}'" if 32 <= key <= 126 else f"CODE_{key}"
                last_key_time = time.time()

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
