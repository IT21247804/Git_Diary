import os
import re
import csv
from collections import defaultdict
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet

# Authors to include
TARGET_AUTHORS = {
    "Baddewithana P",
    "Pasan Baddewithana"
}

INPUT_FOLDER = "git_histories"

all_commits = []
daily_summary = defaultdict(lambda: defaultdict(list))

# Read all repository files
for filename in os.listdir(INPUT_FOLDER):

    if not filename.endswith(".txt"):
        continue

    repo_name = os.path.splitext(filename)[0]

    filepath = os.path.join(INPUT_FOLDER, filename)

    with open(filepath, "r", encoding="utf-16") as f:

        for line in f:

            line = line.strip()

            match = re.match(
                r"(\d{4}-\d{2}-\d{2}) \| (.*?): (.*)",
                line
            )

            if not match:
                continue

            date, author, commit = match.groups()

            if author not in TARGET_AUTHORS:
                continue

            all_commits.append([
                date,
                repo_name,
                commit
            ])

            daily_summary[date][repo_name].append(commit)

# Sort by date
all_commits.sort(key=lambda x: (x[0], x[1]))

# --------------------------------------------------
# Detailed CSV
# --------------------------------------------------

with open(
    "Detailed_Work_Log.csv",
    "w",
    newline="",
    encoding="utf-8"
) as csvfile:

    writer = csv.writer(csvfile)

    writer.writerow([
        "Date",
        "Repository",
        "Commit"
    ])

    writer.writerows(all_commits)

print("Detailed CSV generated.")

# --------------------------------------------------
# Diary CSV
# --------------------------------------------------

with open(
    "Daily_Diary.csv",
    "w",
    newline="",
    encoding="utf-8"
) as csvfile:

    writer = csv.writer(csvfile)

    writer.writerow([
        "Date",
        "Work Summary"
    ])

    for date in sorted(daily_summary.keys()):

        summary_parts = []

        for repo in sorted(daily_summary[date].keys()):

            commits = daily_summary[date][repo]

            summary_parts.append(
                f"{repo}: " +
                "; ".join(commits)
            )

        writer.writerow([
            date,
            " | ".join(summary_parts)
        ])

print("Diary CSV generated.")

# --------------------------------------------------
# PDF Diary
# --------------------------------------------------

pdf = SimpleDocTemplate(
    "Work_Diary.pdf"
)

styles = getSampleStyleSheet()

elements = []

elements.append(
    Paragraph(
        "Software Development Work Diary",
        styles["Title"]
    )
)

elements.append(Spacer(1, 12))

for date in sorted(daily_summary.keys(), reverse=True):

    elements.append(
        Paragraph(
            f"<b>{date}</b>",
            styles["Heading2"]
        )
    )

    for repo in sorted(daily_summary[date].keys()):

        elements.append(
            Paragraph(
                f"<b>{repo}</b>",
                styles["Heading3"]
            )
        )

        for commit in daily_summary[date][repo]:

            elements.append(
                Paragraph(
                    f"• {commit}",
                    styles["BodyText"]
                )
            )

        elements.append(
            Spacer(1, 6)
        )

    elements.append(
        Spacer(1, 12)
    )

pdf.build(elements)

print("PDF diary generated.")