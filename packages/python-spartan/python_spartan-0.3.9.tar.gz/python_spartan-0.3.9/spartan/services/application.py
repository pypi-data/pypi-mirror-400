import io
import os
import shutil
import zipfile

import requests
from rich import print


class ApplicationService:
    def __init__(self, project_name: str, provider: str = "gcp"):
        self.project_name = project_name
        self.provider = provider.lower()

        branch = "main"

        if self.provider == "gcp":
            self.release_url = f"https://github.com/nerdmonkey/spartan-lazaro/archive/refs/heads/{branch}.zip"
        else:
            self.release_url = f"https://github.com/nerdmonkey/spartan-bogart/archive/refs/heads/{branch}.zip"

    def is_valid_folder_name(self):
        return (
            all(c.isidentifier() or c == "-" for c in self.project_name)
            and not self.project_name[0].isdigit()
        )

    def download_zip(self):
        release_url = self.release_url

        try:
            response = requests.get(release_url, timeout=30)  # nosec B113
            response.raise_for_status()
            return io.BytesIO(response.content)
        except requests.exceptions.RequestException as err:
            print(f"Request error: {err}")
            return None

    def extract_zip(self, zip_data):
        temp_folder = "temp_extracted_folder"
        try:
            with zipfile.ZipFile(zip_data, "r") as zip_ref:
                zip_ref.extractall(temp_folder)
            return temp_folder
        except zipfile.BadZipFile:
            print("Error: The downloaded file is not a valid ZIP file.")
            return None

    def setup_project(self, temp_folder):
        extracted_files = os.listdir(temp_folder)
        if len(extracted_files) == 1 and os.path.isdir(
            os.path.join(temp_folder, extracted_files[0])
        ):
            extracted_folder = os.path.join(temp_folder, extracted_files[0])
            os.rename(extracted_folder, self.project_name)
            shutil.rmtree(temp_folder)
            return True
        return False

    def create_app(self):
        if os.path.exists(self.project_name):
            print(f"The {self.project_name} folder already exists. Aborting.")
            return
        if not self.is_valid_folder_name():
            print(f"{self.project_name} is not a valid project name. Aborting.")
            return

        zip_data = self.download_zip()
        if zip_data:
            temp_folder = self.extract_zip(zip_data)
            if temp_folder and self.setup_project(temp_folder):
                self.print_ascii_art()
                self.print_message()
                self.print_success_message()
                self.print_first_mission()
            else:
                print("Error: The ZIP file should contain a single top-level folder.")

    def print_ascii_art(self):
        ascii_art = [
            ".d8888. d8888b.  .d8b.  d8888b. d888888b  .d8b.  d8b   db",
            "88'  YP 88  `8D d8' `8b 88  `8D `~~88~~' d8' `8b 888o  88",
            "`8bo.   88oodD' 88ooo88 88oobY'    88    88ooo88 88V8o 88",
            "  `Y8b. 88~~~   88~~~88 88`8b      88    88~~~88 88 V8o88",
            "db   8D 88      88   88 88 `88.    88    88   88 88  V888",
            "`8888Y' 88      YP   YP 88   YD    YP    YP   YP VP   V8P",
        ]

        print("\n")
        for line in ascii_art:
            print(line)

    def print_message(self):
        message = [
            "Embark on your cloud software journey with Spartan determination and simplicity.",
            "Build your digital empire with unwavering focus and minimalism,",
            "just like the warriors of ancient Sparta.",
        ]

        print("\n")
        for line in message:
            print(line)

    def print_success_message(self):
        print(f"\nSuccessfully setup the project to '{self.project_name}' folder.")

    def print_first_mission(self):
        # Automate copying .env.example to .env if possible
        env_example = os.path.join(self.project_name, ".env.example")
        env_file = os.path.join(self.project_name, ".env")
        print("\n")
        try:
            if os.path.exists(env_example) and not os.path.exists(env_file):
                shutil.copy(env_example, env_file)
                print("[green].env.example copied to .env[/]")
            elif os.path.exists(env_file):
                print("[yellow].env already exists, skipping copy[/]")
            else:
                print("[red].env.example not found, skipping copy[/]")
        except Exception as e:
            print(f"[red]Failed to copy .env.example to .env: {e}[/]")

        print("\n[bold blue]Spartan this is your first mission:[/]")
        print("[yellow]---------------[/]")
        print(f"[green]cd {self.project_name}[/]")
        print("[green]python -m venv .venv[/]")
        print("[green]source .venv/bin/activate # linux or macOS[/]")
        print("[magenta]or[/]")
        print("[green].venv\\Scripts\\activate # Windows (cmd)[/]")
        print("[magenta]or[/]")
        print("[green]source .venv/Scripts/activate # Git Bash/Powershell[/]")
        print("\n")
        print("[bold blue]To install the dependencies, run:[/]")
        print("[yellow]---------------[/]")
        print("[green]pip install -r requirements-dev.txt[/]")

        print("\n[bold blue]To run the application, run:[/]")
        print("[yellow]---------------[/]")

        if self.provider == "gcp":
            print("[green]python main.py[/]")
        else:
            print(
                "[green]python -m handlers.<handler_file> # eq. python -m handlers.inference[/]"
            )
        print("\n")
