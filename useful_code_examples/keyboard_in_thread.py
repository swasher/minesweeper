import threading
import time
import sys


class MyThread(threading.Thread):
    def __init__(self, threadID, name, counter, f):
        super().__init__()
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.func = f

    def run(self):
        self.func()

class KeyboardMonitor:
    def __init__(self):
        # Setting a boolean flag is atomic in Python.
        # It's hard to imagine a boolean being
        # anything else, with or without the GIL.
        # If inter-thread communication is anything more complicated than
        # a couple of flags, you should replace low level variables with
        # a thread safe buffer.
        self.keepGoing = True

    def wait4KeyEntry(self):
        while self.keepGoing:
            s = input("Type q to quit: ")
            if s == "q":
                self.keepGoing = False

    def mainThread(self, f, *args, **kwargs):
        """Pass in some main function you want to run, and this will run it
        until keepGoing = False. The first argument of function f must be
        this class, so that that function can check the keepGoing flag and
        quit when keepGoing is false."""
        keyboardThread = MyThread(1, "keyboard_thread", 0, self.wait4KeyEntry)
        keyboardThread.start()
        while self.keepGoing:
            f(self, *args, **kwargs)

def main(keyMonitorInst, *args, **kwargs):
    while keyMonitorInst.keepGoing:
        print("Running again...")
        time.sleep(1)

if __name__ == "__main__":
    uut = KeyboardMonitor()
    uut.mainThread(main)