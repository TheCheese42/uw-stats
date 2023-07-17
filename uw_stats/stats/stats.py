import pandas as pd
from typing import Optional


def mean(values: list[int | float]) -> float:
    return sum(values) / float(len(values))


class DataExtractor:
    """A class to extract various valuable data from a dataframe.
    """
    def __init__(
        self,
        df: pd.DataFrame,
        pagerange: Optional[range] = None,
        postrange: Optional[range] = None,
    ) -> None:
        """Initialize the Extractor by providing a dataframe and
        post/pageranges to specify the data to be analyzed. Ranges
        apply for every further method. Second range parameter is exclusive.

        Args:
            df (pd.DataFrame): The pandas Dataframe containing the data.
            pagerange (range, optional): The pagerange to include in the table.
            Mutually exclusive with other ranges. Defaults to None.
            postrange (range, optional): The postrange to include in the table.
            Mutually exclusive with other ranges. Defaults to None.
        """
        # Only save data included in ranges
        if pagerange:
            start = pagerange[0]
            end = pagerange[-1]
            selected = df.loc[
                (df["page_num"] >= start) & (df["page_num"] <= end)
            ]
        elif postrange:
            start = postrange[0]
            end = postrange[-1]
            selected = df.loc[start:end]
        else:
            selected = df
        self.df = selected

    @property
    def messages(self) -> int:
        return len(self.df)

    def get_authors(self) -> list[str]:
        """Get a list of all authors.

        Returns:
            list[str]: The list of authors.
        """
        return self.df["author"].unique().tolist()

    def select_messages_from_author(self, author: str) -> pd.DataFrame:
        return self.df[self.df["author"] == author]

    def get_messages_from_author(self, author: str) -> int:
        """Get the number of messages an author wrote.

        Args:
            author (str): The author's name.

        Returns:
            int: The message count.
        """
        return len(self.select_messages_from_author(author))

    def get_rule_violating_messages_from_author(self, author: str) -> int:
        posts = self.select_messages_from_author(author)
        return len(posts[posts["is_rules_compliant"] == False])  # noqa

    def get_authors_sorted_by_messages(self) -> list[str]:
        authors = self.get_authors()
        authors_to_messages = {}
        for author in authors:
            posts = self.select_messages_from_author(author)
            authors_to_messages[author] = len(posts)
        authors_to_messages = {
            k: v for k, v in sorted(
                authors_to_messages.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        }
        return list(authors_to_messages.keys())


class DataVisualizer:
    """A class providing various methods used to visualize
    data in various formats.
    """
    def __init__(self, data_extractor: DataExtractor) -> None:
        self.data_extractor = data_extractor

    def maua1_style_mdtable(self):
        """Constructs a BBCode Table with the authors as Y-axis and the columns
        as X-axis. For an example see https://uwmc.de/p370063.

        Args:

        Returns:
            str: The table using BBCode syntax.
        """
        table = "\
            [TABLE=full][TR][TD]Spieler[/TD][TD]Anzahl Beiträge[/TD]\
            [TD]Anzahl nicht regelkonformer Beiträge[/TD]\
            [TD]Prozentanzahl nicht regelkonformer Beiträge[/TD][/TR]"

        authors_sorted = self.data_extractor.get_authors_sorted_by_messages()
        for author in authors_sorted:
            messages = self.data_extractor.get_messages_from_author(author)
            rules_violating_messages = (
                self.data_extractor.get_rule_violating_messages_from_author(
                    author
                )
            )
            percentage_rules_violating_messages = (
                rules_violating_messages / messages
            )
            table += f"\
                [TR][TD]{author}[/TD]\
                [TD]{messages}[/TD]\
                [TD]{rules_violating_messages}[/TD]\
                [TD]{percentage_rules_violating_messages * 100}%[/TD][/TR]"
        table += "[/TABLE]"
        table = table.replace("  ", "")
        table = table.strip()
        return table
