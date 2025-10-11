import requests
from Qso import Qso
import configparser
import Crypto
from urllib.parse import quote
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError


class QrzApi:

    def __init__(self, config: configparser.ConfigParser):
        self._session_key = ""
        self._username = config.get('QRZ', 'username', fallback="")
        self._password = Crypto.decrypt_text(config.get('QRZ', 'password', fallback=""))
        self._api_key = Crypto.decrypt_text(config.get('QRZ', 'api_key', fallback=""))
        self._log_url = "https://logbook.qrz.com/api"
        self._xml_url = "https://xmldata.qrz.com/xml"
        self._xmlns_url = "http://xmldata.qrz.com"
        self._agent = "QsoLogBook/1.0"

    def reload_config(self, config: configparser.ConfigParser):
        self._username = config.get('QRZ', 'username', fallback="")
        self._password = Crypto.decrypt_text(config.get('QRZ', 'password', fallback=""))
        self._api_key = Crypto.decrypt_text(config.get('QRZ', 'api_key', fallback=""))
        self._session_key = ""  # Clear session key on config reload
        self._agent = "QsoLogBook/1.0"
        
    def _to_int(self, x):
        try: return int(x) if x is not None and x != "" else None
        except ValueError: return None

    def _to_float(self, x):
        try: return float(x) if x is not None and x != "" else None
        except ValueError: return None

    def _to_bool_yn(self, x):
        if x is None: return None
        x = x.strip().upper()
        return True if x in ("Y", "1", "T", "TRUE") else False if x in ("N", "0", "F", "FALSE") else None

    def _get(self, elem, tag, ns):
        node = elem.find(f"qrz:{tag}", ns)
        return node.text.strip() if node is not None and node.text is not None else None

    def parse_qrz_xml(self, xml_str: str):
        # Handle cases where the incoming string is quoted and has \n escapes
        xml_str = xml_str.strip()
        if (xml_str.startswith("'") and xml_str.endswith("'")) or (xml_str.startswith('"') and xml_str.endswith('"')):
            xml_str = xml_str[1:-1]
        # Parse
        root = ET.fromstring(xml_str)
        ns = {"qrz": self._xmlns_url}

        callsign_el = root.find("qrz:Callsign", ns)
        session_el  = root.find("qrz:Session", ns)

        callsign = {}
        if callsign_el is not None:
            callsign = {
                "call":      self._get(callsign_el, "call", ns),
                "dxcc":      self._to_int(self._get(callsign_el, "dxcc", ns)),
                "fname":     self._get(callsign_el, "fname", ns),
                "name":      self._get(callsign_el, "name", ns),
                "addr1":     self._get(callsign_el, "addr1", ns),
                "addr2":     self._get(callsign_el, "addr2", ns),
                "state":     self._get(callsign_el, "state", ns),
                "zip":       self._get(callsign_el, "zip", ns),
                "country":   self._get(callsign_el, "country", ns),
                "lat":       self._to_float(self._get(callsign_el, "lat", ns)),
                "lon":       self._to_float(self._get(callsign_el, "lon", ns)),
                "grid":      self._get(callsign_el, "grid", ns),
                "county":    self._get(callsign_el, "county", ns),
                "ccode":     self._get(callsign_el, "ccode", ns),
                "fips":      self._get(callsign_el, "fips", ns),
                "land":      self._get(callsign_el, "land", ns),
                "efdate":    self._get(callsign_el, "efdate", ns),   # 'YYYY-MM-DD'
                "expdate":   self._get(callsign_el, "expdate", ns),  # 'YYYY-MM-DD'
                "class":     self._get(callsign_el, "class", ns),
                "codes":     self._get(callsign_el, "codes", ns),
                "qslmgr":    self._get(callsign_el, "qslmgr", ns),
                "email":     self._get(callsign_el, "email", ns),
                "u_views":   self._to_int(self._get(callsign_el, "u_views", ns)),
                "bio_url":   self._get(callsign_el, "bio", ns),
                "image_url": self._get(callsign_el, "image", ns),
                "moddate":   self._get(callsign_el, "moddate", ns),  # 'YYYY-MM-DD HH:MM:SS'
                "MSA":       self._get(callsign_el, "MSA", ns),
                "AreaCode":  self._get(callsign_el, "AreaCode", ns),
                "TimeZone":  self._get(callsign_el, "TimeZone", ns),
                "GMTOffset": self._to_int(self._get(callsign_el, "GMTOffset", ns)),
                "DST":       self._to_bool_yn(self._get(callsign_el, "DST", ns)),
                "eqsl":      self._to_int(self._get(callsign_el, "eqsl", ns)),
                "mqsl":      self._to_int(self._get(callsign_el, "mqsl", ns)),
                "cqzone":    self._to_int(self._get(callsign_el, "cqzone", ns)),
                "locref":    self._to_int(self._get(callsign_el, "locref", ns)),
                "born":      self._to_int(self._get(callsign_el, "born", ns)),
                "lotw":      self._to_int(self._get(callsign_el, "lotw", ns)),
                "user":      self._get(callsign_el, "user", ns),
            }

        session = {}
        if session_el is not None:
            session = {
                "Key":     self._get(session_el, "Key", ns),
                "Count":   self._to_int(self._get(session_el, "Count", ns)),
                "SubExp":  self._get(session_el, "SubExp", ns),   # free-form time string from QRZ
                "GMTime":  self._get(session_el, "GMTime", ns),   # free-form time string
                "Remark":  self._get(session_el, "Remark", ns),
            }

        return {"Callsign": callsign, "Session": session}

    def login(self, timeout=10) -> bool:
        if not self._username or not self._password:
            raise ValueError("Missing QRZ credentials")
        url = (f"{self._xml_url}?username={self._username};"
               f"password={self._password};agent={self._agent}")
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            data = self.parse_qrz_xml(r.text)
            key = data.get("Session", {}).get("Key")
            if not key:
                err = data.get("Session", {}).get("Error", "No session key in response")
                raise RuntimeError(f"QRZ login failed: {err}")
            self._session_key = key
            return True
        except ParseError as pe:
            # Show a snippet to help debug server-side content
            preview = r.text[:400] if "r" in locals() else ""
            raise RuntimeError(f"QRZ login XML parse failed: {pe}\nPreview: {preview}")

    def lookup(self, callsign: str, timeout=10):
        # We need the session key to continue
        if not self._session_key:
            raise RuntimeError("Not logged in")
        url = f"{self._xml_url}?s={self._session_key};callsign={callsign}"
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return self.parse_qrz_xml(r.text)

    def upload_qso(self, qso: Qso, timeout=10):
        if not self._session_key:
            raise RuntimeError("Not logged in")
        if not self._api_key:
            raise ValueError("Missing QRZ API key")
        if not qso.is_valid():
            raise ValueError("Invalid QSO data")
        # Query parameters
        action = "insert"
        adif = qso.to_adif()
        #print("ADIF:", adif)
        # URL-encode ADIF
        adif_encoded = quote(adif, safe="")
        #print("Encoded ADIF:", adif_encoded)
        # Full URL
        url = self._log_url + "?key=" + self._api_key + "&action=" + action + "&adif=" + adif_encoded
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            # Parse response
            result = count = logid = reason = None
            qrz_resp = response.text.split("&")
            #print("QRZ Response:", qrz_resp)
            for item in qrz_resp:
                if item.lower().startswith("result="):
                    result = item[len("result="):].strip("\n")
                elif item.lower().startswith("count="):
                    count = self._to_int(item[len("count="):])
                elif item.lower().startswith("logid="):
                    logid = self._to_int(item[len("logid="):])
                elif item.lower().startswith("reason="):
                    reason = item[len("reason="):].strip("\n") 
        except requests.RequestException as e:
            raise RuntimeError(f"QSO upload failed: {e}")
        return result, count, logid, reason
        