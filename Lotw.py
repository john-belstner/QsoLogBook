# lotw_sign_and_upload.py
import subprocess, re, pathlib
import configparser
import requests
import Crypto

LOTW_UPLOAD_URL = "https://lotw.arrl.org/lotw/upload"

UPL_RE   = re.compile(r"<!--\s*\.UPL\.\s*(accepted|rejected)\s*-->", re.I)
UPLM_RE  = re.compile(r"<!--\s*\.UPLMESSAGE\.\s*(.*?)\s*-->", re.S | re.I)

class TQSLException(RuntimeError): pass
class LoTWUploadError(RuntimeError): pass

class Lotw:

    def __init__(self, config: configparser.ConfigParser):
        self._username = config.get('LOTW', 'username', fallback="")
        self._password = Crypto.decrypt_text(config.get('LOTW', 'password', fallback=""))
        self._location = config.get('LOTW', 'location', fallback="")
        self._certificate = config.get('LOTW', 'certificate', fallback="")
        self._cert_password = Crypto.decrypt_text(config.get('LOTW', 'cert_password', fallback=""))
        self._agent = "QsoLogBook/1.0"

    def reload_config(self, config: configparser.ConfigParser):
        self._username = config.get('LOTW', 'username', fallback="")
        self._password = Crypto.decrypt_text(config.get('LOTW', 'password', fallback=""))
        self._location = config.get('LOTW', 'location', fallback="")
        self._certificate = config.get('LOTW', 'certificate', fallback="")
        self._cert_password = Crypto.decrypt_text(config.get('LOTW', 'cert_password', fallback=""))
        self._agent = "QsoLogBook/1.0"
        
    def tqsl_import_p12(self, p12_path: str, password: str | None = None) -> None:
        """Import a .p12 Callsign Certificate into TQSL's keystore (run once)."""
        cmd = ["tqsl", "-q", "-i", p12_path]
        if password:
            cmd += ["-p", password]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise TQSLException(f"TQSL import failed (rc={res.returncode}): {res.stderr.strip()}")

    def tqsl_sign(self, adif_path: str, station_location: str,
                out_tq8: str | None = None,
                cert_password: str | None = None,
                duplicate_policy: str = "compliant") -> pathlib.Path:
        """
        Sign ADIF -> TQ8 with TQSL.
        duplicate_policy: one of 'ask','abort','compliant','all'
        Returns path to .tq8 file.
        """
        adif = pathlib.Path(adif_path)
        if not out_tq8:
            out_tq8 = str(adif.with_suffix(".tq8"))
        cmd = ["tqsl", "-q", "-d",
            "-a", duplicate_policy,
            "-l", station_location,
            "-o", out_tq8,
            adif_path]
        if cert_password:
            cmd[1:1] = ["-p", cert_password]  # insert after 'tqsl'
        # TQSL writes status to stderr; success code 0 means “signed/saved or signed/uploaded”
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise TQSLException(f"TQSL signing failed (rc={res.returncode}): {res.stderr.strip()}")
        return pathlib.Path(out_tq8)

    def lotw_upload_tq8(self, tq8_path: str) -> tuple[bool, str]:
        """
        Upload a .tq8 (or .tq5) to LoTW via RFC1867 (multipart/form-data).
        Parses <!-- .UPL. accepted|rejected --> and <!-- .UPLMESSAGE. ... -->.
        """
        with open(tq8_path, "rb") as f:
            # LoTW’s developer page states the endpoint accepts an RFC1867 multipart upload
            # and returns the two HTML comments we parse below.
            files = {"file": (pathlib.Path(tq8_path).name, f, "application/octet-stream")}
            r = requests.post(LOTW_UPLOAD_URL, files=files, timeout=60)
        text = r.text
        m_result = UPL_RE.search(text)
        m_msg    = UPLM_RE.search(text)
        if not m_result:
            raise LoTWUploadError(f"Unexpected response from LoTW (no .UPL. marker). HTTP {r.status_code}")
        accepted = m_result.group(1).lower() == "accepted"
        message  = (m_msg.group(1).strip() if m_msg else "").strip()
        return accepted, message

    def lotw_sign_and_upload(self, adif_path: str, station_location: str,
                            cert_password: str | None = None,
                            duplicate_policy: str = "compliant") -> tuple[bool, str]:
        """
        Sign ADIF with TQSL and upload to LoTW.
        Returns (accepted: bool, message: str).
        """
        tq8_path = self.tqsl_sign(adif_path, station_location,
                            cert_password=cert_password,
                            duplicate_policy=duplicate_policy)
        return self.lotw_upload_tq8(tq8_path)
