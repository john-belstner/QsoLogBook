#!/usr/bin/env python3
import configparser
import shutil
import time
from QrzApi import QrzApi
from Lotw import Lotw
from Qso import Qso
from Cat import Cat
from Cat import bands, modes
from LastQSOs import LastQSOs
from ConfigWindow import ConfigWindow
from LogDatabase import LogDatabase as Db
from pathlib import Path
from datetime import datetime, timezone
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox


appVersion = "0.6"
app = Tk()
app.title('QSO Log Book by W9EN - v' + appVersion)

POLL_INTERVAL_MS = 5000  # Update the Radio Settings periodically (if connected)

# Some global variables
band_var = StringVar(app)
band_var.set(bands[0]) # default value

mode_var = StringVar(app)
mode_var.set(modes[0]) # default value

propModes = ["N/A", "AS", "AUR", "BS", "EME", "ES", "F2", "GWAVE", "INTERNET", "LOS", "MS", "RPT", "SAT", "TR"]
propMode_var = StringVar(app)
propMode_var.set(propModes[0]) # default value

lotw = None
ldb = None
qrz_logged_in = False
qrz = None
cat_connected = False
cat = None


# Application exit function
def app_exit():
    close = messagebox.askyesno("Exit?", "Are you sure you want to exit the application?", parent=app)
    if close:
        ldb.close()
        if cat and cat_connected:
            cat.disconnect()
        app.destroy()

app.protocol("WM_DELETE_WINDOW", app_exit)


# Message box functions
def showInfo(message):
    response = messagebox.showinfo("Status", message, parent=app)
    return response

def showWarning(message):
    response = messagebox.showwarning("Warning", message, parent=app)
    return response

def showError(message):
    response = messagebox.showerror("Error", message, parent=app)
    return response


# A basic type-to-complete behavior for a ttk.Combobox in state='normal'
def attach_autocomplete_to_combobox(cb, values):
    type_buffer = {"last": 0}

    def on_keyrelease(event):
        # Ignore nav/control keys so we don't fight the user
        if event.keysym in ("BackSpace","Left","Right","Home","End","Up","Down",
                            "Return","Escape","Tab"):
            return

        typed = cb.get()
        if not typed:
            return

        # Find first prefix match
        match = next((v for v in values if v.lower().startswith(typed.lower())), None)
        if match:
            cb.set(match)
            # put the cursor after what the user typed, and select the remainder
            cb.icursor(len(typed))
            cb.select_range(len(typed), "end")

    cb.bind("<KeyRelease>", on_keyrelease)


# To accommodate custom <Tab> order
def focus_next_widget(event, next_widget):
    next_widget.focus_set()
    return "break"  # prevent default tab behavior


# Read config file
config = configparser.ConfigParser()
config_file = 'config.ini'
if Path(config_file).exists():
    config.read(config_file)
else:
    showError("No config file found. Please create a config.ini file.")


# Open the Log Database
if 'MY_DETAILS' in config and 'my_grid' in config['MY_DETAILS']:
    my_grid = config['MY_DETAILS']['my_grid']
    ldb = Db(my_grid)
else:
    showWarning("Config file is missing my_grid. Please update the config.ini file.")
    ldb = Db()  # Use default values


# LoTW Login
def lotw_login():
    global lotw
    if 'LOTW' not in config or 'location' not in config['LOTW'] or 'upload' not in config['LOTW']:
        showWarning("Config file is missing LOTW location or upload. Please update the config.ini file.")
        return
    if shutil.which("tqsl"):
        showInfo("TQSL installation found in PATH.")
    else:
        showWarning("TQSL is NOT installed or not in PATH.")
    try:
        lotw = Lotw(config)
    except Exception as e:
        showError(f"An error occurred during LOTW class initialization: {str(e)}")


# QRZ Login
def qrz_login():
    global qrz_logged_in, qrz
    # Check if already logged in
    if qrz and qrz_logged_in:
        showInfo("Already logged into QRZ.com")
        return
    if 'QRZ' not in config or 'username' not in config['QRZ'] or 'password' not in config['QRZ']:
        showWarning("Config file is missing QRZ username or password. Please update the config.ini file.")
        return
    try:
        qrz = QrzApi(config)
        qrz_logged_in = qrz.login()
        if qrz_logged_in:
            showInfo("Successfully logged into QRZ.com")
        else:
            showError(f"Failed to log into QRZ. Please check your credentials.")
    except Exception as e:
        showError(f"An error occurred during QRZ login: {str(e)}")


