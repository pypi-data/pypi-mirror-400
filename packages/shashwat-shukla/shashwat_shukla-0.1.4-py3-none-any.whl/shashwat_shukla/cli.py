import argparse
import webbrowser
import importlib.resources as res
import importlib.metadata
import subprocess
import sys
import os
import datetime
import qrcode

PKG_NAME = "shashwat-shukla"

# ---------- helpers ----------

def get_package_info():
    version = importlib.metadata.version(PKG_NAME)
    dist = importlib.metadata.distribution(PKG_NAME)
    install_time = datetime.datetime.fromtimestamp(
        os.path.getctime(dist._path)
    )
    return version, install_time

def open_resume():
    with res.files("shashwat_shukla").joinpath("Shashwat_CV.pdf") as pdf:
        path = str(pdf)
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])

def open_projects():
    webbrowser.open("https://github.com/shukla-shashwat")

def open_linkedin():
    webbrowser.open("https://www.linkedin.com/in/shashwat--shukla")

def upgrade_package():
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", PKG_NAME],
        check=False
    )

def show_resume_qr():
    try:
        qr = qrcode.QRCode(border=1)
        qr.add_data("https://drive.google.com/file/d/1gQJWSH30ZQ8ypwNN9KUsLyDe1Rmg2nrs/view?usp=drive_link")  # or direct PDF link
        qr.make()

        print("\nScan to view resume:\n")
        qr.print_ascii()
    except Exception as e:
        print("\n[QR generation failed]")


# ---------- main ----------

def main():
    def print_ascii_banner():
        banner = r"""
/* +--------------------------------------------------------------------------------------------+ */
/* |      /$$$$$$  /$$                           /$$                                 /$$        | */
/* |     /$$__  $$| $$                          | $$                                | $$        | */
/* |    | $$  \__/| $$$$$$$   /$$$$$$   /$$$$$$$| $$$$$$$  /$$  /$$  /$$  /$$$$$$  /$$$$$$      | */
/* |    |  $$$$$$ | $$__  $$ |____  $$ /$$_____/| $$__  $$| $$ | $$ | $$ |____  $$|_  $$_/      | */
/* |     \____  $$| $$  \ $$  /$$$$$$$|  $$$$$$ | $$  \ $$| $$ | $$ | $$  /$$$$$$$  | $$        | */
/* |     /$$  \ $$| $$  | $$ /$$__  $$ \____  $$| $$  | $$| $$ | $$ | $$ /$$__  $$  | $$ /$$    | */
/* |    |  $$$$$$/| $$  | $$|  $$$$$$$ /$$$$$$$/| $$  | $$|  $$$$$/$$$$/|  $$$$$$$  |  $$$$/    | */
/* |     \______/ |__/  |__/ \_______/|_______/ |__/  |__/ \_____/\___/  \_______/   \___/      | */
/* |                                                                                            | */
/* |                                                                                            | */
/* |                                                                                            | */
/* |      /$$$$$$  /$$                 /$$       /$$                                            | */
/* |     /$$__  $$| $$                | $$      | $$                                            | */
/* |    | $$  \__/| $$$$$$$  /$$   /$$| $$   /$$| $$  /$$$$$$                                   | */
/* |    |  $$$$$$ | $$__  $$| $$  | $$| $$  /$$/| $$ |____  $$                                  | */
/* |     \____  $$| $$  \ $$| $$  | $$| $$$$$$/ | $$  /$$$$$$$                                  | */
/* |     /$$  \ $$| $$  | $$| $$  | $$| $$_  $$ | $$ /$$__  $$                                  | */
/* |    |  $$$$$$/| $$  | $$|  $$$$$$/| $$ \  $$| $$|  $$$$$$$                                  | */
/* |     \______/ |__/  |__/ \______/ |__/  \__/|__/ \_______/                                  | */    
/* |                                                                                          | */
/* +--------------------------------------------------------------------------------------------+ */
"""
        print(banner)


    parser = argparse.ArgumentParser(
        prog=PKG_NAME,
        description="Personal developer CLI by Shashwat Shukla"
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show installed version"
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("resume", help="Open resume PDF")
    sub.add_parser("projects", help="Open GitHub projects")
    sub.add_parser("linkedin", help="Open LinkedIn profile")
    sub.add_parser("upgrade", help="Upgrade this package")

    args = parser.parse_args()

    # Default behavior
    if not args.command and not args.version:
        print_ascii_banner()
        version, installed_on = get_package_info()
        print("Shashwat Shukla CLI")
        print(f"Version     : {version}")
        print(f"Installed on: {installed_on.strftime('%Y-%m-%d %H:%M')}")
        print("\nTry:")
        print("  shashwat-shukla resume")
        print("  shashwat-shukla projects")
        print("  shashwat-shukla linkedin")
        print("  shashwat-shukla upgrade")
        return
    if args.version:
        print(importlib.metadata.version(PKG_NAME))
    elif args.command == "resume":
        # open_resume()
        show_resume_qr()
        ans = input("Open resume? (y/n): ").lower()
        if ans == "y":
            open_resume()
    elif args.command == "projects":
        open_projects()
    elif args.command == "linkedin":
        open_linkedin()
    elif args.command == "upgrade":
        upgrade_package()
    else:
        parser.print_help()

# future planning of portfolio link