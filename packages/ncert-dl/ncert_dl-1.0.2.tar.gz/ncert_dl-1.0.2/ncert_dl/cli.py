#!/usr/bin/env python3
import os
import sys
import time
import argparse
from pathlib import Path
import requests
from tqdm import tqdm
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live

# Initialize Rich Console
console = Console()

import json
import importlib.resources

# ================= CONFIG =================
BASE_URL = "https://ncert.nic.in/textbook/pdf/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def load_syllabus():
    """Lengths the syllabus from the JSON file packaged with the tool."""
    try:
        # For Python 3.9+
        ref = importlib.resources.files('ncert_dl') / 'syllabus.json'
        with ref.open('r') as f:
            return json.load(f)
    except Exception:
         # Fallback or older python support if needed, but 3.9+ is in pyproject
        with open(Path(__file__).parent / "syllabus.json", "r") as f:
            return json.load(f)

SYLLABUS = load_syllabus()

class NCERTDownloader:
    def __init__(self, output_dir=None):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        if output_dir is None:
            self.output_dir = Path.home() / "NCERT_Downloads"
        else:
            self.output_dir = Path(output_dir)

    def print_banner(self):
        console.print(Panel.fit(
            "[bold cyan]NCERT-DL: Universal Textbook Downloader[/bold cyan]\n"
            "[white]An automated tool for students and educators[/white]",
            border_style="blue"
        ))

        if lang_code == "h":
             # 2nd character (index 1) indicates medium. 'e' -> 'h'
             # Example: jemh1 -> jhmh1
            actual_prefix = prefix[:1] + lang_code + prefix[2:]
        else:
            actual_prefix = prefix
        
        # Format chapter number: 1 -> 01
        ch_str = str(ch_num).zfill(2)
        
        return f"{actual_prefix}{ch_str}.pdf"

    def download_chapter(self, url, dest_path):
        if dest_path.exists():
            return "exists"

        try:
            response = self.session.get(url, stream=True, timeout=20)
            if response.status_code != 200:
                return "missing"

            total_size = int(response.headers.get('content-length', 0))
            
            with open(dest_path, 'wb') as f, tqdm(
                desc=f"  └─ {dest_path.name}",
                total=total_size,
                unit='iB',
                unit_scale=True,
                leave=False,
                bar_format="{l_bar}{bar:20}{r_bar}"
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    f.write(data)
                    bar.update(len(data))
            return "success"
        except Exception:
            return "error"

    def run(self):
        self.print_banner()

        # 1. Select Class
        cls = questionary.select(
            "Select Class:",
            choices=list(SYLLABUS.keys()) + ["Exit"]
        ).ask()

        if cls == "Exit" or not cls:
            sys.exit(0)

        # 2. Prepare Subject Choices (including books)
        # Format: "Subject - Book Name" or just "Subject" if same
        choices_map = {}
        display_choices = []
        
        for subject, books in SYLLABUS[cls].items():
            for book in books:
                # If the book name is very similar to subject (e.g. Mathematics), just show Subject
                # Otherwise show "Subject - Book Name"
                if book['name'].lower() == subject.lower():
                    display_name = subject
                else:
                    display_name = f"{subject} - {book['name']}"
                
                display_choices.append(display_name)
                choices_map[display_name] = {
                    "subject": subject,
                    "book_data": book
                }

        # 3. Select Books
        selected_displays = questionary.checkbox(
            "Select Books:",
            choices=display_choices
        ).ask()

        if not selected_displays:
            console.print("[yellow]No books selected. Goodbye![/yellow]")
            return

        # 4. Select Language
        lang = questionary.select(
            "Select Language:",
            choices=[
                questionary.Choice("English", value="e"),
                questionary.Choice("Hindi", value="h")
            ]
        ).ask()

        # 5. Execution
        table = Table(title=f"Download Queue: Class {cls}", show_header=True, header_style="bold magenta")
        table.add_column("Book", style="dim")
        table.add_column("Status")

        for item in selected_displays:
            table.add_row(item, "[pending]Waiting...[/pending]")

        console.print(table)

        for display_name in selected_displays:
            selection = choices_map[display_name]
            subject = selection['subject']
            book = selection['book_data']
            
            # Create path: Class > Subject > BookName (if needed)
            # If subject has only one book named same as subject, clean path
            # But here we stick to: Class > Subject > BookName to be safe/organized
            # exception: Maths/Science usually just have one book.
            
            base_folder = self.output_dir / f"Class_{cls}" / subject.replace(" ", "_")
            if book['name'].lower() != subject.lower():
                 base_folder = base_folder / book['name'].replace(" ", "_")
            
            base_folder.mkdir(parents=True, exist_ok=True)
            
            console.print(f"\n[bold green]➜ Downloading {display_name}[/bold green]")
            
            for ch in range(1, book["chapters"] + 1):
                fname = self.get_filename(book["prefix"], ch, lang)
                url = f"{BASE_URL}{fname}"
                dest = base_folder / f"Chapter_{ch}.pdf"
                
                result = self.download_chapter(url, dest)
                
                if result == "missing":
                    console.print(f"  [red]✖[/red] Chapter {ch} not found ({fname}).")
                elif result == "error":
                    console.print(f"  [red]✖[/red] Error downloading Chapter {ch}.")

        console.print("\n[bold cyan]✨ All Tasks Completed![/bold cyan]")
        console.print(f"Files saved to: [underline]{self.output_dir.absolute()}[/underline]")

def main():
    downloader = NCERTDownloader()
    try:
        downloader.run()
    except KeyboardInterrupt:
        console.print("\n[red]Stopping...[/red]")
        sys.exit(0)

if __name__ == "__main__":
    main()