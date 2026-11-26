"""Sample student records shared by the desktop and web versions.

Keeping this in its own module means the web app never has to import Tkinter.
"""

from __future__ import annotations

from .models import SUBJECTS, Student


# (roll number, name, [marks in SUBJECTS order])
SAMPLE_DATA = [
    ("24011001001", "Aarav Sharma", [92, 88, 95, 90, 86]),
    ("24011001002", "Diya Verma", [78, 85, 72, 80, 76]),
    ("24011001003", "Kabir Malhotra", [55, 62, 48, 58, 60]),
    ("24011001004", "Isha Gupta", [88, 92, 84, 89, 91]),
    ("24011001005", "Rohan Kapoor", [40, 35, 38, 42, 30]),
    ("24011001006", "Sneha Iyer", [73, 68, 79, 70, 74]),
    ("24011001007", "Anirudh", [96, 93, 98, 94, 92]),
    ("24011001008", "Meera Nair", [65, 70, 60, 68, 66]),
    ("24011001009", "Aditya Rao", [82, 79, 88, 85, 80]),
    ("24011001010", "Tanya Singh", [30, 45, 50, 38, 42]),
    ("24011001011", "Vikram Sethi", [58, 64, 55, 60, 57]),
    ("24011001012", "Priya Bansal", [90, 86, 89, 92, 88]),
]


def sample_students() -> list[Student]:
    """Build Student objects from the sample data table."""
    return [
        Student(roll, name, dict(zip(SUBJECTS, marks)))
        for roll, name, marks in SAMPLE_DATA
    ]
