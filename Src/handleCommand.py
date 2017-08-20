
import subprocess

def handleCommandPrintAndExecute(commandString):
    print(commandString)
    subprocess.call(commandString, shell=True)


def handleCommandJustPrint(commandString):
    print(commandString)
