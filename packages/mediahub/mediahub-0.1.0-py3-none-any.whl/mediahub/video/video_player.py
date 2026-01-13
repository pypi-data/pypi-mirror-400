# src/video/video_player.py
import cv2

class VideoPlayer:
    def __init__(self):
        self.cap = None

    def play(self, file_path):
        self.cap = cv2.VideoCapture(file_path)
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()
