"""CSV file storage using the standard-library ``csv`` module.

Demonstrates: file read/write with ``with``, pathlib/os path handling,
lists of dictionaries, exception handling and list comprehensions
(Practicals 09, 13, 19, 20, 21 and 22).
"""

from __future__ import annotations

import csv
from pathlib import Path

from .models import SUBJECTS, Student


CSV_COLUMNS = [
    "Roll No",
    "Name",
    *SUBJECTS,
    "Total",
    "Average",
    "Grade",
    "Result",
]


class StudentRepository:
    """Reads and writes student records in a CSV file."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def load(self) -> list[Student]:
        """Load all valid records. Creates an empty file if none exists."""
        if not self.path.exists():
            self.save([])
            return []

        students: list[Student] = []
        with self.path.open("r", newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                try:
                    student = Student.from_row(row)
                    student.validate()
                except (ValueError, TypeError, AttributeError):
                    # Skip broken rows instead of crashing the whole app.
                    continue
                students.append(student)
        return students

    def save(self, students: list[Student], path: Path | str | None = None) -> None:
        """Overwrite the CSV with the given students (or write to ``path``)."""
        target = Path(path) if path is not None else self.path
        target.parent.mkdir(parents=True, exist_ok=True)

        with target.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for student in students:
                writer.writerow(student.to_row())
