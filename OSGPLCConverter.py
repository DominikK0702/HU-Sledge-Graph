from PyQt5.QtCore import QThread, QObject, pyqtSignal
import requests
import subprocess
import time
from loguru import logger


class OSGWebTraceClient:
    user = 'SINAMICS'
    password = ''
    tmp_trace_file = './export/tmp.ACX.GZ'

    def __init__(self, ip):
        self.ip = ip
        self.session = requests.Session()
        self.cookies = {
            'siemens_automation_language': '0',
            'siemens_ad_session'         : '',
        }
        self.headers = {
            'Connection'     : 'keep-alive',
            'Accept'         : 'application/json, text/plain, */*',
            'User-Agent'     : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
            'Content-type'   : 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin'         : f'http://{self.ip}',
            'Referer'        : f'http://{self.ip}/login',
            'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'Pragma'         : 'no-cache',
            'Cache-Control'  : 'no-cache',
            'Accept-Encoding': 'gzip, deflate',
            'HOST'           : '169.254.11.22'
        }

        self.data = {
            'Login'      : OSGWebTraceClient.user,
            'Password'   : OSGWebTraceClient.password,
            'Redirection': '/index.mwsl'
        }

    def login(self):
        response = self.session.post(f'http://{self.ip}/FormLogin',
                                     headers=self.headers,
                                     cookies=self.cookies,
                                     data=self.data,
                                     verify=False)
        if response.status_code == 200:
            self.cookies['siemens_ad_session'] = response.headers.get('set-cookie').split(';')[0][19:]
            self.headers['Referer'] = f'http://{self.ip}/login'
            logger.info("Sinamics S120 Login success")
            return True
        else:
            logger.error("Sinamics S120 Login error")
            return False

    def logged_in_check(self):
        response = requests.get(f'http://{self.ip}/STATUSAPP?LOGGEDINUSER&_={int(time.time() * 1000)}',
                                headers=self.headers,
                                cookies=self.cookies)
        if response.status_code == 200:
            self.headers['Referer'] = f'http://{self.ip}/diagnostics/tracefiles'
            logger.info("Sinamics S120 login check success")
            return True
        else:
            logger.error("Sinamics S120 login check failed")
            return False

    def get_last_trace_name(self):
        response = requests.get(f'http://{self.ip}/PAGELOADER?page=tracefile', headers=self.headers,
                                cookies=self.cookies)
        if response.status_code == 200:
            ts = max([int(i[1]) for i in response.json()])
            tracefile = [i[0] for i in response.json() if int(i[1]) == ts].pop()
            self.headers['Insecure'] = '1'
            logger.info("Sinamics S120 get latest tracename success")
            return tracefile
        else:
            logger.error("Sinamics S120 get latest tracename failed")
            return False

    def get_last_tracefile(self, tracefile):
        response = requests.get(f'http://{self.ip}/DRVTRACEFILEAPP/{tracefile}', headers=self.headers,
                                cookies=self.cookies,
                                allow_redirects=True)
        if response.status_code == 200:
            with open(OSGWebTraceClient.tmp_trace_file, 'wb') as f:
                f.write(response.content)
            logger.info("Sinamics S120 get last tracefile success")
            return True
        else:
            logger.error("Sinamics S120 get last tracefile failed")
            return False

    @staticmethod
    def convert_last_trace_to_csv(csv_file):
        trace_file = OSGWebTraceClient.tmp_trace_file
        subprocess.call(
            ['./bin/Convert_SINAMICS_trace_CSV.exe', trace_file, '-sep', 'SEMICOLON', '-out',
             csv_file])


class ConverterEvents(QObject):
    language_changed = pyqtSignal()


class OSGSinamicsConverter(QThread):
    def __init__(self, parent=None):
        super(OSGSinamicsConverter, self).__init__()
        self.parent = parent
        self.trace_webclient = OSGWebTraceClient(self.parent.application.configmanager._config['CONVERTER'].get('ip'))
        self.delay = self.parent.application.configmanager._config['CONVERTER'].getint('refresh_delay_ms')
        self.running = True
        self.setConnectionStatus(False)
        self.events = ConverterEvents()
        # todo remove comment below
        self.start()

    def setConnectionStatus(self, state):
        self.parent.setConverterConnectionStatus(state)

    def connected(self):
        return False
        # todo logic
        while self.running:
            print(self.delay)
            self.msleep(self.delay)
