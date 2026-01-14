import datetime
import io
import re

import httpx
import pymupdf

from ._client import _get_client
from .constants import INJURY_COLUMNS, REASON_KEY_WORDS, STATUSES, TEAM_NAMES
from .models import InjuryEntry, InjuryReport


def get_injury_report(
    timestamp: str,
    client: httpx.Client | None = None,
) -> InjuryReport:
    """Fetch and process a pre-game NBA Injury Report.

    This function returns the latest injury report within the past hour of a
    given time. If no such report is available, raises an error.

    Args:
        timestamp: ISO 8601–formatted datetime string.
            Expected format: "YYYY-MM-DDTHH:MM:SS"
        client: Optional httpx client for making requests. If not provided,
            a default client will be created.

    Returns:
        InjuryReport with structured entries.

    Raises:
        httpx.HTTPError: If the report cannot be fetched from NBA servers.
        pydantic.ValidationError: If the PDF cannot be parsed into valid entries.

    Example:
        >>> from datetime import datetime
        >>> # To get the latest report available at 10:30 AM on Dec 1, 2024
        >>> report = get_injury_report('2024-12-01T10:30:00')
    """
    # NBA publishes injury reports at the half hour
    # E.g. "10AM" in the api url returns a 10:30 AM report
    dt = datetime.datetime.fromisoformat(timestamp)
    adjusted_dt = dt - datetime.timedelta(minutes=30)
    date_str = adjusted_dt.strftime("%Y-%m-%d")
    time_str = adjusted_dt.strftime("%I%p")

    published_datetime = datetime.datetime.strptime(
        f"{date_str} {time_str}", "%Y-%m-%d %I%p"
    ) + datetime.timedelta(minutes=30)

    pdf = _fetch_pdf(date_str, time_str, client)
    records = _process_pdf(pdf)
    return InjuryReport(
        published_timestamp=published_datetime.isoformat(), entries=records
    )


def _fetch_pdf(date: str, time: str, client: httpx.Client | None = None) -> bytes:
    """Return injury report pdf content as bytes."""
    url = (
        f"https://ak-static.cms.nba.com/referee/injury/Injury-Report_{date}_{time}.pdf"
    )

    if client is None:
        client = _get_client()

    resp = client.get(url=url)
    resp.raise_for_status()
    return resp.content


def _process_pdf(pdf: bytes) -> list[InjuryEntry]:
    """Return structured table from an injury report pdf."""
    doc = pymupdf.open(stream=io.BytesIO(pdf))
    vals = []
    for page in doc:
        vals.extend(page.get_text().splitlines())
    doc.close()
    records = _extract_records(vals)
    records = _forward_fill_entries(records)
    return records


def _extract_records(vals: list[str]) -> list[InjuryEntry]:
    """Return structured data from pdf text."""
    rows = []
    row = {}
    cur_idx = -1
    for val in vals:
        pred = _predict_column(val)
        if pred is None:
            continue

        pred_idx = INJURY_COLUMNS.index(pred)
        # Reason can wrap onto multiple lines
        if pred == "Reason" and "Reason" in row:
            row["Reason"] += " " + val
        elif pred_idx <= cur_idx:
            rows.append(InjuryEntry.model_validate(row))
            row = {}
            row[pred] = val
        else:
            row[pred] = val

        cur_idx = pred_idx

    if row:
        rows.append(InjuryEntry.model_validate(row))
    return rows


def _predict_column(val: str) -> str | None:
    """Return the column name to which a piece of text belongs."""
    val = val.strip()
    if (
        ("Injury Report" in val)
        or re.fullmatch(r"Page \d+ of \d+", val)
        or (val in INJURY_COLUMNS)
        or len(val) == 0
    ):
        return None

    if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", val):
        return "Game Date"

    if re.fullmatch(r"\d{1,2}:\d{2}\s*\([A-Za-z]{2,}\)", val):
        return "Game Time"

    if "@" in val:
        return "Matchup"

    if " " not in val and val in STATUSES:
        return "Current Status"

    if val in TEAM_NAMES:
        return "Team"

    if "," in val and any(word.lower() in val.lower() for word in REASON_KEY_WORDS):
        return "Reason"

    if "," in val:
        return "Player Name"

    return "Reason"


def _forward_fill_entries(entries: list[InjuryEntry]) -> list[InjuryEntry]:
    """Return a set of injury entries with the first columns forward-filled."""
    ffill_cols = INJURY_COLUMNS[:4]
    last_seen = {col: None for col in ffill_cols}

    filled: list[InjuryEntry] = []
    for entry in entries:
        data = entry.model_dump()
        for field in last_seen:
            item = data.get(field)
            if item is not None:
                last_seen[field] = item
            else:
                data[field] = last_seen[field]

        filled.append(InjuryEntry.model_validate(data))
    return filled


if __name__ == "__main__":
    ts = "2023-12-18T08:30:00"
    res = get_injury_report(ts)
