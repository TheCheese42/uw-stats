import bs4
import pandas as pd
from pathlib import Path


def construct_dataframe(path: str | Path) -> pd.DataFrame:
    """Constructs a dataframe pagewise from HTML files.

    Args:
        path (str | Path): The path containing the HTML files.

    Returns:
        pd.DataFrame: The newly created dataframe.
    """
    df = pd.DataFrame(columns=("author", "content", "likes", "raw"))

    for file in Path(path).iterdir():
        if file.is_dir():
            continue
        soup = bs4.BeautifulSoup(file.read_text("utf-8"))

        for message in soup.find_all("article", class_="message"):
            content = message.find("article", class_="message-body")
            try:
                # Insert a dot before last smiley to let them count as
                # punctuation.
                content.find_all(class_="smilie")[-1].insert_before(".")
            except IndexError:
                pass
            
