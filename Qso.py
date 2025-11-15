
class Qso:
    def __init__(self, qso_id, callsign="", name="", date="", time="", band="", mode="", report="", prop_mode="", satellite="", grid="", county="", state="", country="", cq="", freq="", remarks="", my_grid=""):
        self.qso_id = qso_id
        self.callsign = callsign
        self.name = name
        self.date = date
        self.time = time
        self.band = band
        self.mode = mode
        self.report = report
        self.prop_mode = prop_mode
        self.satellite = satellite
        self.grid = grid
        self.county = county
        self.state = state
        self.country = country
        self.cq = cq
        self.freq = freq
        self.remarks = remarks
        self.my_grid = my_grid

    def __str__(self):
        return f"QSO(ID={self.qso_id}, Call={self.callsign}, Date={self.date}, Time={self.time}, Band={self.band}, Mode={self.mode}), Report={self.report})"
    
    def is_valid(self):
        if self.qso_id == "" or not self.qso_id.isdigit() or self.callsign == "" or self.date == "" or self.time == "" or self.band == "" or self.mode == "":
            return False
        return True

    def to_adif(self):
        adif_str = f"<call:{len(self.callsign)}>{self.callsign} "
        if self.name:
            adif_str += f"<name:{len(self.name)}>{self.name} "
        if self.date:
            adif_date = self.date.replace("-", "")
            adif_str += f"<qso_date:{len(adif_date)}>{adif_date} "
        if self.time:
            adif_str += f"<time_on:{len(self.time)}>{self.time} "
        if self.band:
            adif_str += f"<band:{len(self.band)}>{self.band} "
        if self.mode:
            adif_str += f"<mode:{len(self.mode)}>{self.mode} "
        if self.report:
            adif_str += f"<rst_rcvd:{len(self.report)}>{self.report} "
        if self.prop_mode != "N/A":
            adif_str += f"<prop_mode:{len(self.prop_mode)}>{self.prop_mode} "
        if self.satellite != "None":
            adif_str += f"<sat_name:{len(self.satellite)}>{self.satellite} "
        if self.grid:
            adif_str += f"<gridsquare:{len(self.grid)}>{self.grid} "
        if self.county:
            adif_str += f"<county:{len(self.county)}>{self.county} "
        if self.state:
            adif_str += f"<state:{len(self.state)}>{self.state} "
        if self.country:
            adif_str += f"<country:{len(self.country)}>{self.country} "
        if self.cq:
            adif_str += f"<cqz:{len(self.cq)}>{self.cq} "
        if self.freq:
            adif_str += f"<freq:{len(self.freq)}>{self.freq} "
        if self.remarks:
            adif_str += f"<remarks:{len(self.remarks)}>{self.remarks} "
        if self.my_grid:
            adif_str += f"<my_gridsquare:{len(self.my_grid)}>{self.my_grid} "
        adif_str += "<eor>\n"
        return adif_str
