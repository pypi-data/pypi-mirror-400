from importlib.metadata import version
import sys

def main():
    if "-v" in sys.argv or "--version" in sys.argv:
        print(version("iewil"))
        return

    print("IEWIL CLI")
    print("Gunakan: iewil -v")
