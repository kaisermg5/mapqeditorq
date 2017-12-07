
import subprocess
import time


class SubprocessReader:
    def __init__(self, cmd):
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def get_next_line(self):
        while True:
            line = self.process.stdout.readline().decode(errors='ignore')
            if line != '' or self.process.poll() is not None:
                break
            else:
                time.sleep(0.5)
        return line

    def __iter__(self):
        return self

    def __next__(self):
        line = self.get_next_line()
        if line == '':
            raise StopIteration
        return line

