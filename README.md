# stayhomeandlearn.org
![Python](https://img.shields.io/badge/Python-v3.7.1-brightgreen) ![License](https://img.shields.io/badge/license-MIT-blue) ![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)

Repository containing code for building and deploying the [stayhomeandlearn.org](https://stayhomeandlearn.org) site.

# How to setup locally

These are the instructions for setting up the site, including the setting up Google Sheets API as a CMS, and hosting it on S3 for free. 
For that purpose, you'll need to have a [Google account](https://myaccount.google.com/), a [GCP account](https://cloud.google.com/), and an [AWS account](https://aws.amazon.com/free/). 

In addition, you should have the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed, as it currently uses whatever profile you specify in the `aws_config.ini` for connecting to AWS.

## Setup local repository
1. Clone repository `git clone https://github.com/dylanjcastillo/stayhomeandlearn.org.git`
2. Get into the repository's local folder and create a virtual environment: `python3 -m venv [venv`
3. Install required libraries

## Using the Google Sheets API
1. Create a Workbook in Google Sheets (this is mine: [Stay Home and Learn](https://docs.google.com/spreadsheets/d/1RiPaFQHyDr1-jmefeenK3TAnn9MShQQBhD6fZV0LgGM/edit?usp=sharing))
2. Go to the [Google APIs Console](https://console.developers.google.com/)
3. Create a new project.
4. Click Enable API. Search for and enable the Google Drive API.
5. *Create credentials* for a *Web Server* to access *Application Data*.
6. Name the service account and grant it a *Project* Role of *Editor*.
7. Download the JSON file.
8. Copy the JSON file <REPO>/site_builder and rename it to `credentials.json`
9. Find the client_email inside `credentials.json`. Back in your spreadsheet, click the *Share* button in the top right, and paste the client email into the *People* field to give it edit rights. Hit Send. 

Steps 3-9 are *borrowed* from here: [Google Spreadsheets and Python](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html)

## Setting up an S3 bucket for hosting a static site 

1. Go to the [Amazon S3 Console](https://console.aws.amazon.com/s3) 
2. Create an S3 bucket
3. Once in the bucket, select *Properties* and go to the *Static website hosting* box
4. Select the option *Use this bucket to host a website*
5. Under *Index document* and *Error document* put index.html
6. Save the URL from *Endpoint*. That's what you'll use for connecting to your site.
7. Go to *Permissions* and click *Edit*
8. Clear *Block all public access*, choose *Save*, and confirm. Make sure that you understand that **when you change this anyone on the internet can access the contents of this bucket**. That's what you want when you are publishing a site, however don't put anything private there!
9. Now go to *Bucket Policy*, replace the bucket name in the following policy, paste it there, and click Save. 
```json5
{
  "Version":"2012-10-17",
  "Statement":[{
	"Sid":"PublicReadGetObject",
        "Effect":"Allow",
	  "Principal": "*",
      "Action":["s3:GetObject"],
      "Resource":["arn:aws:s3:::BUCKET-NAME-HERE/*"
      ]
    }
  ]
}
```
This policy will make the objects store in the bucket you just created publicly readable.

## Provide AWS configuration 
1. Rename the `aws_config_example.ini` file to `aws_config.ini`
2. Provide profile that you'll use for connecting to AWS
3. Check region in the *Endpoint* URL from the previous section (step 6)  
4. If you followed the previous step and created only one S3 bucket put its name after `bucket_dev`. You can use `bucket_prod` and `cloudfront_id` if you have a production version of your site that uses Cloudfront. I use it for [stayhomeandlearn.org](https://stayhomeandlearn.org).

# How to use

From the root folder of your repository, you can simply run it as follows: `python run.py`. This will download the sheets from your workbook, generate the site, and open a local version of it in your web browser.

You can also build the site and deploy it directly to S3. For the dev bucket you can run the following command: `python run.py --env dev`.

If you have your production site and Cloudfront configuration setup, you can run `python run.py --env prod --clear`. This will deploy the site and clear the Cloudfront cache, so that your latest changes on your site get reflected through the CDN. 

# License

This project is licensed under the terms of the MIT license.
