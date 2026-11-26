"""Matplotlib charts that are embedded directly inside the Tkinter window.

Demonstrates: subplots, bar/pie/histogram charts, NumPy-style data handling
and GUI integration (Practicals 29 and 30).
"""

from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure

from .analytics import grade_counts, subject_averages, top_students


COLORS = ["#4F8BD6", "#57A773", "#EE964B", "#9B5DE5", "#F15BB5"]


def build_figure(df: pd.DataFrame) -> Figure:
    """Build a 2x2 dashboard figure from the class DataFrame."""
    figure = Figure(figsize=(11, 6.2), dpi=100)
    figure.patch.set_facecolor("#F7F9FC")
    grid = figure.add_gridspec(2, 2, hspace=0.48, wspace=0.32)

    # 1) Average mark per subject
    ax1 = figure.add_subplot(grid[0, 0])
    averages = subject_averages(df)
    ax1.bar(list(averages.keys()), list(averages.values()), color=COLORS)
    ax1.set_title("Average Marks by Subject")
    ax1.set_ylim(0, 100)
    ax1.tick_params(axis="x", rotation=20)
    ax1.grid(axis="y", alpha=0.3)

    # 2) Grade distribution (pie chart)
    ax2 = figure.add_subplot(grid[0, 1])
    counts = grade_counts(df)
    if counts:
        ax2.pie(
            list(counts.values()),
            labels=list(counts.keys()),
            autopct="%1.0f%%",
            startangle=140,
            colors=COLORS[: len(counts)],
        )
        ax2.set_title("Grade Distribution")
    else:
        ax2.text(0.5, 0.5, "No data yet", ha="center", va="center")
        ax2.set_title("Grade Distribution")

    # 3) Histogram of student averages
    ax3 = figure.add_subplot(grid[1, 0])
    if not df.empty:
        ax3.hist(df["Average"], bins=8, edgecolor="black", color="#4F8BD6")
    ax3.set_title("Distribution of Averages")
    ax3.set_xlabel("Average mark")
    ax3.set_ylabel("Students")
    ax3.grid(axis="y", alpha=0.3)

    # 4) Top 5 students (horizontal bar)
    ax4 = figure.add_subplot(grid[1, 1])
    top = top_students(df, 5)
    if not top.empty:
        ax4.barh(top["Name"][::-1], top["Average"][::-1], color="#57A773")
        ax4.set_xlim(0, 100)
    ax4.set_title("Top 5 Students")
    ax4.set_xlabel("Average mark")
    ax4.grid(axis="x", alpha=0.3)

    return figure
