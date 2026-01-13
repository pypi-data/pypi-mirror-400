#!/usr/bin/env python3
import os
import sys

CONFIG_FILE = os.path.expanduser("~/.name")


def main():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            print(f.read().strip())
            return
    # first time
    while True:
        try:
            username = input("Whats ya name ").strip()
        except KeyboardInterrupt:
            print("\nProcess interrupted. Goodbye")
            sys.exit(0)
        if username:
            break

        print("username cannot be empty")

    with open(CONFIG_FILE, "w") as f:
        f.write(username)
    print("name saved!")


def clear():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        print("name cleared")
    else:
        print("no name to clear")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear()
    else:
        main()
