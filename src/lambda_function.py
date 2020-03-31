import csv
import re
import shutil
from pathlib import Path

import gspread
import jinja2
from oauth2client.service_account import ServiceAccountCredentials

ROOT_DIR = Path(__file__).parent
TEMPLATE_DIR = ROOT_DIR / "template"
CSS_DIR = TEMPLATE_DIR / "css"
SITE_DIR = ROOT_DIR / "site"
DATA_DIR = ROOT_DIR / "data"

LISTS_MAPPING = {
    "learning_resources": "&#128218; Learning Resources",
    "productivity": "&#128187; Productivity",
    "health": "&#x1F3CB; Health",
    "entertainment": "&#x1F4FA; Entertainment",
}

INTRO_TEXT = """
<b>COVID-19 is disrupting our lives.</b> Many are going through severe health situations. Others have lost their jobs. In several countries, people are quarantined in their homes, dealing with changes in their habits and daily routines.
<br><br>
Much of what is going on is not under our control, and we need to accept that. However, for the things that are under our control, like how we spend our time, <b>we are in a moment where the decisions we take now may have a huge impact on where we end-up in the future.</b>
<br><br>
<b>This page is a list of self-improvement resources available for free or at discounted prices due to the COVID-19.</b>
If you find them relevant, use them, or share them with others. If you know of something that is not here, <a href="https://docs.google.com/forms/d/e/1FAIpQLSf6qLcvJGWS3VltKV99sO0KhBxmWxb0sdIpVu93OolL42s7rQ/viewform?usp=sf_link">please let me know</a>.
"""


def download_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    workbook = client.open("Stay Home and Learn")

    try:
        shutil.rmtree(DATA_DIR)
    except:
        pass
    DATA_DIR.mkdir()

    for worksheet in workbook.worksheets():
        filename = DATA_DIR / (worksheet.title + ".csv")
        sheet_values = worksheet.get_all_values()
        print(f"Downloading: {worksheet.title}")
        with open(filename, "w") as f:
            writer = csv.writer(f)
            writer.writerows(sheet_values)


def generate_site():
    try:
        shutil.rmtree(SITE_DIR)
    except:
        pass
    SITE_DIR.mkdir()
    for filename in TEMPLATE_DIR.iterdir():
        if filename.is_dir():
            shutil.copytree(filename, SITE_DIR / filename.name)
        elif filename.name != "template.html":
            shutil.copy(filename, SITE_DIR)
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("template.html")

    csv_files = [
        filename for filename in DATA_DIR.iterdir() if filename.suffix == ".csv"
    ]
    csv_files.sort()
    lists_all = []
    for csv_file in csv_files:
        re_match = re.search(r"[0-9]_(.*?)\.csv", csv_file.name)
        proc_name = LISTS_MAPPING.get(re_match.group(1), re_match.group(1))
        with open(csv_file, mode="r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            list_ind = [row for row in csv_reader]
            lists_all.append((proc_name, list_ind))
    output = template.render(lists=lists_all, intro_text=INTRO_TEXT)

    with open(SITE_DIR / "index.html", "w") as f:
        f.write(output)


def build_site():
    download_sheets()
    generate_site()


if __name__ == "__main__":
    build_site()
