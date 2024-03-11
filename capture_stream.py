import cv2
import threading
import queue


class Capture:
    """
        A class to manage the captured video stream in a separate thread
    """
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
        # initialize a separate thread for reading the next frame
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    def _reader(self):
        """
            Thread for reading the capture frame values
        """
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
        """
            Wrapper function for the camera thread
            Returns:
                Tuple(Bool, np.ndarray): a flag to verify frame availability, and the actual frame, (False, None) if no frame is returned.
        """
        frame = self.q.get()
        if frame is not None:
            return True, frame
        return False, None

    def release(self):
        """
            Release capture resources
        """
        self.cap.release()
