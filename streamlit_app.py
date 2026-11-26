"""Streamlit web version of the Student Report Card System.

Run locally with:   streamlit run streamlit_app.py
Deploy for free at: https://share.streamlit.io  (or Hugging Face Spaces)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.analytics import summarize, to_dataframe
from src.charts import build_figure
from src.models import SUBJECTS, Student
from src.sample_data import sample_students
from src.storage import StudentRepository


DATA_FILE = Path(__file__).resolve().parent / "data" / "students.csv"
REPOSITORY = StudentRepository(DATA_FILE)

st.set_page_config(
    page_title="Student Report Card System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# The session state is the live copy of the records shown in the browser.
if "students" not in st.session_state:
    st.session_state.students = REPOSITORY.load()


def save_students() -> None:
    """Write the current session records back to the CSV file."""
    REPOSITORY.save(st.session_state.students)


def current_dataframe() -> pd.DataFrame:
    """Convert the session records into a pandas DataFrame."""
    return to_dataframe(st.session_state.students)


st.title("🎓 Student Report Card System")
st.caption(
    "A Python web project by Anirudh — add students, automatic grades, CSV export "
    "and an analytics dashboard."
)

page = st.sidebar.radio("Go to", ["Manage Students", "Dashboard", "How to present"])
st.sidebar.divider()
st.sidebar.info(f"Records in this session: **{len(st.session_state.students)}**")


# --------------------------------------------------------------- manage page
if page == "Manage Students":
    st.header("Manage Students")

    form_column, table_column = st.columns([1, 2], gap="large")

    with form_column:
        st.subheader("Student details")
        rolls = [student.roll_no for student in st.session_state.students]
        edit_choice = st.selectbox(
            "Edit an existing record (optional)", ["-- New student --", *rolls]
        )
        selected = next(
            (
                student
                for student in st.session_state.students
                if student.roll_no == edit_choice
            ),
            None,
        )
        key_suffix = edit_choice.replace(" ", "_")

        with st.form("student_form"):
            roll = st.text_input(
                "Roll No",
                value=selected.roll_no if selected else "",
                key=f"roll_{key_suffix}",
            )
            name = st.text_input(
                "Name", value=selected.name if selected else "", key=f"name_{key_suffix}"
            )
            marks = {}
            for subject in SUBJECTS:
                marks[subject] = st.number_input(
                    subject,
                    min_value=0,
                    max_value=100,
                    value=int(selected.marks[subject]) if selected else 0,
                    step=1,
                    key=f"{subject}_{key_suffix}",
                )
            submitted = st.form_submit_button(
                "Add / Update Student", width="stretch"
            )

        if submitted:
            student = Student(roll.strip(), name.strip(), marks)
            try:
                student.validate()
            except ValueError as error:
                st.error(str(error))
            else:
                remaining = [
                    item
                    for item in st.session_state.students
                    if item.roll_no.lower() != student.roll_no.lower()
                ]
                st.session_state.students = [*remaining, student]
                save_students()
                st.success(
                    f"Saved {student.name} — Grade {student.grade} ({student.result})"
                )

        st.divider()
        st.subheader("Delete / reset")
        if rolls:
            delete_choice = st.selectbox("Record to delete", rolls, key="delete_choice")
            if st.button("Delete selected record"):
                st.session_state.students = [
                    item
                    for item in st.session_state.students
                    if item.roll_no != delete_choice
                ]
                save_students()
                st.warning(f"Deleted {delete_choice}")

        if st.button("Load 12 sample students"):
            st.session_state.students = sample_students()
            save_students()
            st.success("Sample data loaded")

        confirmed = st.checkbox("I want to clear all records")
        if st.button("Clear all records", disabled=not confirmed):
            st.session_state.students = []
            save_students()
            st.warning("All records cleared")

    with table_column:
        st.subheader("Student records")
        query = st.text_input("Search by name or roll number")

        full_df = current_dataframe()
        visible_df = full_df
        if query.strip():
            needle = query.strip().lower()
            visible_df = full_df[
                full_df["Roll No"].str.lower().str.contains(needle, regex=False)
                | full_df["Name"].str.lower().str.contains(needle, regex=False)
            ]

        st.caption(
            f"Showing {len(visible_df)} of {len(st.session_state.students)} students"
        )
        if visible_df.empty:
            st.info("No records yet — add a student or load the sample data.")
        else:

            def colour_result(row: pd.Series) -> list[str]:
                colour = "#187a3a" if row["Result"] == "Pass" else "#c0392b"
                return [f"color: {colour}"] * len(row)

            st.dataframe(
                visible_df.style.apply(colour_result, axis=1),
                hide_index=True,
                width="stretch",
            )

        st.download_button(
            "⬇️ Download full report (CSV)",
            full_df.to_csv(index=False).encode("utf-8"),
            file_name="students_report.csv",
            mime="text/csv",
            width="stretch",
        )


# -------------------------------------------------------------- dashboard
elif page == "Dashboard":
    st.header("Class Dashboard")

    df = current_dataframe()
    stats = summarize(df)

    first, second, third, fourth = st.columns(4)
    first.metric("Students", stats["count"])
    second.metric("Class average", f"{stats['average']:.1f}" if stats["count"] else "-")
    third.metric("Topper", stats["topper"])
    fourth.metric(
        "Pass percentage", f"{stats['pass_percent']:.0f}%" if stats["count"] else "-"
    )

    st.subheader("Analytics (pandas + matplotlib)")
    st.pyplot(build_figure(df))

    with st.expander("View the data table"):
        st.dataframe(df, hide_index=True, width="stretch")


# ----------------------------------------------------- presentation guide
else:
    st.header("How to present this project")
    st.markdown(
        """
1. Open the **Manage Students** page — the 12 sample students are already loaded.
2. Pick **Anirudh** in *Edit an existing record* to show how marks are loaded into
   the form and how total, average, grade and result are calculated automatically.
3. Type a name in the search box to demonstrate live filtering.
4. Open the **Dashboard** page: explain the four summary cards and each chart
   (subject averages, grade distribution, histogram, top 5).
5. Add a new student with one mark below 33 — the row turns red (**Fail**) even if
   the average is good, which shows the pass rule.
6. Click **Download full report (CSV)** to demonstrate file handling/export.
"""
    )

    st.subheader("Rules used")
    st.markdown(
        """
- **Grade:** A+ ≥ 90, A ≥ 80, B+ ≥ 70, B ≥ 60, C ≥ 50, D ≥ 40, otherwise F.
- **Pass:** average ≥ 40 **and** every subject ≥ 33.
- **Roll No** is the unique key — adding an existing roll number updates that record.
"""
    )

    st.info(
        "Note: on a free public host the CSV is temporary and resets when the app "
        "restarts. Use **Download full report (CSV)** if you want to keep a copy."
    )
