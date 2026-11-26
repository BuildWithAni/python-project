"""Data analysis with pandas: DataFrame creation, filtering, aggregation.

Demonstrates: DataFrames, groupby-style aggregation, sorting, boolean
indexing and summary statistics (Practicals 27 and 28).
"""

from __future__ import annotations

import pandas as pd

from .models import SUBJECTS, Student


DATAFRAME_COLUMNS = [
    "Roll No",
    "Name",
    *SUBJECTS,
    "Total",
    "Average",
    "Grade",
    "Result",
]


def to_dataframe(students: list[Student]) -> pd.DataFrame:
    """Convert a list of Student objects into a pandas DataFrame."""
    return pd.DataFrame(
        [student.to_row() for student in students], columns=DATAFRAME_COLUMNS
    )


def summarize(df: pd.DataFrame) -> dict:
    """Return headline statistics for the whole class."""
    if df.empty:
        return {
            "count": 0,
            "average": 0.0,
            "topper": "-",
            "pass_percent": 0.0,
        }

    topper_row = df.loc[df["Average"].idxmax()]
    return {
        "count": int(len(df)),
        "average": float(df["Average"].mean()),
        "topper": f"{topper_row['Name']} ({topper_row['Average']:.1f})",
        "pass_percent": float((df["Result"] == "Pass").mean() * 100),
    }


def subject_averages(df: pd.DataFrame) -> dict[str, float]:
    """Average mark of each subject (empty dict when there is no data)."""
    if df.empty:
        return {subject: 0.0 for subject in SUBJECTS}
    return {subject: float(value) for subject, value in df[list(SUBJECTS)].mean().items()}


def grade_counts(df: pd.DataFrame) -> dict[str, int]:
    """How many students got each grade."""
    if df.empty:
        return {}
    return {str(grade): int(count) for grade, count in df["Grade"].value_counts().items()}


def top_students(df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    """The ``limit`` highest scorers, sorted by average."""
    if df.empty:
        return df
    return df.sort_values("Average", ascending=False).head(limit)
