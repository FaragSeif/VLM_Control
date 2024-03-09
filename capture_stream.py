import cv2
import threading
import queue


class Capture:
    def __init__(self, src=0):
        try:
            self.cap = cv2.VideoCapture(src)  # initialise empty VideoCapture class
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except:
            print("Cannot find IP or wrong Cam IP adress")
            print("terminating....")
            exit(1)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.q = queue.Queue()
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    def _reader(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                if not self.q.empty():
                    try:
                        self.q.get_nowait()  # Discard previous (unprocessed) frame
                    except queue.Empty:
                        pass
                self.q.put(frame)
        except:
            self.cap.release()
            exit(1)

    def read(self):
        frame = self.q.get()
        if frame is not None:
            return True, frame
        return False, None

    def release(self):
        self.cap.release()
