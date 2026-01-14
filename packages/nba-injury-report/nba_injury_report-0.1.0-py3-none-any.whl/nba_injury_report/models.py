import io

from pydantic import BaseModel, ConfigDict, Field

from .constants import INJURY_COLUMNS


class InjuryEntry(BaseModel):
    """A single entry in an NBA injury report."""

    model_config = ConfigDict(
        validate_by_name=False,
        validate_by_alias=True,
        serialize_by_alias=True,
    )

    game_date: str | None = Field(None, alias="Game Date")
    game_time: str | None = Field(None, alias="Game Time")
    matchup: str | None = Field(None, alias="Matchup")
    team: str | None = Field(None, alias="Team")
    player_name: str | None = Field(None, alias="Player Name")
    current_status: str | None = Field(None, alias="Current Status")
    reason: str | None = Field(None, alias="Reason")


class InjuryReport(BaseModel):
    """An NBA injury report."""

    published_timestamp: str
    entries: list[InjuryEntry]

    def to_dataframe(self):
        """
        Return a pandas DataFrame representation of the injury report.

        Raises:
            ImportError: if pandas is not installed.
        """
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError(
                "pandas is required for to_dataframe(). "
                "Install it with `pip install nba-injury-report[pandas]`."
            ) from exc

        records = [entry.model_dump() for entry in self.entries]
        return pd.DataFrame.from_records(records)

    def to_list(self) -> dict:
        """Return list representation of the injury report."""
        return [entry.model_dump() for entry in self.entries]

    def to_json(self, **kwargs) -> str:
        """
        Return JSON string representation of the injury report.

        Args:
            **kwargs: json.dumps kwargs
        """
        import json

        return json.dumps([entry.model_dump() for entry in self.entries], **kwargs)

    def to_csv(self) -> str:
        """
        Return CSV string representation of the injury report.
        """
        import csv

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=INJURY_COLUMNS)

        writer.writeheader()
        for entry in self.entries:
            writer.writerow(entry.model_dump())

        return output.getvalue()

    def to_table(self) -> str:
        """
        Return formatted table string representation.

        Raises:
            ImportError: if tabulate is not installed.
        """
        try:
            from tabulate import tabulate
        except ImportError as exc:
            raise ImportError(
                "tabulate is required for to_table(). "
                "Install it with `pip install nba-injury-report[tabulate]`."
            ) from exc

        df = self.to_dataframe()
        return tabulate(df, headers="keys", tablefmt="github", showindex=False)