# CAT Connect
def cat_connect():
    global cat_connected, cat
    # Check if already connected
    if cat and cat_connected:
        showInfo("Already connected to CAT")
        return
    config.read(config_file)
    try:
        cat = Cat(config)
        cat_connected = cat.connect()
        if cat_connected:
            showInfo(f"Successfully connected {cat._com_port} at {cat._baudrate} baud.")
        else:
            showError(f"Failed to connect on {cat._com_port}.")
    except Exception as e:
        showError(f"An error occurred during CAT connection: {str(e)}")


# Menu functions
def import_log():
    adif_file = filedialog.askopenfilename(initialdir=".", title="Select .adi File", filetypes=(("adif files", "*.adi"), ("all files", "*.*")))
    # Create a popup telling the user that the import is in progress
    popup = Toplevel(app)
    popup.title("Importing Log")
    Label(popup, text="Importing ADIF log, please wait...").pack(padx=20, pady=20)
    app.update_idletasks()  # Ensure the popup is drawn before starting the import

    success, reason = ldb.import_from_adif(adif_file)
    popup.destroy()  # Close the popup after import is done
    if success:
        showInfo("ADIF log imported successfully.")
        clear_entries()
    else:
        showError(f"Failed to import ADIF log: {reason}")

def export_log():
    adif_file = filedialog.asksaveasfilename(initialdir=".", title="Save .adi File", defaultextension=".adi", filetypes=(("adif files", "*.adi"), ("all files", "*.*")))
    # Create a popup telling the user that the imporexport is in progress
    popup = Toplevel(app)
    popup.title("Exporting Log")
    Label(popup, text="Exporting ADIF log, please wait...").pack(padx=20, pady=20)
    app.update_idletasks()  # Ensure the popup is drawn before starting the export

    success, reason = ldb.export_to_adif(adif_file, appVersion)
    popup.destroy()  # Close the popup after export is done
    if success:
        showInfo("ADIF log exported successfully.")
    else:
        showError(f"Failed to export ADIF log: {reason}")

def config_settings():
    global qrz_logged_in, qrz, cat_connected, cat
    dlg = ConfigWindow(app, config)
    app.wait_window(dlg.top)
    # After the dialog is closed, reload the config
    if qrz and qrz_logged_in:
        qrz.reload_config(config)
        qrz_logged_in = qrz.login()
        if qrz_logged_in:
            showInfo("Successfully re-logged into QRZ.com")
        else:
            showError(f"Failed to re-log into QRZ. Please check your credentials.")
    # If CAT was connected, reconnect with new settings
    if cat and cat_connected:
        if cat.reload_config(config):
            showInfo(f"Successfully reconnected {cat._com_port} at {cat._baudrate} baud.")
        else:
            showError(f"Failed to reconnect on {cat._com_port}.")
    if lotw:
        lotw.reload_config(config)
    # Update my_grid in the database if it was changed
    if 'MY_DETAILS' in config and 'my_grid' in config['MY_DETAILS']:
        new_grid = config['MY_DETAILS']['my_grid']
        ldb.update_my_grid(new_grid)
    else:
        showWarning("Config file is missing my_grid. Please update the config.ini file.")


# Create the File menu
menubar = Menu(app)
file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label="Import ADIF", command=import_log)
file_menu.add_command(label="Export ADIF", command=export_log)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=app_exit)
menubar.add_cascade(label="File", menu=file_menu)

# Create the Connect menu
connect_menu = Menu(menubar, tearoff=0)
connect_menu.add_command(label="Connect CAT", command=cat_connect)
connect_menu.add_command(label="Connect QRZ", command=qrz_login)
connect_menu.add_command(label="Connect LoTW", command=lotw_login)
menubar.add_cascade(label="Connect", menu=connect_menu)

# Create the Config menu
config_menu = Menu(menubar, tearoff=0)
config_menu.add_command(label="Settings", command=config_settings)
menubar.add_cascade(label="Config", menu=config_menu)

# Root view
previewFrame = LabelFrame(app, text="Recent Contacts", padx=5, pady=5)
previewFrame.grid(row=0, column=0, padx=5, pady=5)  # Set the frame position
previewFrame.grid_columnconfigure(0, minsize=972)

