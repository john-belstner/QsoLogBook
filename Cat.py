import time
import serial
import configparser


bands = ["160M", "80M", "60M", "40M", "30M", "20M", "17M", "15M", "12M", "10M", "6M", "2M", "1.25M", "70CM", "33CM", "23CM", "13CM", "9CM", "6CM", "3CM"]
modes = ["NONE", "SSB", "SSB", "CW", "FM", "AM", "DIGI", "CW", "ERR", "DIGI"]

class Cat:

    def __init__(self, config: configparser.ConfigParser):
        self._com_port = config['CAT'].get('con_port', '/dev/ttyUSB0')
        self._baudrate = int(config['CAT'].get('baudrate', '38400'))
        self._freq_cmd = config['CAT'].get('freq_cmd', 'FA')
        self._band_cmd = config['CAT'].get('band_cmd', 'BN')
        self._mode_cmd = config['CAT'].get('mode_cmd', 'MD')
        self._ser = None

    def reload_config(self, config: configparser.ConfigParser):
        self._com_port = config['CAT'].get('com_port', '/dev/ttyUSB0')
        self._baudrate = int(config['CAT'].get('baudrate', '38400'))
        self._freq_cmd = config['CAT'].get('freq_cmd', 'FA')
        self._band_cmd = config['CAT'].get('band_cmd', 'BN')
        self._mode_cmd = config['CAT'].get('mode_cmd', 'MD')
        if self._ser and self._ser.is_open:
            self.disconnect()
            return self.connect()
        else:
            return True

    def connect(self):
        try:
            self._ser = serial.Serial(self._com_port, self._baudrate, timeout=1)
            time.sleep(0.200)  # Wait for the connection to establish
            if self._ser.is_open:
                #print(f"Connected to CAT Interface on {self._com_port} at {self._baudrate} baud.")
                return True
            else:
                #print(f"Failed to open serial port {self._com_port}.")
                return False
        except serial.SerialException as e:
            #print(f"Serial exception: {e}")
            return False

    def disconnect(self):
        if self._ser and self._ser.is_open:
            self._ser.close()
            #print("Disconnected from CAT Interface")

    def get_freq_band_mode(self):
        if not self._ser or not self._ser.is_open:
            #print("Serial port is not open.")
            return None, None
        else:
            self._ser.write(f"{self._freq_cmd};\n".encode("ascii"))
            self._ser.write(f"{self._band_cmd};\n".encode("ascii"))
            self._ser.write(f"{self._mode_cmd};\n".encode("ascii"))
            time.sleep(0.300)  # Wait for the radio to respond
            if self._ser.in_waiting > 0:
                response = self._ser.readline().decode("utf-8", errors="ignore").strip()
                #print("Received:", response)
            if response:
                #print(f"Raw response: {response}")
                freq = band = mode = None
                parts = response.split(';')
                for part in parts:
                    if part.startswith(self._freq_cmd):
                        if part[2:].isdigit():
                            freq = str(round(int(part[2:]) / 1000000, 3))  # Convert Hz to MHz
                    elif part.startswith(self._band_cmd):
                        if part[2:].isdigit():
                            band_code = int(part[2:])
                            if band_code < len(bands):
                                band = bands[band_code]
                    elif part.startswith(self._mode_cmd):
                       if part[2:].isdigit():
                            mode_code = int(part[2:])
                            if mode_code < len(modes):
                                mode = modes[mode_code]
                return freq, band, mode
            else:
                #print("No response received.")
                return None, None

