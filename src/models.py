"""Student data model.

Demonstrates: classes and objects (OOP), dataclasses, @property, tuples,
dictionaries, f-strings, if/else decisions and validation with exceptions
(Practicals 01, 04, 08 and 12).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


# Subjects are fixed for every student, so a tuple (immutable) is a good fit.
SUBJECTS = ("Python", "Java", "Maths", "Physics", "Chemistry")

MIN_MARK = 0
MAX_MARK = 100
PASS_MARK_PER_SUBJECT = 33
PASS_AVERAGE = 40

# (minimum average, grade) - ordered from highest to lowest.
GRADE_SCALE = (
    (90, "A+"),
    (80, "A"),
    (70, "B+"),
    (60, "B"),
    (50, "C"),
    (40, "D"),
)


def grade_for(average: float) -> str:
    """Return a letter grade for a numeric average using the grade scale."""
    for cutoff, grade in GRADE_SCALE:
        if average >= cutoff:
            return grade
    return "F"


@dataclass
class Student:
    """One student record with marks for all subjects."""

    roll_no: str
    name: str
    marks: Dict[str, float]

    def __post_init__(self) -> None:
        # Store marks in a fixed subject order and make sure they are numbers.
        self.marks = {
            subject: float(self.marks.get(subject, 0)) for subject in SUBJECTS
        }

    # --- Derived values are properties so they can never get out of sync ---
    @property
    def total(self) -> float:
        return sum(self.marks.values())

    @property
    def average(self) -> float:
        return self.total / len(SUBJECTS)

    @property
    def grade(self) -> str:
        return grade_for(self.average)

    @property
    def result(self) -> str:
        """Pass requires >= 40 average and >= 33 in every subject."""
        passed = self.average >= PASS_AVERAGE and all(
            mark >= PASS_MARK_PER_SUBJECT for mark in self.marks.values()
        )
        return "Pass" if passed else "Fail"

    def validate(self) -> None:
        """Raise ValueError with a helpful message if the record is invalid."""
        if not self.roll_no.strip():
            raise ValueError("Roll number is required.")
        if not self.name.strip():
            raise ValueError("Name is required.")
        for subject, mark in self.marks.items():
            if not MIN_MARK <= mark <= MAX_MARK:
                raise ValueError(
                    f"{subject} marks must be between {MIN_MARK} and {MAX_MARK}."
                )

    def to_row(self) -> dict:
        """Flatten the object into a dictionary suitable for a CSV row."""
        row = {"Roll No": self.roll_no.strip(), "Name": self.name.strip()}
        row.update({subject: self.marks[subject] for subject in SUBJECTS})
        row.update(
            {
                "Total": self.total,
                "Average": round(self.average, 2),
                "Grade": self.grade,
                "Result": self.result,
            }
        )
        return row

    @classmethod
    def from_row(cls, row: dict) -> "Student":
        """Build a Student from a CSV row (derived columns are recomputed)."""
        marks = {subject: float(row.get(subject, 0) or 0) for subject in SUBJECTS}
        return cls(
            roll_no=str(row.get("Roll No", "")).strip(),
            name=str(row.get("Name", "")).strip(),
            marks=marks,
        )
