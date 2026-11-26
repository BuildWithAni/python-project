# Student Report Card System

A Python GUI mini-project that manages student marks, calculates grades automatically,
saves records to a CSV file, and shows an analytics dashboard with charts.

Built by **Anirudh** (BTech CSE, Section A, Roll No 24011001007) — Hindu College of
Engineering, Sonipat.

**Live web demo:** _add your Streamlit link here after deploying (see DEPLOY.md)_.

## Two ways to run it

- **Desktop GUI:** `python main.py` (Tkinter)
- **Web app / shareable link:** `streamlit run streamlit_app.py`, then follow
  [DEPLOY.md](DEPLOY.md) to put it online for free.

## Features

- **Manage students:** add, update, delete and clear records through a form + table.
- **Automatic grading:** total, average, grade and pass/fail are calculated for you.
- **Search:** filter the table by name or roll number as you type.
- **CSV persistence:** records are saved in `data/students.csv` and can be exported.
- **Dashboard:** Pandas summary cards (class average, topper, pass %) and four
  Matplotlib charts embedded in the GUI (subject averages, grade distribution,
  histogram of averages, top 5 students).
- **Sample data:** 12 ready-made students are included so the app looks alive on
  first run; `File > Load Sample Data` restores them at any time.
- **Validation:** marks must be numbers between 0 and 100, roll numbers are unique,
  and friendly dialogs explain any mistake.

## How to run

```bash
pip install -r requirements.txt
python main.py
```

Requires Python 3.10+ (tested on 3.12). Tkinter comes with Python on Windows; on
Linux you may need `sudo apt install python3-tk`.

Run the unit tests with:

```bash
python -m unittest discover -s tests -v
```

## 2-minute classroom demo

1. Start the app with `python main.py` — 12 sample students are already loaded.
2. On the **Manage Students** tab, double-click **Anirudh** to load his marks into
   the form; point out that average/grade/result are computed automatically.
3. Type `Diya` in the search box to show live filtering, then click **Show All**.
4. Switch to the **Dashboard** tab: explain the Pandas summary cards and each chart.
5. Add a new student with one mark below 33 — the row turns red (**Fail**) even if
   the average is high, showing the pass rule in action.
6. Use **File > Export CSV As...** to demonstrate file handling, and
   **Save Chart As PNG...** to show the chart can be saved.

## Project structure

```text
python-project/
├── main.py                 # desktop entry point: python main.py
├── streamlit_app.py        # web version: streamlit run streamlit_app.py
├── requirements.txt        # pandas, matplotlib, numpy, streamlit
├── DEPLOY.md               # steps to get a free public link
├── data/
│   └── students.csv        # saved records (12 sample students included)
├── src/
│   ├── models.py           # Student dataclass, grading rules, validation
│   ├── storage.py          # CSV read/write with csv + pathlib
│   ├── analytics.py        # pandas DataFrame, aggregation and statistics
│   ├── charts.py           # matplotlib figures for the dashboard
│   ├── sample_data.py      # sample records shared by both versions
│   └── gui.py              # Tkinter windows, form, table, menus, events
└── tests/
    └── test_core.py        # 8 unit tests for models, storage and analytics
```

## How this connects to your practical file

| Practical(s) | Where it is used here |
| --- | --- |
| 01 Variables & data types | `SUBJECTS` tuple, marks dictionary, student objects |
| 04 If-else | grade scale and pass/fail decision in `models.py` |
| 05 Loops | form creation, table population, CSV writing |
| 07 Functions / 08 Arguments | small helper functions with default arguments |
| 09 Lists / 12 Dictionaries | `students` list, `to_row()` dictionaries |
| 13 List/string to dict | `dict(zip(SUBJECTS, marks))` in `sample_students()` |
| 15 Comprehensions / lambdas | filtering students, building rows |
| 19-21 File handling & CSV | `StudentRepository` saves/loads `students.csv` |
| 22 os/sys modules | `pathlib` paths and folder creation |
| 27-28 Pandas | `to_dataframe()`, `summarize()`, sorting, value counts |
| 29 Matplotlib | four charts in `charts.py` |
| 30 Tkinter GUI | the whole `gui.py` module |

## Rules used

- **Grade:** A+ ≥ 90, A ≥ 80, B+ ≥ 70, B ≥ 60, C ≥ 50, D ≥ 40, otherwise F.
- **Pass:** average ≥ 40 **and** every subject ≥ 33.
- **Roll No** is the unique key: adding an existing roll number updates that record.