qsoFrame = LabelFrame(app, text="QSO Entry", padx=5, pady=5)
qsoFrame.grid(row=1, column=0, padx=5, pady=5)  # Set the frame position
minColumnWidth = 106
qsoFrame.grid_columnconfigure(0, minsize=minColumnWidth)
qsoFrame.grid_columnconfigure(1, minsize=minColumnWidth)
qsoFrame.grid_columnconfigure(2, minsize=minColumnWidth)
qsoFrame.grid_columnconfigure(3, minsize=minColumnWidth)
qsoFrame.grid_columnconfigure(4, minsize=minColumnWidth)
qsoFrame.grid_columnconfigure(5, minsize=minColumnWidth)
qsoFrame.grid_columnconfigure(6, minsize=minColumnWidth)
qsoFrame.grid_columnconfigure(7, minsize=minColumnWidth)
qsoFrame.grid_columnconfigure(8, minsize=minColumnWidth)

# QSO Entry Frame
callsignLabel = Label(qsoFrame, text="Callsign")  # Create a label widget
callsignLabel.grid(row=0, column=0)  # Put the label into the window
callsignEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
callsignEntry.grid(row=1, column=0)  # Set the input box position

nameLabel = Label(qsoFrame, text="Name")  # Create a label widget
nameLabel.grid(row=0, column=1)  # Put the label into the window
nameEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
nameEntry.grid(row=1, column=1)  # Set the input box position

dateLabel = Label(qsoFrame, text="Date")  # Create a label widget
dateLabel.grid(row=0, column=2)  # Put the label into the window
dateEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
dateEntry.grid(row=1, column=2)  # Set the input box position

timeLabel = Label(qsoFrame, text="Time")  # Create a label widget
timeLabel.grid(row=0, column=3)  # Put the label into the window
timeEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
timeEntry.grid(row=1, column=3)  # Set the input box position

bandLabel = Label(qsoFrame, text="Band")  # Create a label widget
bandLabel.grid(row=0, column=4)  # Put the label into the window
bandMenu = ttk.Combobox(qsoFrame, textvariable=band_var, values=bands, state="normal")
bandMenu.grid(row=1, column=4, padx=5, pady=5)
bandMenu.config(width=8)
attach_autocomplete_to_combobox(bandMenu, bands)

modeLabel = Label(qsoFrame, text="Mode")  # Create a label widget
modeLabel.grid(row=0, column=6)  # Put the label into the window
modeMenu = ttk.Combobox(qsoFrame, textvariable=mode_var, values=modes, state="normal")
modeMenu.grid(row=1, column=6, padx=5, pady=5)
modeMenu.config(width=10)
attach_autocomplete_to_combobox(modeMenu, modes)

reportLabel = Label(qsoFrame, text="Report")  # Create a label widget
reportLabel.grid(row=2, column=5)  # Put the label into the window
reportEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
reportEntry.grid(row=3, column=5)  # Set the input box position

propModeLabel = Label(qsoFrame, text="PropMode")  # Create a label widget
propModeLabel.grid(row=0, column=7)  # Put the label into the window
propModeMenu = ttk.Combobox(qsoFrame, textvariable=propMode_var, values=propModes, state="normal")
propModeMenu.grid(row=1, column=7, padx=5, pady=5)
propModeMenu.config(width=10)
attach_autocomplete_to_combobox(propModeMenu, propModes)

satelliteLabel = Label(qsoFrame, text="Satellite")  # Create a label widget
satelliteLabel.grid(row=0, column=8)  # Put the label into the window
satelliteEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
satelliteEntry.grid(row=1, column=8)  # Set the input box position  
satelliteEntry.insert(0, "None")

gridLabel = Label(qsoFrame, text="Grid")  # Create a label widget
gridLabel.grid(row=2, column=0)  # Put the label into the window
gridEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
gridEntry.grid(row=3, column=0)  # Set the input box position

countyLabel = Label(qsoFrame, text="County")  # Create a label widget
countyLabel.grid(row=2, column=1)  # Put the label into the window
countyEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
countyEntry.grid(row=3, column=1)  # Set the input box position

stateLabel = Label(qsoFrame, text="State")  # Create a label widget
stateLabel.grid(row=2, column=2)  # Put the label into the window
stateEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
stateEntry.grid(row=3, column=2)  # Set the input box position

countryLabel = Label(qsoFrame, text="Country")  # Create a label widget
countryLabel.grid(row=2, column=3)  # Put the label into the window
countryEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
countryEntry.grid(row=3, column=3)  # Set the input box position

cqLabel = Label(qsoFrame, text="CQ Zone")  # Create a label widget
cqLabel.grid(row=2, column=4)  # Put the label into the window
cqEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
cqEntry.grid(row=3, column=4)  # Set the input box position

