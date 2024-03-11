import serial


class ExoConnection:
    """
        A class to establish serial communication with the wearable device
    """
    def __init__(self, port="COM1", baudrate=9600, timeout=0, write_timeout=0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = write_timeout
        self.connection = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout,
            write_timeout=self.write_timeout,
        )

    def send_compensation(self, compensation=b"0"):
        """
            A function to send the correct compensation value over serial
            Input:
                compensation(binary string): the compensation command in binary format
        """
        self.connection.write(compensation)

    def receive(self):
        """
            A function to send the correct compensation value over serial
            Returns:
                string: a string of sensor values, None if no data recieved.
        """
        data = self.connection.readline().decode("Ascii").strip("\r\n")
        return data if data else None
