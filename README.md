# Computer Vision Chess

> Play chess using **real-time hand gesture recognition** — no physical interaction required.

---

## What is Computer Vision Chess?

A computer vision-based chess system that allows users to control a chess game using **hand gestures in real-time**.

This project combines **OpenCV, MediaPipe, Pygame, and the Stockfish chess engine** to create an interactive, AI-powered chess experience without using a mouse or keyboard.

---

## Features:

*  Hand gesture recognition (both hands)
*  Stable gesture detection with confirmation system
*  Fully functional chessboard UI
*  AI opponent powered by Stockfish
*  Smart state-based move selection (file → rank system)
*  Real-time camera input

---

##  Technology Implementation:

* Python
* OpenCV
* MediaPipe
* Pygame
* python-chess
* Stockfish Engine

---

## Project Structure:

```
Computer-Vision-Chess/
│
├── Game/
│   └── main.py
│
├── assets/
│   ├── wp.png
│   ├── bp.png
│   └── ...
│
├── Stockfish-windows/
└── README.md
```

---


##  Working Algorithm:

1. Detect hand landmarks using MediaPipe
2. Count fingers to determine input:
   * for File Selection: (Thumbs Don't Count)
      1. Left Hand's 4 fingers = File A to D
      2. Right Han's 4 fingers = File E to H
      3. Opposite Hand's Thumb = Confirmation
   * for Rank Selection: (Thumbs Don't Count)
      1. Left Hand's 4 fingers = Rank 5 to 8
      2. Right Hand's 4 fingers = Rank 1 to 4
      3. Opposite Hand's Thumb = Confirmation
    

3. Map gestures to:

   * File (a–h)
   * Rank (1–8)
4. Confirm selection using opposite thumb gesture
5. Construct move (e.g., `e2 → e4`)
6. Validate move using python-chess
7. Execute move and trigger Engine response

---

## Author

**Shreyash Dahiwale**  
Software Developer | Computer Science Student