freqLabel = Label(qsoFrame, text="Freq MHz")  # Create a label widget
freqLabel.grid(row=0, column=5)  # Put the label into the window
freqEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
freqEntry.grid(row=1, column=5)  # Set the input box position

remarksLabel = Label(qsoFrame, text="Remarks")  # Create a label widget
remarksLabel.grid(row=2, column=6, columnspan=3)  # Put the label into the window
remarksEntry = Entry(qsoFrame, width=42, borderwidth=2)  # Create an input box
remarksEntry.grid(row=3, column=6, columnspan=3)  # Set the input box position

qsoNumberEntry = Entry(qsoFrame, width=10, borderwidth=2)  # Create an input box
qsoNumberEntry.grid(row=5, column=8)  # Set the input box

def display_qso_number(id: int):
    qsoNumberEntry.delete(0, END)
    qsoNumberEntry.insert(0, str(id))

# Recent Contacts Frame
last_qsos = LastQSOs(previewFrame, ldb.conn, display_qso_number)
last_qsos.pack(fill="both", expand=True)
last_qsos.refresh()


# Button function (Clear)
def clear_entries():
    callsignEntry.delete(0, END)
    nameEntry.delete(0, END)
    dateEntry.delete(0, END)
    timeEntry.delete(0, END)
    #band_var.set(bands[0])
    #mode_var.set(modes[0])
    reportEntry.delete(0, END)
    propMode_var.set(propModes[0])
    satelliteEntry.delete(0, END)
    satelliteEntry.insert(0, "None")
    gridEntry.delete(0, END)
    countyEntry.delete(0, END)
    stateEntry.delete(0, END)
    countryEntry.delete(0, END)
    cqEntry.delete(0, END)
    freqEntry.delete(0, END)
    remarksEntry.delete(0, END)
    display_qso_number(ldb.get_last_rowid() + 1)
    last_qsos.refresh()
    callsignEntry.focus_set()


# Periodic CAT update
def update_radio_settings():
    if cat and cat_connected:
        try:
            freq, band, mode = cat.get_freq_band_mode()
            #print(f"Freq: {freq}, Band: {band}, Mode: {mode}")
            freqEntry.delete(0, END)
            freqEntry.insert(0, freq)
            band_var.set(band)
            mode_var.set(mode)
        except Exception as e:
            showError(f"An error occurred while updating radio settings: {str(e)}")
    app.after(POLL_INTERVAL_MS, update_radio_settings)


# Button function (Lookup)
def lookup_call(event=None):
    callsignEntry_value = callsignEntry.get().strip().upper()
    if callsignEntry_value == "":
        showWarning("Please enter a callsign to look up.")
        callsignEntry.focus_set()
        return "break"
    if not qrz_logged_in:
        showWarning("Please log into QRZ first.")
        callsignEntry.focus_set()
        return "break"
    callsignEntry.delete(0, END)
    callsignEntry.insert(0, callsignEntry_value)
    try:
        result = qrz.lookup(callsignEntry_value)
        call_info = result['Callsign']
        nameEntry.delete(0, END)
        if 'fname' in call_info and 'name' in call_info and call_info['fname'] is not None and call_info['name'] is not None:
            nameEntry.insert(0, call_info.get('fname', '') + ' ' + call_info.get('name', ''))
        gridEntry.delete(0, END)
        if 'grid' in call_info and call_info['grid'] is not None:
            gridEntry.insert(0, call_info.get('grid', ''))
        countyEntry.delete(0, END)
        if 'county' in call_info and call_info['county'] is not None:
            countyEntry.insert(0, call_info.get('county', ''))
        stateEntry.delete(0, END)
        if 'state' in call_info and call_info['state'] is not None:
            stateEntry.insert(0, call_info.get('state', ''))
        countryEntry.delete(0, END)
        if 'country' in call_info and call_info['country'] is not None:
            countryEntry.insert(0, call_info.get('country', ''))
        cqEntry.delete(0, END)
        if 'cqzone' in call_info and call_info['cqzone'] is not None:
            cqEntry.insert(0, call_info.get('cqzone', ''))
        current_time = datetime.now(timezone.utc)
        dateEntry.delete(0, END)
        dateEntry.insert(0, current_time.strftime('%Y-%m-%d'))
        timeEntry.delete(0, END)
        timeEntry.insert(0, current_time.strftime('%H%M'))
        if cat_connected:
            freq, band, mode = cat.get_freq_band_mode()
            #print(f"Freq: {freq}, Band: {band}, Mode: {mode}")
            freqEntry.delete(0, END)
            freqEntry.insert(0, freq)
            band_var.set(band)
            mode_var.set(mode)
        last_qsos.lookup(callsignEntry_value)
        nameEntry.focus_set()
        return "break"
    except Exception as e:
        showError(f"An error occurred during QRZ lookup: {str(e)}")


