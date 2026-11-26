"""Unit tests for the non-GUI parts of the project.

Run with:  python -m unittest discover -s tests -v
"""

import tempfile
import unittest
from pathlib import Path

from src.analytics import summarize, to_dataframe
from src.models import SUBJECTS, Student, grade_for
from src.storage import StudentRepository


def make_student(roll="1", name="Test Student", marks=None) -> Student:
    return Student(roll, name, dict(zip(SUBJECTS, marks or [80, 80, 80, 80, 80])))


class TestStudent(unittest.TestCase):
    def test_grade_boundaries(self):
        self.assertEqual(grade_for(95), "A+")
        self.assertEqual(grade_for(80), "A")
        self.assertEqual(grade_for(70), "B+")
        self.assertEqual(grade_for(60), "B")
        self.assertEqual(grade_for(50), "C")
        self.assertEqual(grade_for(40), "D")
        self.assertEqual(grade_for(39), "F")

    def test_totals_and_average(self):
        student = make_student(marks=[90, 80, 70, 60, 50])
        self.assertEqual(student.total, 350)
        self.assertAlmostEqual(student.average, 70)

    def test_pass_needs_every_subject_and_average(self):
        self.assertEqual(make_student(marks=[50, 50, 50, 50, 50]).result, "Pass")
        # Average is 41, but one subject is below 33.
        self.assertEqual(make_student(marks=[30, 45, 45, 42, 43]).result, "Fail")

    def test_validation(self):
        with self.assertRaises(ValueError):
            make_student(name="").validate()
        with self.assertRaises(ValueError):
            make_student(marks=[120, 80, 80, 80, 80]).validate()


class TestRepository(unittest.TestCase):
    def test_csv_round_trip(self):
        students = [make_student("1", "A", [90, 90, 90, 90, 90]),
                    make_student("2", "B", [50, 55, 60, 65, 70])]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "students.csv"
            repository = StudentRepository(path)
            repository.save(students)
            loaded = repository.load()

        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].name, "A")
        self.assertEqual(loaded[1].grade, "B")

    def test_missing_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as folder:
            repository = StudentRepository(Path(folder) / "new.csv")
            self.assertEqual(repository.load(), [])


class TestAnalytics(unittest.TestCase):
    def test_summary(self):
        students = [make_student("1", "A", [90, 90, 90, 90, 90]),
                    make_student("2", "B", [60, 60, 60, 60, 60])]
        stats = summarize(to_dataframe(students))
        self.assertEqual(stats["count"], 2)
        self.assertEqual(stats["average"], 75.0)
        self.assertEqual(stats["pass_percent"], 100.0)
        self.assertTrue(stats["topper"].startswith("A"))

    def test_empty_summary_does_not_crash(self):
        stats = summarize(to_dataframe([]))
        self.assertEqual(stats["count"], 0)
        self.assertEqual(stats["topper"], "-")


if __name__ == "__main__":
    unittest.main()
