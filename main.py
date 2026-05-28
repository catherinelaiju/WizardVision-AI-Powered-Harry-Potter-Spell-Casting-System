import cv2
import mediapipe as mp
import math
import pygame

# -----------------------------
# INITIALIZE SOUND SYSTEM
# -----------------------------
pygame.mixer.init()

fire_sound = pygame.mixer.Sound("sounds/fire.mp3")
lightning_sound = pygame.mixer.Sound("sounds/lightning.mp3")
shield_sound = pygame.mixer.Sound("sounds/shield.mp3")

# -----------------------------
# LOAD PNG IMAGES
# -----------------------------
fire_img = cv2.imread("images/fire.png", cv2.IMREAD_UNCHANGED)
shield_img = cv2.imread("images/shield.png", cv2.IMREAD_UNCHANGED)

# -----------------------------
# IMAGE OVERLAY FUNCTION
# -----------------------------
def overlay_png(background, overlay, x, y):

    h, w = overlay.shape[:2]

    # Prevent image going outside screen
    if x < 0 or y < 0:
        return

    if y + h > background.shape[0] or x + w > background.shape[1]:
        return

    # RGB channels
    overlay_rgb = overlay[:, :, :3]

    # Alpha channel
    mask = overlay[:, :, 3] / 255.0

    # Area where image will be placed
    roi = background[y:y+h, x:x+w]

    # Blend PNG with webcam frame
    for c in range(3):

        roi[:, :, c] = (
            roi[:, :, c] * (1 - mask) +
            overlay_rgb[:, :, c] * mask
        )

    background[y:y+h, x:x+w] = roi

# -----------------------------
# OPEN WEBCAM
# -----------------------------
cap = cv2.VideoCapture(0)

# -----------------------------
# MEDIAPIPE SETUP
# -----------------------------
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# -----------------------------
# STORE TRAIL POINTS
# -----------------------------
points = []

# Prevent sound spam
last_spell = ""

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:

    # Read webcam frame
    success, frame = cap.read()

    if not success:
        break

    # Flip webcam horizontally
    frame = cv2.flip(frame, 1)

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process hand tracking
    results = hands.process(rgb_frame)

    # -----------------------------
    # HAND DETECTION
    # -----------------------------
    if results.multi_hand_landmarks:

        # Count hands
        hand_count = len(results.multi_hand_landmarks)

        # -----------------------------
        # SHIELD SPELL
        # -----------------------------
        if hand_count == 2:

            cv2.putText(
                frame,
                "SHIELD SPELL!",
                (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (255, 255, 0),
                4
            )

            # Resize shield image
            shield_resized = cv2.resize(
                shield_img,
                (300, 300)
            )

            # Overlay shield
            overlay_png(frame, shield_resized, 170, 90)

            # Play sound once
            if last_spell != "shield":
                shield_sound.play()
                last_spell = "shield"

        # -----------------------------
        # LOOP THROUGH HANDS
        # -----------------------------
        for hand_landmarks in results.multi_hand_landmarks:

            # Draw hand skeleton
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # Index fingertip
            tip = hand_landmarks.landmark[8]

            # Frame dimensions
            h, w, c = frame.shape

            # Convert normalized coords → pixels
            x = int(tip.x * w)
            y = int(tip.y * h)

            # -----------------------------
            # WAND GLOW EFFECT
            # -----------------------------

            # Outer glow
            cv2.circle(
                frame,
                (x, y),
                40,
                (255, 255, 0),
                2
            )

            # Inner orb
            cv2.circle(
                frame,
                (x, y),
                20,
                (255, 0, 255),
                -1
            )

            # -----------------------------
            # MAGIC TRAIL
            # -----------------------------
            points.append((x, y))

            # Keep trail short
            if len(points) > 25:
                points.pop(0)

            # Draw trail
            for point in points:

                cv2.circle(
                    frame,
                    point,
                    5,
                    (0, 0, 255),
                    -1
                )

            # -----------------------------
            # FIRE SPELL
            # -----------------------------
            if len(points) > 20:

                start_x, start_y = points[0]
                end_x, end_y = points[-1]

                # Distance formula
                distance = math.sqrt(
                    (end_x - start_x) ** 2 +
                    (end_y - start_y) ** 2
                )

                # Circle motion detection
                if distance < 50:

                    cv2.putText(
                        frame,
                        "FIRE SPELL!",
                        (50, 170),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        (0, 0, 255),
                        4
                    )

                    # Resize fire image
                    fire_resized = cv2.resize(
                        fire_img,
                        (150, 150)
                    )

                    # Overlay fire
                    overlay_png(
                        frame,
                        fire_resized,
                        x - 75,
                        y - 75
                    )

                    # Play sound once
                    if last_spell != "fire":
                        fire_sound.play()
                        last_spell = "fire"

            # -----------------------------
            # LIGHTNING SPELL
            # -----------------------------
            if len(points) > 10:

                start_x, start_y = points[0]
                end_x, end_y = points[-1]

                # Upward movement
                dy = start_y - end_y

                # Detect fast upward swipe
                if dy > 150:

                    cv2.putText(
                        frame,
                        "LIGHTNING SPELL!",
                        (50, 240),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        (0, 255, 255),
                        4
                    )

                    # Lightning bolt
                    cv2.line(
                        frame,
                        (x, 0),
                        (x, y),
                        (0, 255, 255),
                        8
                    )

                    # Play sound once
                    if last_spell != "lightning":
                        lightning_sound.play()
                        last_spell = "lightning"

    else:
        # Reset spell tracking
        last_spell = ""

    # -----------------------------
    # SHOW WINDOW
    # -----------------------------
    cv2.imshow(
        "Harry Potter Spell System",
        frame
    )

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -----------------------------
# CLEANUP
# -----------------------------
cap.release()
cv2.destroyAllWindows()