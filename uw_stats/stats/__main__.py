import argparse
from pathlib import Path
import stats
import scraper
import sys


def parse_range(rangestring: str) -> range:
    """Parses a special range string.

    Args:
        rangestring (str): A string with format `"n1,n2,n3"`, where n2 is
        exclusive and n3 optional.

    Returns:
        range: The range object to produce.
    """
    parts = rangestring.split(",")
    if len(parts) not in (2, 3):
        raise ValueError("Invalid rangestring")
    nums = [int(i) for i in parts]
    return range(*nums)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="uw-stats",
        description="A statistical analyst designed for analyzing uwmc.de "
                    "forums.",
        epilog="Don't forget playing on uwmc.de!",
    )

    visualization_format_options = [
        i for i in dir(stats.DataVisualizer) if not i.startswith("_")  # type: ignore  # noqa
    ]
    visualization_format_options_str = ""
    for i in visualization_format_options:
        visualization_format_options_str += f"`{i}`, "
    visualization_format_options_str = visualization_format_options_str[:-2]
    parser.add_argument(
        "format",
        action="store",
        type=str,
        help="The output visualization format. Possible options are: "
             f"{visualization_format_options_str}",
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
        "--pagerange",
        action="store",
        type=str,
        required=False,
        help="A range of pages to be analyzed. Should have the format "
             "\"n1,n2,n3\". n2 is exclusive, n3 is optional. Only one "
             "*range flag is allowed.",
        dest="pagerange",
    )
    parser.add_argument(
        "--postrange",
        action="store",
        type=str,
        required=False,
        help="A range of posts to be analyzed. Should have the format "
             "\"n1,n2,n3\". n2 is exclusive, n3 is optional. Only one "
             "*range flag is allowed.",
        dest="postrange",
    )

    args = parser.parse_args()

    if args.pagerange and args.postrange:
        print("Only one *range flag allowed.")
        sys.exit(1)

    if args.format not in [str(i) for i in visualization_format_options]:
        print("Format positional argument should be one of "
              f"{visualization_format_options_str}")

    range_arg = {}
    if args.pagerange:
        range_arg["pagerange"] = parse_range(args.pagerange)
    if args.postrange:
        range_arg["postrange"] = parse_range(args.postrange)

    try:
        df = scraper.construct_dataframe(args.path, **range_arg)
    except FileNotFoundError:
        print("Invalid path provided (default is `.html_content` in cwd)")
        sys.exit(1)
    visualizer = stats.DataVisualizer(data_extractor=stats.DataExtractor(df))  # type: ignore  # noqa
    method = getattr(visualizer, args.format)
    visualization = method()
    if method.__doc__.strip().startswith("<printable>"):
        print(visualization)
    elif method.__doc__.startswith("<plot>"):
        ...  # not yet implemented
