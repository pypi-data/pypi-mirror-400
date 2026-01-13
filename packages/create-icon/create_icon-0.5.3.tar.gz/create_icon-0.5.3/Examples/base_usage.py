# __main__.py
# Last Modified: 2026-01-06 15:xx:xx

import os
from tkinter import Tk


def main():
    root = Tk()
    root.minsize(300, 100)
    root.title("<--<< The Icon")

    # Add icon to Windows title bar using LOCALAPPDATA
    if os.name == "nt":
        local_appdata = os.environ.get("LOCALAPPDATA")

        if local_appdata:
            icon_path = os.path.join(
                local_appdata,
                "Caveman Software",
                "Icon",
                "icon.ico",
            )

            if os.path.exists(icon_path):
                root.wm_iconbitmap(default=icon_path)

    root.mainloop()


if __name__ == "__main__":
    main()