# Button function (Log QSO)
def log_qso(event=None):
    new_qso = Qso(
        qso_id = qsoNumberEntry.get().strip(),
        callsign = callsignEntry.get().strip().upper(),
        name = nameEntry.get().strip(),
        date = dateEntry.get().strip(),
        time = timeEntry.get().strip(),
        band = band_var.get(),
        mode = mode_var.get(),
        report = reportEntry.get().strip(),
        prop_mode = propMode_var.get(),
        satellite = satelliteEntry.get().strip(),
        grid = gridEntry.get().strip().upper(),
        county = countyEntry.get().strip(),
        state = stateEntry.get().strip().upper(),
        country = countryEntry.get().strip(),
        cq = cqEntry.get().strip(),
        freq = freqEntry.get().strip(),
        remarks = remarksEntry.get().strip(),
        my_grid = ldb.my_grid
    )

    if not new_qso.is_valid():
        showWarning("Please fill in at least Callsign, Date, Time, Band and Mode fields.")
        return
    try:
        if int(new_qso.qso_id) > ldb.get_last_rowid():
            ldb.insert_qso(new_qso)
            showInfo(f"QSO with {new_qso.callsign} logged successfully.")
        else:
            ldb.update_qso(new_qso)
            showInfo(f"QSO ID {new_qso.qso_id} updated successfully.")
        if qrz_logged_in and config.getboolean('QRZ', 'upload', fallback=False):
            result, count, logid, reason = qrz.upload_qso(new_qso)
            if result == "OK":
                showInfo(f"QSO uploaded to QRZ successfully (LogID={logid})")
            else:
                showError(f"QSO upload failed, REASON= {reason})")
        if lotw and config.getboolean('LOTW', 'upload', fallback=False):
            lotw.tqsl_sign_and_upload(new_qso.to_adif(), "compliant")
    except Exception as e:
        showError(f"An error occurred while logging the QSO: {str(e)}")

    clear_entries()
    

def next_qso_in_db():
    display_qso_number(ldb.get_last_rowid() + 1)
    

def load_qso_from_db():
    rowid = qsoNumberEntry.get().strip()
    if rowid == "":
        showWarning("Please enter a QSO number to load.")
        return
    try:
        qso = ldb.fetch_qso_by_id(rowid)
        if qso is None:
            showWarning(f"No QSO found with ID {rowid}.")
            return
        # Assuming the order of columns in the database matches the following:
        # (rowid, Call, Name, Date, Time, Band, Mode, Report, PropMode, Satellite, Grid, County, State, Country, CQ, ITU, Remarks, My_Grid)
        callsignEntry.delete(0, END)
        callsignEntry.insert(0, qso[Db.columns.index("Call")])
        nameEntry.delete(0, END)
        nameEntry.insert(0, qso[Db.columns.index("Name")])
        dateEntry.delete(0, END)
        dateEntry.insert(0, qso[Db.columns.index("Date")])
        timeEntry.delete(0, END)
        timeEntry.insert(0, qso[Db.columns.index("Time")])
        band_var.set(qso[Db.columns.index("Band")])
        mode_var.set(qso[Db.columns.index("Mode")])
        reportEntry.delete(0, END)
        reportEntry.insert(0, qso[Db.columns.index("Report")])
        propMode_var.set(qso[Db.columns.index("PropMode")])
        satelliteEntry.delete(0, END)
        satelliteEntry.insert(0, qso[Db.columns.index("Satellite")])
        gridEntry.delete(0, END)
        gridEntry.insert(0, qso[Db.columns.index("Grid")])
        countyEntry.delete(0, END)
        countyEntry.insert(0, qso[Db.columns.index("County")])
        stateEntry.delete(0, END)
        stateEntry.insert(0, qso[Db.columns.index("State")])
        countryEntry.delete(0, END)
        countryEntry.insert(0, qso[Db.columns.index("Country")])
        cqEntry.delete(0, END)
        cqEntry.insert(0, qso[Db.columns.index("CQ")])
        freqEntry.delete(0, END)
        freqEntry.insert(0, qso[Db.columns.index("Freq")])
        remarksEntry.delete(0, END)
        remarksEntry.insert(0, qso[Db.columns.index("Remarks")])
    except Exception as e:
        showError(f"An error occurred while loading QSO: {str(e)}")

