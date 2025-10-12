# ConfigWindow.py
from tkinter import *
from tkinter import messagebox
import configparser
import Crypto


class ConfigWindow:

    def __init__(self, parent, config: configparser.ConfigParser):
        self.parent = parent
        self.config = config
        self.top = Toplevel(parent)
        self.top.title("Configuration Settings")
        self.top.transient(parent) # stay on top of parent
        self.top.grab_set()        # modal
        self._build_ui()

    def save_config(self):
        # Write to config file
        self.config['MY_DETAILS']['call'] = self.callEntry.get().strip().upper()
        self.config['MY_DETAILS']['name'] = self.nameEntry.get().strip()
        self.config['MY_DETAILS']['addr'] = self.addressEntry.get().strip()
        self.config['MY_DETAILS']['city'] = self.cityEntry.get().strip()
        self.config['MY_DETAILS']['state'] = self.stateEntry.get().strip().upper()
        self.config['MY_DETAILS']['zip'] = self.zipEntry.get().strip()
        self.config['MY_DETAILS']['my_grid'] = self.myGridEntry.get().strip()
        self.config['LOTW']['username'] = self.lotwUsernameEntry.get().strip()
        self.config['LOTW']['password'] = Crypto.encrypt_text(self.lotwPasswordEntry.get().strip())
        self.config['LOTW']['location'] = self.locationEntry.get().strip()
        self.config['LOTW']['upload'] = str(self.lotwUploadVar.get())
        self.config['CAT']['com_port'] = self.comPortEntry.get().strip()
        self.config['CAT']['baudrate'] = self.baudrateEntry.get().strip()
        self.config['CAT']['freq_cmd'] = self.freqCmdEntry.get().strip()
        self.config['CAT']['band_cmd'] = self.bandCmdEntry.get().strip()
        self.config['CAT']['mode_cmd'] = self.modeCmdEntry.get().strip()
        self.config['QRZ']['username'] = self.qrzUsernameEntry.get().strip()
        self.config['QRZ']['password'] = Crypto.encrypt_text(self.qrzPasswordEntry.get().strip())
        self.config['QRZ']['api_key'] = Crypto.encrypt_text(self.apiKeyEntry.get().strip())
        self.config['QRZ']['upload'] = str(self.qrzUploadVar.get())
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        messagebox.showinfo("Settings Saved", "Configuration settings have been saved.", parent=self.top)
        self.top.destroy()

    def _build_ui(self):
        self.detailsFrame = LabelFrame(self.top, text="My Details", padx=5, pady=5)
        self.detailsFrame.grid(row=0, column=0, padx=5, pady=5)

        self.callLabel = Label(self.detailsFrame, text="Callsign:")
        self.callLabel.grid(row=0, column=0, sticky=W)
        self.callEntry = Entry(self.detailsFrame, width=10)
        self.callEntry.grid(row=0, column=1, padx=5, pady=2)
        self.callEntry.insert(0, self.config.get('MY_DETAILS', 'call', fallback=""))

        self.nameLabel = Label(self.detailsFrame, text="Name:")
        self.nameLabel.grid(row=1, column=0, sticky=W)
        self.nameEntry = Entry(self.detailsFrame, width=20)
        self.nameEntry.grid(row=1, column=1, padx=5, pady=2)
        self.nameEntry.insert(0, self.config.get('MY_DETAILS', 'name', fallback=""))

        self.addressLabel = Label(self.detailsFrame, text="Address:")
        self.addressLabel.grid(row=2, column=0, sticky=W)
        self.addressEntry = Entry(self.detailsFrame, width=20)
        self.addressEntry.grid(row=2, column=1, padx=5, pady=2)
        self.addressEntry.insert(0, self.config.get('MY_DETAILS', 'addr', fallback=""))

        self.cityLabel = Label(self.detailsFrame, text="City:")
        self.cityLabel.grid(row=3, column=0, sticky=W)
        self.cityEntry = Entry(self.detailsFrame, width=20)
        self.cityEntry.grid(row=3, column=1, padx=5, pady=2)
        self.cityEntry.insert(0, self.config.get('MY_DETAILS', 'city', fallback=""))

        self.stateLabel = Label(self.detailsFrame, text="State:")
        self.stateLabel.grid(row=4, column=0, sticky=W)
        self.stateEntry = Entry(self.detailsFrame, width=4)
        self.stateEntry.grid(row=4, column=1, padx=5, pady=2, sticky=W)
        self.stateEntry.insert(0, self.config.get('MY_DETAILS', 'state', fallback=""))

        self.zipLabel = Label(self.detailsFrame, text="Zip:")
        self.zipLabel.grid(row=5, column=0, sticky=W)
        self.zipEntry = Entry(self.detailsFrame, width=10)
        self.zipEntry.grid(row=5, column=1, padx=5, pady=2, sticky=W)
        self.zipEntry.insert(0, self.config.get('MY_DETAILS', 'zip', fallback=""))

        self.myGridLabel = Label(self.detailsFrame, text="My Grid:")
        self.myGridLabel.grid(row=6, column=0, sticky=W)
        self.myGridEntry = Entry(self.detailsFrame, width=16)
        self.myGridEntry.grid(row=6, column=1, padx=5, pady=2, sticky=W)
        self.myGridEntry.insert(0, self.config.get('MY_DETAILS', 'my_grid', fallback=""))

        self.lotwFrame = LabelFrame(self.top, text="LoTW Settings", padx=5, pady=5)
        self.lotwFrame.grid(row=0, column=2, padx=5, pady=5)  # Set the frame position

        self.lotwUsernameLabel = Label(self.lotwFrame, text="Username:")
        self.lotwUsernameLabel.grid(row=0, column=0, sticky=W)
        self.lotwUsernameEntry = Entry(self.lotwFrame, width=16)
        self.lotwUsernameEntry.grid(row=0, column=1, padx=5, pady=2)
        self.lotwUsernameEntry.insert(0, self.config.get('LOTW', 'username', fallback=""))

        self.lotwPasswordLabel = Label(self.lotwFrame, text="Password:")
        self.lotwPasswordLabel.grid(row=1, column=0, sticky=W)
