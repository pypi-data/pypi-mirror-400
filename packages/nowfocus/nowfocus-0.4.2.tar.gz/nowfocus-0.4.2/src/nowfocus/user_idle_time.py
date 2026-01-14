import os
import platform
import subprocess

class UserIdleTime():
    def __init__(self, platform = None, **kwargs):

        self.getters = {
            'linux_wayland': self.get_idle_seconds_linux_wayland,
            'linux_x': self.get_idle_seconds_linux_x,
            'mac': self.get_idle_seconds_mac,
            'windows': self.get_idle_seconds_windows,
        }

        if platform:
            self.platform = platform
        else:
            self.detect_platform()

        print('UserIdleTime platform set to',self.platform)

    def get (self) :
        ''' Returns int of seconds since user was active '''
        try:
            return int(self.getters[self.platform]())
        except Exception as e:
            print(' CheckIdleTime failed')
            print(e)
            return 0
    


    def detect_platform (self):

        match (platform.system()):
            case ('Linux'):
                if os.environ.get('XDG_SESSION_TYPE') == "wayland":
                    self.platform = "linux_wayland"
                else:
                    self.platform = "linux_x"

            case ("Darwin"):
                self.platform = "mac"

            case ("Windows"):
                self.platform = "windows"
 
        return self.platform


    def get_idle_seconds_linux_wayland (self):
        # https://askubuntu.com/a/1231995/292055

        command = "dbus-send --print-reply --dest=org.gnome.Mutter.IdleMonitor /org/gnome/Mutter/IdleMonitor/Core org.gnome.Mutter.IdleMonitor.GetIdletime"

        response = subprocess.getoutput(command)

        idle_time = int(int(response.rsplit(None,1)[-1]) / 1000)

        return idle_time


    def get_idle_seconds_linux_x (self):
        idle_time = int(subprocess.getoutput('xprintidle')) / 1000 # Requires xprintidle (sudo apt install xprintidle)
        return idle_time


    def get_idle_seconds_windows (self):
        # https://stackoverflow.com/a/67091943/4692205
        import win32api

        idle_time = (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0

        return idle_time


    def get_idle_seconds_mac (self):
        # https://stackoverflow.com/a/17966890/4692205
        command = "ioreg -c IOHIDSystem | awk '/HIDIdleTime/ {print $NF/1000000000; exit}'"

        idle_time = int(float(subprocess.getoutput(command)))
        return idle_time