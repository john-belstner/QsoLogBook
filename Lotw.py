# lotw_sign_and_upload.py
import subprocess, pathlib
import configparser
import requests
import Crypto


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
        
    def tqsl_sign_and_upload(self, qso, duplicate_policy: str = "compliant") -> tuple[bool, str]:
        """
        Sign ADIF -> TQ8 with TQSL.
        duplicate_policy: one of 'ask','abort','compliant','all'
        Returns path to .tq8 file.
        """
        with open("qso.adi", "w") as f:
            f.write(qso)
        cmd = ["tqsl", "-d", "-u",
            "-a", duplicate_policy,
            "-l", self._location,
            "qso.adi"]
        if self._cert_password:
            cmd[1:1] = ["-p", self._cert_password]  # insert after 'tqsl'
        # TQSL writes status to stderr; success code 0 means “signed/saved or signed/uploaded”
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return True, result
        except Exception as e:
            return False, str(e)