#        self.lotwPasswordEntry = Entry(self.lotwFrame, width=16, show="*")
        self.lotwPasswordEntry = Entry(self.lotwFrame, width=16)
        self.lotwPasswordEntry.grid(row=1, column=1, padx=5, pady=2)
        self.lotwPasswordEntry.insert(0, Crypto.decrypt_text(self.config.get('LOTW', 'password', fallback="")))

        self.locationLabel = Label(self.lotwFrame, text="Location:")
        self.locationLabel.grid(row=2, column=0, sticky=W)
        self.locationEntry = Entry(self.lotwFrame, width=16)
        self.locationEntry.grid(row=2, column=1, padx=5, pady=2)
        self.locationEntry.insert(0, self.config.get('LOTW', 'location', fallback=""))  

        upload_to_lotw = self.config.getboolean('LOTW', 'upload', fallback=False)
        self.lotwUploadVar = BooleanVar(value=upload_to_lotw)
        self.lotwUploadCheck = Checkbutton(
            self.lotwFrame,
            text="Upload QSOs to LoTW",
            variable=self.lotwUploadVar,
            onvalue=True,
            offvalue=False
        )
        self.lotwUploadCheck.grid(row=5, column=0, columnspan=2, sticky="w", pady=(5, 0))

        self.catFrame = LabelFrame(self.top, text="CAT Interface Settings", padx=5, pady=5)
        self.catFrame.grid(row=1, column=0, padx=5, pady=5)  # Set the frame position

        self.comPortLabel = Label(self.catFrame, text="COM Port:")
        self.comPortLabel.grid(row=0, column=0, sticky=W)
        self.comPortEntry = Entry(self.catFrame, width=16)
        self.comPortEntry.grid(row=0, column=1, padx=5, pady=2)
        self.comPortEntry.insert(0, self.config.get('CAT', 'com_port', fallback=""))

        self.baudrateLabel = Label(self.catFrame, text="Baudrate:")
        self.baudrateLabel.grid(row=1, column=0, sticky=W)
        self.baudrateEntry = Entry(self.catFrame, width=16)
        self.baudrateEntry.grid(row=1, column=1, padx=5, pady=2)
        self.baudrateEntry.insert(0, self.config.get('CAT', 'baudrate', fallback=""))

        self.freqCmdLabel = Label(self.catFrame, text="Freq Cmd:")
        self.freqCmdLabel.grid(row=2, column=0, sticky=W)
        self.freqCmdEntry = Entry(self.catFrame, width=16)
        self.freqCmdEntry.grid(row=2, column=1, padx=5, pady=2)
        self.freqCmdEntry.insert(0, self.config.get('CAT', 'freq_cmd', fallback=""))

        self.bandCmdLabel = Label(self.catFrame, text="Band Cmd:")
        self.bandCmdLabel.grid(row=3, column=0, sticky=W)
        self.bandCmdEntry = Entry(self.catFrame, width=16)
        self.bandCmdEntry.grid(row=3, column=1, padx=5, pady=2)
        self.bandCmdEntry.insert(0, self.config.get('CAT', 'band_cmd', fallback=""))

        self.modeCmdLabel = Label(self.catFrame, text="Mode Cmd:")
        self.modeCmdLabel.grid(row=4, column=0, sticky=W)
        self.modeCmdEntry = Entry(self.catFrame, width=16)
        self.modeCmdEntry.grid(row=4, column=1, padx=5, pady=2)
        self.modeCmdEntry.insert(0, self.config.get('CAT', 'mode_cmd', fallback=""))

        self.qrzFrame = LabelFrame(self.top, text="QRZ.com Settings", padx=5, pady=5)
        self.qrzFrame.grid(row=0, column=1, padx=5, pady=5)  # Set the frame position

        self.qrzUsernameLabel = Label(self.qrzFrame, text="Username:")
        self.qrzUsernameLabel.grid(row=0, column=0, sticky=W)
        self.qrzUsernameEntry = Entry(self.qrzFrame, width=18)
        self.qrzUsernameEntry.grid(row=0, column=1, padx=5, pady=2)
        self.qrzUsernameEntry.insert(0, self.config.get('QRZ', 'username', fallback=""))

        self.qrzPasswordLabel = Label(self.qrzFrame, text="Password:")
        self.qrzPasswordLabel.grid(row=1, column=0, sticky=W)
