import random
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time

# ────────────────────  SETUP  ────────────────────
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

detector = HandDetector(maxHands=1)

timer          = 0
stateResult    = False
startGame      = False
scores         = [0, 0]     # [AI, Player]
winner_text    = ""         # Shown when someone hits 5
WIN_SCORE      = 5          # points needed to win

# ────────────────────  GAME LOOP  ────────────────────
while True:
    # Background and webcam frame
    imgBG  = cv2.imread("BG.png")
    # --- Show Rules Box in the Middle of 1280x720 Screen ---

    # Define box size
    box_width = 400
    box_height = 100

    # Calculate center position
    x1 = 1280 // 2 - box_width // 2  # 640 - 200 = 440
    y1 = 720 // 2 - box_height // 2  # 360 - 50 = 310
    x2 = x1 + box_width              # 440 + 400 = 840
    y2 = y1 + box_height             # 310 + 100 = 410

    # Draw background box
    cv2.rectangle(imgBG, (x1+70, y1-157), (x2-70, y2-157), (168, 55, 241), -1)

    # Draw control texts
    cv2.putText(imgBG, "Controls:", (x1 + 130, y1 - 130), cv2.FONT_HERSHEY_PLAIN, 1.6, (255, 255, 255), 2) #25
    cv2.putText(imgBG, "  s - Start Round", (x1 + 70, y1 - 110), cv2.FONT_HERSHEY_PLAIN, 1.4, (0, 0, 0), 1) #v 45
    cv2.putText(imgBG, "  r - Restart", (x1 + 70, y1 - 90), cv2.FONT_HERSHEY_PLAIN, 1.4, (0, 0, 0), 1) # 65
    cv2.putText(imgBG, "  q - Quit", (x1 + 70, y1 - 70), cv2.FONT_HERSHEY_PLAIN, 1.4, (0, 0, 0), 1) # 85


    success, img = cap.read()

    # Resize and crop camera frame
    imgScaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
    imgScaled = imgScaled[:, 80:480]

    # Detect hands
    hands, img = detector.findHands(imgScaled)

    # If a winner already declared, just show message
    if winner_text:
        cv2.putText(
            imgBG,
            winner_text,
            (300, 430),
            cv2.FONT_HERSHEY_SIMPLEX,
            2.4,
            (0, 255, 0),
            5,
        )
    else:
        # ─────────────  GAME STARTED  ─────────────
        if startGame:

            # Show countdown for first 2 s
            if stateResult is False:
                timer = time.time() - initialTime
                cv2.putText(
                    imgBG,
                    str(int(timer)),
                    (605, 435),
                    cv2.FONT_HERSHEY_PLAIN,
                    6,
                    (255, 0, 255),
                    4,
                )

                # After 2 s evaluate moves
                if timer > 2:
                    stateResult = True
                    timer = 0

                    # Player move
                    if hands:
                        playerMove = None
                        hand = hands[0]
                        fingers = detector.fingersUp(hand)
                        if fingers == [0, 0, 0, 0, 0]:
                            playerMove = 1  # Rock
                        elif fingers == [1, 1, 1, 1, 1]:
                            playerMove = 2  # Paper
                        elif fingers == [0, 1, 1, 0, 0]:
                            playerMove = 3  # Scissors

                    # AI move
                    randomNumber = random.randint(1, 3)
                    imgAI = cv2.imread(f"{randomNumber}.png", cv2.IMREAD_UNCHANGED)

                    # Show AI move on BG
                    imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

                    # Scoring logic
                    if playerMove:
                        # Player wins
                        if (
                            (playerMove == 1 and randomNumber == 3)
                            or (playerMove == 2 and randomNumber == 1)
                            or (playerMove == 3 and randomNumber == 2)
                        ):
                            scores[1] += 1
                        # AI wins
                        elif (
                            (playerMove == 3 and randomNumber == 1)
                            or (playerMove == 1 and randomNumber == 2)
                            or (playerMove == 2 and randomNumber == 3)
                        ):
                            scores[0] += 1

                    # Check for winner
                    if scores[0] >= WIN_SCORE:
                        winner_text = "AI  WINS!"
                    elif scores[1] >= WIN_SCORE:
                        winner_text = "PLAYER  WINS!"

        # Embed webcam feed into background
        imgBG[234:654, 795:1195] = imgScaled

        # Keep AI move overlaid after result
        if stateResult and not winner_text:
            imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

    # Display scores
    cv2.putText(imgBG, str(scores[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

    # ---------------- Show windows ----------------
    cv2.imshow("BG", imgBG)

    # ---------------- Keyboard controls ----------------
    key = cv2.waitKey(1) & 0xFF
    if key == ord("s") and not winner_text:
        startGame   = True
        initialTime = time.time()
        stateResult = False
    elif key == ord("r"):
        # Reset everything
        scores       = [0, 0]
        startGame    = False
        stateResult  = False
        winner_text  = ""
        timer        = 0
    elif key == ord("q"):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
