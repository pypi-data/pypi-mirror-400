import subprocess
import sys
import os

class LibraryManager:
    def install_library(self, library_name):
        print(f"[INFO] Installing {library_name}...")
        subprocess.run([sys.executable, "-m", "pip", "install", library_name])

    def uninstall_library(self, library_name):
        print(f"[INFO] Uninstalling {library_name}...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", library_name, "-y"])

    def select_active_library(self):
        print("Select which testing library to use:")
        print("1. fastapptest")
        print("2. flaskapptest")
        choice = input("Enter number: ").strip()
        if choice == "1":
            self.set_active("fastapptest")
        elif choice == "2":
            self.set_active("flaskapptest")
        else:
            print("[ERROR] Invalid choice!")

    def set_active(self, library_name):
        # Store active library in a file inside user's home folder for persistence
        home_dir = os.path.expanduser("~")
        config_file = os.path.join(home_dir, ".pyapptest_active_library")
        with open(config_file, "w") as f:
            f.write(library_name)
        print(f"[INFO] Active testing library set to {library_name}")
        print(f"[TIP] This selection is persistent. Use `python -m pyapptest options` anytime to change it.")
