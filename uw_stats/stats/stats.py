import pandas as pd
from typing import Optional


def mean(values: list[int | float]) -> float:
    return sum(values) / float(len(values))


def build_maua1_style_table(
    df: pd.DataFrame,
    pagerange: Optional[range] = None,
    postrange: Optional[range] = None,
) -> str:
    """Constructs a BBCode Table with the authors as Y-axis and the columns
    as X-axis. For an example see https://uwmc.de/p370063.
    If no *range parameters are given all posts will be included.

    Args:
        df (pd.DataFrame): The pandas Dataframe containing the data.
        pagerange (range, optional): The pagerange to include in the table.
        Mutually exclusive with other ranges. Defaults to None.
        postrange (range, optional): The postrange to include in the table.
        Mutually exclusive with other ranges. Defaults to None.

    Returns:
        str: The table using BBCode syntax.
    """
    if all([pagerange, postrange]):
        raise ValueError("Only one *range parameter can be given.")

    # This repetition is intended because it looks beautiful. >:)
    if pagerange:
        start = pagerange[0]
        end = pagerange[-1]
        selected = df.loc[(df['page_num'] >= start) & (df['page_num'] <= end)]
    elif postrange:
        start = postrange[0]
        end = postrange[-1]
        selected = df.loc[start:end]
    else:
        selected = df

    all_authors = selected["author"].unique().tolist()
    stats_by_author: dict[str, tuple[int, int, float]] = {}
    for author in all_authors:
        posts = selected[selected["author"] == author]
        amount = len(posts)
        amount_rule_violating = len(posts[posts["is_rules_compliant"] == False])  # noqa
        percentage_rule_violating = amount_rule_violating / amount
        stats_by_author[author] = (
            amount, amount_rule_violating, percentage_rule_violating
        )
    total = (
        sum([i[0] for i in stats_by_author.values()]),  # Amount
        sum([i[1] for i in stats_by_author.values()]),  # Amount violated
        mean([i[2] for i in stats_by_author.values()]),  # Percentage violated
    )
    stats_by_author["Gesamt"] = total
    authors_sorted_by_amount: list[str] = [
        i[0] for i in sorted(
            stats_by_author.items(),
            key=lambda x: x[1][0],
            reverse=True,
        )
    ]
    table = "\
        [TABLE=full][TR][TD]Spieler[/TD][TD]Anzahl Beiträge[/TD]\
        [TD]Anzahl nicht regelkonformer Beiträge[/TD]\
        [TD]Prozentanzahl nicht regelkonformer Beiträge[/TD][/TR]"

    for author in authors_sorted_by_amount:
        table += f"\
            [TR][TD]{author}[/TD]\
            [TD]{stats_by_author[author][0]}[/TD]\
            [TD]{stats_by_author[author][1]}[/TD]\
            [TD]{stats_by_author[author][2] * 100}%[/TD][/TR]"
    table += "[/TABLE]"

    return table