def delete_qso_from_db():
    rowid = qsoNumberEntry.get().strip()
    if rowid == "":
        showWarning("Please enter a QSO number to delete.")
        return
    try:
        qso = ldb.fetch_qso_by_id(rowid)
        if qso is None:
            showWarning(f"No QSO found with ID {rowid}.")
            return
        confirm = messagebox.askyesno("Delete QSO Entry", f"Are you sure you want to delete QSO ID {rowid}?", parent=app)
        if confirm:
            ldb.delete_qso(rowid)
            showInfo(f"QSO ID {rowid} has been deleted.")
            clear_entries()
    except Exception as e:
        showError(f"An error occurred while deleting QSO: {str(e)}")

# Buttons
lookupButton = Button(qsoFrame, text="Lookup", command=lookup_call)
lookupButton.grid(row=5, column=0, padx=5, pady=5)
lookupButton.config(width=8)
callsignEntry.bind("<Return>", lookup_call)

logButton = Button(qsoFrame, text="Log QSO", command=log_qso)
logButton.grid(row=5, column=1, padx=5, pady=5)
logButton.config(width=8)
remarksEntry.bind("<Return>", log_qso)

clearButton = Button(qsoFrame, text="Clear", command=clear_entries)
clearButton.grid(row=5, column=2, padx=5, pady=5)
clearButton.config(width=8)

nextButton = Button(qsoFrame, text="Next Log Entry", command=next_qso_in_db)
nextButton.grid(row=5, column=5, padx=5, pady=5)
nextButton.config(width=10)

loadButton = Button(qsoFrame, text="Edit Log Entry", command=load_qso_from_db)
loadButton.grid(row=5, column=6, padx=5, pady=5)
loadButton.config(width=10)

deleteButton = Button(qsoFrame, text="Delete Log Entry", command=delete_qso_from_db)
deleteButton.grid(row=5, column=7, padx=5, pady=5)
deleteButton.config(width=12)


# Set the focus order when <Tab> is pressed
callsignEntry.bind("<Tab>", lambda e: lookup_call(e))
nameEntry.bind("<Tab>", lambda e: focus_next_widget(e, reportEntry))
reportEntry.bind("<Tab>", lambda e: focus_next_widget(e, remarksEntry))
remarksEntry.bind("<Tab>", lambda e: focus_next_widget(e, dateEntry))
dateEntry.bind("<Tab>", lambda e: focus_next_widget(e, timeEntry))
timeEntry.bind("<Tab>", lambda e: focus_next_widget(e, bandMenu))
bandMenu.bind("<Tab>", lambda e: focus_next_widget(e, freqEntry))
freqEntry.bind("<Tab>", lambda e: focus_next_widget(e, modeMenu))
modeMenu.bind("<Tab>", lambda e: focus_next_widget(e, propModeMenu))
propModeMenu.bind("<Tab>", lambda e: focus_next_widget(e, satelliteEntry))
satelliteEntry.bind("<Tab>", lambda e: focus_next_widget(e, gridEntry))
gridEntry.bind("<Tab>", lambda e: focus_next_widget(e, countyEntry))
countyEntry.bind("<Tab>", lambda e: focus_next_widget(e, stateEntry))
stateEntry.bind("<Tab>", lambda e: focus_next_widget(e, countryEntry))
countryEntry.bind("<Tab>", lambda e: focus_next_widget(e, cqEntry))
cqEntry.bind("<Tab>", lambda e: focus_next_widget(e, callsignEntry))
callsignEntry.focus_set()


# Configure the menu bar
app.config(menu=menubar)

# Load initial data
display_qso_number(ldb.get_last_rowid() + 1)

app.attributes('-topmost', True)
app.update()

# Check auto connect and auto upload settings
if config.getboolean('CAT', 'auto_con', fallback=False):
    cat_connect()
if config.getboolean('QRZ', 'upload', fallback=False):
    qrz_login()
if config.getboolean('LOTW', 'upload', fallback=False):
    lotw_login()

# Start periodic CAT updates
app.after(POLL_INTERVAL_MS, update_radio_settings)

# Keep the window open
app.mainloop()
