import argparse
from site_builder.site_builder import download_sheets, generate_site, deploy_site


def parse_arguments():
    """Parse arguments when executed from CLI"""
    parser = argparse.ArgumentParser(
        prog="run-site-builder",
        description="CLI tool for building and deploying stayhomeandlearn.org",
    )
    parser.add_argument(
        "--environment",
        choices=["local", "dev", "prod"],
        default="local",
        help="Environment where site will be deployed",
    )
    parser.add_argument(
        "--clear-cloudfront-cache",
        action="store_true",
        help="Clears Cloudfront cache after deploying site to S3 bucket",
    )
    args = parser.parse_args()
    return args


def main(args):
    print("### Get data from Google Sheets ###")
    download_sheets()
    print("### Build site using template ###")
    generate_site()
    print(f"### Deploy site: {args.environment} ###")
    deploy_site(
        env=args.environment, clear_cloudfront_cache=args.clear_cloudfront_cache
    )
    pass


if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
