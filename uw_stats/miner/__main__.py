import argparse
import sys
from pathlib import Path

import miner

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="uw-miner",
        description="A dataminer designed for the uwmc.de forum.",
        epilog="Don't forget playing on uwmc.de!",
    )

    parser.add_argument(
        "-u",
        "--url",
        action="store",
        required=True,
        help="The threads base url.",
        dest="url",
    )
    parser.add_argument(
        "-p",
        "--path",
        action="store",
        default=Path.cwd() / "html_content",
        type=Path,
        required=False,
        help="Path to where the HTML files are saved.",
        dest="path",
    )
    parser.add_argument(
        "--threaded",
        action="store_true",
        default=False,
        required=False,
        help="Should all pages be fetched concurrently?",
        dest="threaded",
    )

    args = parser.parse_args()


    try:
        if args.threaded:
            print("Fetching in threaded mode.")
            miner.fetch_and_save_all_pages_concurrently(
                base_url=args.url,
                working_dir=args.path,
            )
        else:
            print(
                "Fetching linearly. To speed up the process use --threaded flag."
            )
            miner.fetch_and_save_all_pages_linearly(
                base_url=args.url,
                working_dir=args.path,
            )
    except KeyboardInterrupt:
        print("Cancelled due to KeyboardInterrupt.")
        sys.exit()

    print(
        f"Fetched and saved {miner.get_last_page(args.url)} pages into "
        f"{args.path.resolve()}."
    )
