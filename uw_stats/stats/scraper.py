import bs4
import pandas as pd
from pathlib import Path
import re


# Parts of this code are inspired or copied from
# https://github.com/ifscript/lootscript.
# This notice is also found at the top of affected functions.


def find_all_messages(soup: bs4.BeautifulSoup) -> list[bs4.element.Tag]:
    """Returns a list of message article tags.

    Args:
        soup (bs4.BeautifulSoup): The BeautifulSoup object of the HTML page.

    Returns:
        list[bs4.element.Tag]: The list containing the message article tags.
    """
    return soup.find_all("article", class_="message")


def find_message_content(message: bs4.element.Tag) -> bs4.element.Tag:
    """Retrieves the content from a message.

    Args:
        message (bs4.element.Tag): The message's element tag object.

    Returns:
        bs4.element.Tag: The message content's element tag object.
    """
    return message.find("article", class_="message-body")


def construct_dataframe(path: str | Path) -> pd.DataFrame:
    """Constructs a dataframe pagewise from HTML files.
    This could eventually be split up into multiple functions or a class.

    Args:
        path (str | Path): The path containing the HTML files.

    Returns:
        pd.DataFrame: The newly created dataframe.
    """
    df = pd.DataFrame(
        columns=(
            "raw",
            "author",
            "content",
            "like_count",
            "quote_count",
            "quoted_list",
            "spoiler_count",
            "mentions_count",
            "mentioned_list",
            "word_count",
            "emoji_count",
            "emoji_frequency_mapping",
        )
    )

    for file in sorted(
        Path(path).iterdir(), key=lambda s: re.findall(r"\d+", s.name)[0]
    ):
        if file.is_dir():
            continue
        print("Processing", file)
        soup = bs4.BeautifulSoup(file.read_text("utf-8"))
        import time

        for message in find_all_messages(soup):
            start = time.time()
            raw = str(message)
            author = message["data-author"]
            content = find_message_content(message)
            insert_dot_before_last_emoji(content)
            like_count = get_amount_of_likes(message)
            quote_count = get_amount_of_quotes(message)
            quoted_list = get_list_of_quoted_usernames(message)
            spoiler_count = get_amount_of_spoilers(message)
            mentioned_list = get_list_of_mentioned_usernames(message)
            mentions_count = len(mentioned_list)
            word_count = get_amount_of_words(message)
            emoji_frequency_mapping = (
                get_mapping_of_emojis_and_frequency(message))
            emoji_count = len(emoji_frequency_mapping)
            message_series = pd.Series(
                data=(
                    raw,
                    author,
                    content,
                    like_count,
                    quote_count,
                    quoted_list,
                    spoiler_count,
                    mentions_count,
                    mentioned_list,
                    word_count,
                    emoji_count,
                    emoji_frequency_mapping,
                )
            )
            df = pd.concat([df, message_series])
            print(time.time() - start)

    return df


def get_amount_of_likes(message: bs4.element.Tag) -> int:
    """Get the amount of likes a message has.

    Args:
        message (bs4.element.Tag): The messages element tag object.

    Returns:
        int: The like count.
    """
    # Inspired by
    # https://github.com/ifscript/lootscript/blob/main/lootscript.py
    likes_bar = message.find("a", class_="reactionsBar-link")

    if likes_bar is None:
        # No likes found
        return 0

    num_likes = len(likes_bar.find_all('bdi'))

    if num_likes < 3:
        # Can be more if num_likes is 3
        return num_likes

    for bdi in likes_bar("bdi"):
        # Remove usernames
        bdi.decompose()

    text = likes_bar.get_text(strip=True)
    try:
        # Return additional likes plus the ones being counted
        return int(re.findall(r"\d+", text)[0]) + num_likes
    except IndexError:
        # There are just 3 likes
        return num_likes


def insert_dot_before_last_emoji(
    soup: bs4.BeautifulSoup | bs4.element.Tag
) -> None:
    """Inserts a dot before the messages last emoji to let
    them count as punctuation.

    Args:
        soup (bs4.BeautifulSoup | bs4.element.Tag): The message's
        soup or element tag object.
    """
    try:
        soup.find_all(class_="smilie")[-1].insert_before(".")
    except IndexError:
        pass  # no emojis in soup


def get_amount_of_quotes(message: bs4.element.Tag) -> int:
    """Retrieves the amount of quotes of a message.

    Args:
        message (bs4.element.Tag): The message's element tag object.

    Returns:
        int: The quote count.
    """
    return len(message.find_all("blockquote", class_="bbCodeBlock--quote"))


def get_list_of_quoted_usernames(message: bs4.element.Tag) -> list[str]:
    """Retrieves a list of usernames being quoted in a message.

    Args:
        message (bs4.element.Tag): The message's element tag object.

    Returns:
        list[str]: The list containing the usernames.
    """
    usernames: list[str] = []
    for quote in message.find_all("blockquote", class_="bbCodeBlock--quote"):
        usernames.append(quote["data-quote"])
    return usernames


def get_amount_of_spoilers(message: bs4.element.Tag) -> int:
    """Retrieves the amount of spoilers in a message.

    Args:
        message (bs4.element.Tag): The message's element tag object.

    Returns:
        int: The spoiler count.
    """
    return len(message.find_all("div", class_="bbCodeSpoiler"))


def get_list_of_mentioned_usernames(message: bs4.element.Tag) -> list[str]:
    """Retrieves a list of mentioned usernames. Get the amount of mentions
    by using len() on the list.

    Args:
        message (bs4.element.Tag): The message's element tag object.

    Returns:
        list[str]: The list containing all usernames.
    """
    usernames: list[str] = []
    for mention in message.find_all("a", class_="username"):
        if (uname := mention.get_text(strip=True))[0] == "@":
            # There can also be other anchor tags with that class.
            # However, only mentions start with @.
            usernames.append(uname[1:])
    return usernames


def get_amount_of_words(message: bs4.element.Tag) -> int:
    """Retrieves the amount of words in a message.

    Args:
        message (bs4.element.Tag): The message's element tag object.

    Returns:
        int: The word count.
    """
    content = find_message_content(message)
    return _count_words(content.get_text(strip=True))


def get_mapping_of_emojis_and_frequency(
    message: bs4.element.Tag
) -> dict[str, int]:
    """Returns a mapping from all occurring emojis to their frequency.

    Args:
        message (bs4.element.Tag): The message's element tag object.

    Returns:
        dict[str, int]: A mapping from all occurring emojis to their frequency.
    """
    emojis: dict[str, int] = {}
    for emoji in message.find_all("img", class_="smilie"):
        alt = emoji["alt"]
        if not emojis.get(alt):
            emojis[alt] = 1
            continue
        emojis[alt] += 1
    return emojis


def _count_words(string: str) -> int:
    """Counts the amount of words in a string by utilizing the
    str.split() method. Splits on any whitespace character and
    discards empty strings.

    Args:
        string (str): The string to count the words from.

    Returns:
        int: The amount of words in the string.
    """
    return len(string.split())
