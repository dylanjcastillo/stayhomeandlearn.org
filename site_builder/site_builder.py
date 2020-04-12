import configparser
import csv
import re
import shutil
import time
import webbrowser
from datetime import datetime

import boto3
import gspread
import jinja2
from oauth2client.service_account import ServiceAccountCredentials

from site_builder.utils import (
    CONTENT_TYPE_MAPPING,
    DATA_DIR,
    IGNORED_FILES,
    INVALIDATIONS,
    LISTS_MAPPING,
    SITE_DIR,
    SRC_DIR,
    TEMPLATE_DIR,
)

config = configparser.ConfigParser()
config.read_file(open(SRC_DIR / "aws_config.ini"))

AWS_PROFILE = config.get("aws", "profile")
AWS_REGION = config.get("aws", "region")
BUCKET_DEV = config.get("aws", "bucket_dev")
BUCKET_PROD = config.get("aws", "bucket_prod")
DISTRIBUTION_ID = config.get("aws", "distribution_id")
META_CONTENT = """
A list of +50 high-quality resources available for free or cheaper than usual due to the COVID-19 so you can stay home and learn.
"""


def download_sheets():
    """Download sheets using the Google Sheets API"""
    shutil.rmtree(DATA_DIR, ignore_errors=True)
    DATA_DIR.mkdir()

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        SRC_DIR / "credentials.json", scope
    )
    client = gspread.authorize(credentials)

    workbook = client.open("Stay Home and Learn")
    for worksheet in workbook.worksheets():
        filename = DATA_DIR / (worksheet.title + ".csv")
        sheet_values = worksheet.get_all_values()
        print(f"Downloading: {worksheet.title}")
        with open(filename, "w") as f:
            writer = csv.writer(f)
            writer.writerows(sheet_values)


def generate_site():
    """Generate site in local directory"""
    shutil.rmtree(SITE_DIR, ignore_errors=True)
    SITE_DIR.mkdir()

    print("Copy template to site folder")
    for filename in TEMPLATE_DIR.iterdir():
        if filename.is_dir():
            shutil.copytree(str(filename), SITE_DIR / filename.name)
        elif filename.name != "template.html" and filename.name != ".DS_Store":
            shutil.copy(str(filename), SITE_DIR)
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("template.html")

    print("Process data and build site")
    csv_files = [
        filename for filename in DATA_DIR.iterdir() if filename.suffix == ".csv"
    ]
    csv_files.sort()
    lists_all = []
    for csv_file in csv_files:
        original_name = re.search(r"[0-9]_(.*?)\.csv", csv_file.name).group(1)
        processed_name = LISTS_MAPPING.get(original_name, original_name)
        with open(str(csv_file), mode="r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            list_ind = [row for row in csv_reader]
            lists_all.append((original_name, processed_name, list_ind))

    curr_date = datetime.now().strftime("%B %-d, %Y")
    output = template.render(
        lists=lists_all, last_update=curr_date, meta_content=META_CONTENT,
    )

    with open(SITE_DIR / "index.html", "w") as f:
        f.write(output)


def upload_recursively_to_s3(dir, bucket_name, s3, prefix="", verbose=True):
    """Upload a directory to s3 in a recursive manner (adding all files under it)

    Parameters
    ----------
    dir: Directory to upload to S3
    bucket_name: Name of bucket where site will be uploaded
    s3: Boto3 S3 Resource
    prefix: Prefix for directory to upload (e.g. /css)
    """
    for filename in dir.iterdir():
        if filename.is_dir():
            upload_recursively_to_s3(
                dir=filename,
                bucket_name=bucket_name,
                s3=s3,
                prefix=prefix + filename.name + "/",
            )
        elif filename.name not in IGNORED_FILES:
            if verbose:
                print(f"Uploading file: {prefix + filename.name}")
            content_type = CONTENT_TYPE_MAPPING.get(
                filename.suffix, "application/octet-stream"
            )
            s3.Bucket(bucket_name).upload_file(
                Filename=str(filename),
                Key=prefix + filename.name,
                ExtraArgs={"ContentType": content_type},
            )


def deploy_site(env="local", clear_cloudfront_cache=False):
    """Deploy site locally (just open browser :D), or to dev/prod bucket

    Parameters
    ----------
    env: Type of deployment. Either local, dev, or prod
    clear_cloudfront_cache: Clears cache in Cloudfront (to see changes instantly)
    """
    if env == "local":
        webbrowser.open("file://" + str(SITE_DIR / "index.html"))
    elif env == "dev":
        print("Upload data to S3")
        session = boto3.Session(profile_name=AWS_PROFILE)
        s3 = session.resource("s3")
        upload_recursively_to_s3(dir=SITE_DIR, bucket_name=BUCKET_DEV, s3=s3)
        webbrowser.open(f"http://{BUCKET_DEV}.s3-website.{AWS_REGION}.amazonaws.com")
    elif env == "prod":
        print("Upload data to S3")
        session = boto3.Session(profile_name=AWS_PROFILE)
        s3 = session.resource("s3")
        upload_recursively_to_s3(dir=SITE_DIR, bucket_name=BUCKET_PROD, s3=s3)
        if clear_cloudfront_cache:
            print("Clear Cloudfront cache")
            session = boto3.Session(profile_name=AWS_PROFILE)
            cloudfront = session.client("cloudfront")
            invalidation = cloudfront.create_invalidation(
                DistributionId=DISTRIBUTION_ID,
                InvalidationBatch={
                    "Paths": {"Quantity": len(INVALIDATIONS), "Items": INVALIDATIONS},
                    "CallerReference": str(time.time()),
                },
            )
        webbrowser.open(f"http://{BUCKET_PROD}.s3-website.{AWS_REGION}.amazonaws.com")
