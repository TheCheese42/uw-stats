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
        default=Path.cwd() / ".html_content",
        type=Path,
        required=False,
        help="Path to where the HTML files are saved.",
        dest="path",
    )
    parser.add_argument(
        "-n",
        "--only-new-pages",
        action="store_true",
        required=False,
        help=("Only fetches pages that aren't saved yet. Doesn't "
              "update old pages that have changed since."),
        dest="only_new_pages",
    )
    parser.add_argument(
        "--threaded",
        action="store_true",
        default=False,
        required=False,
        help="Should all pages be fetched concurrently?",
        dest="threaded",
    )
    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        default=False,
        required=False,
        help="Do not display informational messages.",
        dest="silent",
    )

    args = parser.parse_args()
    miner.set_verbose(not args.silent)  # type: ignore
    # mypy bug, shows missing attribute of miner although it's there.
    # Happened multiple times, therefore multiple `# type: ignore` lines.

    if not args.url.endswith("/"):
        args.url += "/"

    try:
        if args.threaded:
            print("Fetching in threaded mode.")
            if args.only_new_pages:
                print("Only new pages: activated.")
                miner.fetch_new_pages(  # type: ignore
                    args.url, working_dir=args.path, threaded=args.threaded
                )
            else:
                miner.fetch_and_save_all_pages_concurrently(
                    base_url=args.url, working_dir=args.path
                )
        else:
            print(
                "Fetching linearly. To speed up the process use "
                "--threaded flag."
            )
            if args.only_new_pages:
                print("Only new pages: activated.")
                miner.fetch_new_pages(  # type: ignore
                    args.url, working_dir=args.path, threaded=args.threaded
                )
            miner.fetch_and_save_all_pages_linearly(
                base_url=args.url,
                working_dir=args.path,
            )
    except KeyboardInterrupt:
        print("Cancelled due to KeyboardInterrupt.")
        sys.exit(1)

    print(
        f"Fetched and saved {miner.get_last_page(args.url)} pages into "
        f"{args.path.resolve()}."
    )
