# 📘 QsoLogBook

**QsoLogBook** is a contact logging application for Amateur Radio operators, written in **Python 3** using **Tkinter** and **SQLite**.  
It manages station configuration, logs QSOs locally, integrates with **QRZ.com**, exports/imports **ADIF** files, and optionally uploads confirmed contacts to **LoTW (ARRL Logbook of The World)**.

---

## 🧑‍💻 Author
**John M. Belstner (W9EN)**  
© 2025 – Open-source for educational and Amateur Radio use, GNU General Public License v3.0 (GPL-3.0)

---

## ✨ Key Features

- 🗂️ **Local QSO Database**  
  - Logs all QSOs to a local SQLite database (`qso_log.db`).  
  - Supports full CRUD (Create, Read, Update, Delete) operations.  
  - Imports and exports standard **ADIF** files.

- 🔍 **QRZ.com Integration**  
  - Performs online callsign lookups using your QRZ credentials.  
  - Optionally uploads new QSOs to your QRZ Logbook via API.

- 📡 **CAT Radio Control**  
  - Connects to your transceiver via serial CAT interface.  
  - Automatically reads frequency, mode, and band information.  

- 🔒 **Encrypted Configuration Storage**  
  - Sensitive credentials (QRZ, LoTW passwords, and API keys) are **encrypted** using Fernet symmetric encryption.  
  - The encryption key is stored in your home directory at `~/.qsologbook.key` (permissions 600).

- 🌐 **LoTW Upload Support**  
  - Uses `tqsl` (TrustedQSL) command-line tool to sign ADIF files.  
  - Automatically uploads to LoTW using RFC-1867 protocol.

- 🧭 **Graphical User Interface**
  - Built with Tkinter and ttk for a clean, cross-platform experience.  
  - Displays recent QSOs, provides quick entry forms, and integrates lookup tools.  
  - Includes a dedicated **Configuration Settings** dialog.

---

## 📁 Project Structure

```
QsoLogBook.py          # Main application
ConfigWindow.py        # Configuration GUI (reads/writes config.ini)
Crypto.py              # Fernet encryption/decryption utilities
LogDatabase.py         # SQLite database handler for QSO records
QrzApi.py              # QRZ.com XML and Logbook API interface
Lotw.py                # LoTW upload/signing interface (via tqsl)
LastQSOs.py            # Recent QSOs table display (Treeview)
Cat.py                 # CAT serial interface for radio control
Qso.py                 # QSO record object (ADIF generation, validation)
config.ini             # Configuration file (encrypted credentials)
qso_log.db             # SQLite QSO database
```

---

## ⚙️ Installation and Setup

### 1️⃣ Prerequisites
Ensure the following are installed:
- Python **3.9+**
- `pip install cryptography requests pyserial configparser pathlib datetime tkinter sqlite3`
- **tqsl** command-line utility (for LoTW uploads)
- **QRZ.com** XML subscription (for lookups and uploads)

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/<yourusername>/QsoLogBook.git
cd QsoLogBook
```

### 3️⃣ Create or Edit `config.ini`
An example is included. Update with your callsign, credentials, and paths:

```ini
[MY_DETAILS]
call = W9XYZ
name = John Doe
addr = 123 N 4th St.
city = Cedarburg
state = WI
zip = 53012
my_grid = EN53xh

[QRZ]
username = W9XYZ
password = 
api_key  = 

[LOTW]
username = W9XYZ
password = 
location = Home QTH
certificate = w9xyz.p12
cert_password = 

[CAT]
com_port = /dev/ttyUSB0
baudrate = 38400
freq_cmd = FA
band_cmd = BN
mode_cmd = MD
```

The application automatically encrypts any passwords you save via the **Settings** dialog.

---

## 🪟 Running the Application

Launch the main program:
```bash
python3 QsoLogBook.py
```

You’ll see the main GUI containing:
- **Recent Contacts** panel (top)
- **QSO Entry Form** (bottom)
- **Menu Bar** with options to connect, configure, import/export, and exit.

---

## 🧭 Typical Workflow

1. **Connect Services**  
   - From the *Connect* menu:  
     - “Connect QRZ” → log into your QRZ.com account.  
     - “Connect CAT” → open serial link to your radio.

2. **Lookup a Callsign**  
   - Enter a callsign and click **Lookup**.  
   - The program fills name, grid, state, and country from QRZ.

3. **Log a QSO**  
   - Verify date/time (UTC) and band/mode fields.  
   - Click **Log QSO**.  
   - The entry is stored in `qso_log.db` and optionally uploaded to QRZ.

4. **Review and Edit**  
   - The “Recent Contacts” list shows the latest QSOs.  
   - Enter a QSO number and choose “Edit Log Entry” or “Delete Log Entry”.

5. **Import / Export ADIF**  
   - Use the *File* menu to import old logs or export for LoTW.

6. **Upload to LoTW**  
   - Export an ADIF file, then use **Lotw.py** to sign and upload:
     ```bash
     python3 Lotw.py mylog.adi
     ```

---

## 🔒 Encryption Details

- The file `Crypto.py` manages all secure storage using the **Fernet** cipher from `cryptography`.  
- A private key file `~/.qsologbook.key` is automatically created on first run.  
- If you move machines, you must also copy this key file to decrypt existing passwords.

---

## 🧰 Developer Notes

- Database table: `logbook`
- Primary key: `rowid` (auto-incremented)
- ADIF fields follow `ADIF 3.0.5` standard.
- GUI uses only the built-in `tkinter` and `ttk` libraries—no extra dependencies.
- Pythonic modular design: each subsystem (QRZ, LoTW, CAT, Crypto, Database) is isolated for clarity and testability.

---

## 🛠️ Troubleshooting

| Problem | Likely Cause | Solution |
|----------|---------------|-----------|
| Config window opens but fields are blank | Incorrect section/field name in `config.ini` | Ensure `[MY_DETAILS]`, `[QRZ]`, etc. match code. |
| Passwords not decrypting | Missing `~/.qsologbook.key` | Restore it from backup or delete to regenerate (then re-enter passwords). |
| CAT connection fails | Wrong COM port or baud rate | Verify settings in *Settings → CAT Interface*. |
| QRZ lookup fails | Invalid credentials or no XML subscription | Update credentials and verify QRZ access. |
| LoTW upload rejected | Wrong certificate password | Check certificate path and password in config. |