#        self.qrzPasswordEntry = Entry(self.qrzFrame, width=18, show="*")
        self.qrzPasswordEntry = Entry(self.qrzFrame, width=18)
        self.qrzPasswordEntry.grid(row=1, column=1, padx=5, pady=2)
        self.qrzPasswordEntry.insert(0, Crypto.decrypt_text(self.config.get('QRZ', 'password', fallback="")))

        self.apiKeyLabel = Label(self.qrzFrame, text="API Key:")
        self.apiKeyLabel.grid(row=2, column=0, sticky=W)
#        self.apiKeyEntry = Entry(self.qrzFrame, width=18, show="*")
        self.apiKeyEntry = Entry(self.qrzFrame, width=18)
        self.apiKeyEntry.grid(row=2, column=1, padx=5, pady=2)
        self.apiKeyEntry.insert(0, Crypto.decrypt_text(self.config.get('QRZ', 'api_key', fallback="")))

        upload_to_qrz = self.config.getboolean('QRZ', 'upload', fallback=False)
        self.qrzUploadVar = BooleanVar(value=upload_to_qrz)
        self.qrzUploadCheck = Checkbutton(
            self.qrzFrame,
            text="Upload QSOs to QRZ.com",
            variable=self.qrzUploadVar,
            onvalue=True,
            offvalue=False
        )
        self.qrzUploadCheck.grid(row=3, column=0, columnspan=2, sticky="w", pady=(5, 0))

        self.saveButton = Button(self.top, text="Save", command=self.save_config)
        self.saveButton.grid(row=1, column=1, columnspan=2, pady=10) # Centered below all frames

        self.top.protocol("WM_DELETE_WINDOW", self._config_exit)

    def _config_exit(self):
        close = messagebox.askyesno("Quit?", "Are you sure you want to quit without saving?", parent=self.top)
        if close:
            self.top.destroy()

