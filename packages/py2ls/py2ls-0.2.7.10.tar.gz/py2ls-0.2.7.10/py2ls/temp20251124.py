#!/usr/bin/env python3
"""
Ultimate December Duty Package Generator
Generates:
 - Excel workbook: Calendar + AML rotation + CAR-T + Volunteers + TOIL log + Policy & Messages
 - Printable PDF schedule (calendar + assigned minimal duties + critical day highlights)
 - Policy PDF
 - Slack message text file
 - Email-to-PI text file
 - Fair rotation table CSV + PDF

Usage:
    python generate_december_duty_package.py --year 2025 --month 12 --vacation_csv vacations.csv

If vacation_csv omitted, sample vacation data will be used.

Author: Jeff's assistant (ultimate script)
"""
import argparse
from datetime import datetime, timedelta
import calendar
import pandas as pd
import numpy as np
import os
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from tabulate import tabulate

# ---------- CONFIG / DEFAULTS ----------
AML_ROTATION = ["L", "S", "A", "T", "N"]   # user-provided AML rotation order
CAR_T_MAIN = ["J"]                        # main CAR-T person(s)
CAR_T_BACKUP = ["TechnicianBackup"]       # replace with real name(s)

OUTPUT_DIR = "december_duty_output"
EXCEL_FILENAME = "December_Duty_Ultimate_Template.xlsx"
PDF_SCHEDULE_FILENAME = "December_Duty_Schedule.pdf"
POLICY_PDF_FILENAME = "December_Duty_Policy.pdf"
SLACK_FILENAME = "Slack_message_volunteers.txt"
PI_EMAIL_FILENAME = "Email_to_PI.txt"
ROTATION_CSV = "Fair_Rotation_Table.csv"
ROTATION_PDF = "Fair_Rotation_Table.pdf"

# TOIL rules
TOIL_SHORT_SHIFT = 0.5   # half-day for short minimal duty
TOIL_FULL_SHIFT = 1.0    # full day for full minimal duty
TOIL_VALIDITY_MONTHS = 3  # take TOIL within this many months

# Critical threshold: day is critical if available AML-trained staff <= threshold
CRITICAL_THRESHOLD = 1

# ---------- HELPERS ----------
def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return OUTPUT_DIR

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def read_vacations_csv(path):
    """
    Expected CSV format:
    name,start,end
    L,2025-12-20,2025-12-31
    S,2025-12-24,2025-12-26
    """
    df = pd.read_csv(path, parse_dates=["start", "end"])
    return df

# ---------- MAIN GENERATORS ----------
def build_calendar_df(year, month):
    start = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end = datetime(year, month, last_day)
    dates = pd.date_range(start=start, end=end)
    df = pd.DataFrame({
        "date": dates,
        "weekday": dates.strftime("%a"),
        "day": dates.day,
        "is_weekend": dates.weekday >= 5
    })
    df["public_holiday"] = False   # user can mark later
    df["avail_aml_count"] = np.nan
    df["critical_flag"] = False
    return df

def apply_vacations_to_calendar(calendar_df, vacations_df, aml_people, car_t_main, car_t_backup):
    """
    Mark who is available on each day from AML and CAR-T lists.
    vacations_df columns: name,start,end
    Return:
        calendar_df with columns 'available_aml' (list) and 'available_car_t'
    """
    cal = calendar_df.copy()
    cal["available_aml"] = [[] for _ in range(len(cal))]
    cal["available_car_t"] = [[] for _ in range(len(cal))]

    vac_periods = {}
    if vacations_df is not None:
        for _, row in vacations_df.iterrows():
            name = str(row["name"]).strip()
            vac_periods.setdefault(name, []).append((row["start"].to_pydatetime().date(),
                                                     row["end"].to_pydatetime().date()))

    for idx, row in cal.iterrows():
        d = row["date"].date()
        # AML people availability
        for p in aml_people:
            # if p has any vacation covering this date -> not available
            off = False
            for pr in vac_periods.get(p, []):
                if pr[0] <= d <= pr[1]:
                    off = True
                    break
            if not off:
                cal.at[idx, "available_aml"].append(p)
        # CAR-T main
        for p in car_t_main + car_t_backup:
            off = False
            for pr in vac_periods.get(p, []):
                if pr[0] <= d <= pr[1]:
                    off = True
                    break
            if not off:
                cal.at[idx, "available_car_t"].append(p)

        cal.at[idx, "avail_aml_count"] = len(cal.at[idx, "available_aml"])
        cal.at[idx, "critical_flag"] = cal.at[idx, "avail_aml_count"] <= CRITICAL_THRESHOLD
    return cal

def generate_aml_rotation_sheet(calendar_df, aml_people):
    """
    Create a suggested AML rotation "assigned order" repeating across the month.
    Note: AML arrival detection is event-driven; this is a queue, not day assignment.
    We generate a repeating sequence that can be used as "next responsible".
    """
    cal = calendar_df.copy()
    n = len(cal)
    seq = (aml_people * ((n // len(aml_people)) + 2))[:n]
    cal["assigned_next_in_queue"] = seq
    cal["actual_processed_by"] = ""
    cal["aml_notes"] = ""
    return cal[["date", "weekday", "day", "assigned_next_in_queue", "actual_processed_by", "aml_notes"]]

def create_excel(calendar_df, aml_sheet_df, car_t_df, volunteers_df, toil_log_df, messages_dict, policy_text):
    outdir = ensure_output_dir()
    out_path = os.path.join(outdir, EXCEL_FILENAME)
    writer = pd.ExcelWriter(out_path, engine="xlsxwriter", datetime_format="yyyy-mm-dd", date_format="yyyy-mm-dd")
    workbook = writer.book

    # Calendar sheet
    cal_w = calendar_df.copy()
    # Flatten available lists to strings for Excel view
    cal_w["available_aml"] = cal_w["available_aml"].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
    cal_w["available_car_t"] = cal_w["available_car_t"].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
    cal_w.to_excel(writer, sheet_name="Calendar_Dec", index=False)

    # AML rotation
    aml_sheet_df.to_excel(writer, sheet_name="AML_Rotation", index=False)

    # CAR-T sheet
    car_t_df.to_excel(writer, sheet_name="CAR-T", index=False)

    # Volunteers + TOIL
    volunteers_df.to_excel(writer, sheet_name="Volunteers", index=False)
    toil_log_df.to_excel(writer, sheet_name="TOIL_Log", index=False)

    # Messages and policy sheet as text
    # We write them into one sheet with wide column
    messages_df = pd.DataFrame({
        "type":["slack_message","email_to_pi","fair_rotation_rules","policy"],
        "content":[messages_dict["slack"], messages_dict["email"], messages_dict["fair_rotation"], policy_text]
    })
    messages_df.to_excel(writer, sheet_name="Messages_and_Policy", index=False)

    # Conditional formatting for critical days on calendar
    worksheet = writer.sheets["Calendar_Dec"]
    # find the row numbers for avail_aml_count and critical_flag (we wrote headers)
    # Use column indices by label:
    header = cal_w.columns.tolist()
    try:
        col_avail_idx = header.index("avail_aml_count")
        col_crit_idx = header.index("critical_flag")
    except ValueError:
        col_avail_idx = None
        col_crit_idx = None

    # Apply conditional format: highlight rows where critical_flag == True
    if col_crit_idx is not None:
        # Excel uses A1 notation; compute range
        row_count = len(cal_w)
        # columns start at A (0) -> +1 for Excel column. We'll color the avail_aml_count column to highlight.
        crit_col_letter = xlsx_colname(col_crit_idx + 1)
        # highlight True cells
        worksheet.conditional_format(f"{crit_col_letter}2:{crit_col_letter}{row_count+1}", {
            'type': 'cell',
            'criteria': 'equal to',
            'value': True,
            'format': workbook.add_format({'bg_color': '#FFC7CE'})  # light red
        })
    writer.close()
    return out_path

def xlsx_colname(col):
    """1-indexed column number -> Excel column letter"""
    string = ""
    while col > 0:
        col, remainder = divmod(col-1, 26)
        string = chr(65 + remainder) + string
    return string

def generate_car_t_sheet(calendar_df, car_t_main, car_t_backup):
    cal = calendar_df.copy()
    df = pd.DataFrame({
        "date": cal["date"],
        "weekday": cal["weekday"],
        "CAR-T_main": [", ".join(car_t_main)] * len(cal),
        "CAR-T_backup": [", ".join(car_t_backup)] * len(cal),
        "available_car_t_list": cal["available_car_t"].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
    })
    df["note"] = ""
    return df

def generate_volunteer_sheet(calendar_df):
    df = pd.DataFrame({
        "date": calendar_df["date"],
        "weekday": calendar_df["weekday"],
        "critical_day": calendar_df["critical_flag"],
        "volunteer_name": "",
        "volunteer_contact": "",
        "toil_days_granted": 0.0,
        "notes": ""
    })
    return df

def generate_toil_log():
    df = pd.DataFrame(columns=["name", "date_covered", "toil_days", "taken_YN", "notes"])
    return df

# ---------- PDF / textual exports ----------
def create_pdf_schedule(calendar_df, aml_sheet_df, volunteers_df, out_path):
    """
    Create a simple multi-page PDF schedule showing:
     - calendar with critical days highlighted
     - AML rotation table (assigned queue)
     - volunteer signups (if provided)
    """
    outdir = ensure_output_dir()
    pdf_path = os.path.join(outdir, out_path)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4))
    elements = []

    title = Paragraph("<b>December Duty Schedule</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Calendar table: date, weekday, avail_aml_count, available_aml, critical_flag
    cal = calendar_df.copy()
    cal['date_s'] = cal['date'].dt.strftime("%Y-%m-%d")
    cal_table = cal[["date_s", "weekday", "avail_aml_count", "available_aml", "critical_flag"]]
    cal_table = cal_table.fillna("")
    table_data = [cal_table.columns.tolist()] + cal_table.values.tolist()
    t = Table(table_data, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(Paragraph("<b>Calendar (availability & critical flags)</b>", styles['Heading2']))
    elements.append(t)
    elements.append(PageBreak())

    # AML rotation (short)
    aml = aml_sheet_df.copy()
    aml['date_s'] = aml['date'].dt.strftime("%Y-%m-%d")
    aml_table = aml[["date_s", "weekday", "assigned_next_in_queue", "actual_processed_by", "aml_notes"]]
    aml_table = aml_table.fillna("")
    t2 = Table([aml_table.columns.tolist()] + aml_table.values.tolist(), repeatRows=1)
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
    ]))
    elements.append(Paragraph("<b>AML Rotation (suggested queue)</b>", styles['Heading2']))
    elements.append(t2)
    elements.append(PageBreak())

    # Volunteers
    vol = volunteers_df.copy()
    if "date" in vol.columns:
        vol['date_s'] = vol['date'].dt.strftime("%Y-%m-%d")
    vol_table = vol[["date_s", "weekday", "critical_day", "volunteer_name", "toil_days_granted", "notes"]].fillna("")
    t3 = Table([vol_table.columns.tolist()] + vol_table.values.tolist(), repeatRows=1)
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
    ]))
    elements.append(Paragraph("<b>Volunteer Signups</b>", styles['Heading2']))
    elements.append(t3)

    doc.build(elements)
    return pdf_path

def create_policy_pdf(policy_text, out_path):
    outdir = ensure_output_dir()
    pdf_path = os.path.join(outdir, out_path)
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("<b>Holiday Season Duty Coverage Policy</b>", styles['Title']))
    elements.append(Spacer(1, 12))
    # split long policy into paragraphs by blank lines
    for chunk in policy_text.strip().split("\n\n"):
        elements.append(Paragraph(chunk.replace("\n", "<br/>"), styles['BodyText']))
        elements.append(Spacer(1, 8))
    doc.build(elements)
    return pdf_path

def save_plain_text_message(msg, filename):
    outdir = ensure_output_dir()
    p = os.path.join(outdir, filename)
    with open(p, "w", encoding="utf-8") as f:
        f.write(msg)
    return p

def export_rotation_csv_pdf(rotation_df, csv_name, pdf_name):
    outdir = ensure_output_dir()
    csv_path = os.path.join(outdir, csv_name)
    rotation_df.to_csv(csv_path, index=False)

    # quick PDF using matplotlib table
    pdf_path = os.path.join(outdir, pdf_name)
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape in inches
    ax.axis('off')
    tbl = ax.table(cellText=rotation_df.values, colLabels=rotation_df.columns, loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.2)
    plt.savefig(pdf_path, bbox_inches='tight')
    plt.close(fig)
    return csv_path, pdf_path

# ---------- FAIR ROTATION SUMMARY builder ----------
def build_fair_rotation_summary(aml_people, vacation_df, processed_history=None):
    """
    processed_history: optional dict name->count of AML duties already done in the year
    """
    if processed_history is None:
        processed_history = {p: 0 for p in aml_people}
    rows = []
    for p in aml_people:
        vac_periods = []
        if vacation_df is not None:
            subset = vacation_df[vacation_df["name"] == p]
            for _, r in subset.iterrows():
                vac_periods.append(f"{r['start'].date()}->{r['end'].date()}")
        rows.append({
            "Person": p,
            "AML_trained": True,
            "CAR-T_trained": p in CAR_T_MAIN,
            "Vacations_in_Dec": "; ".join(vac_periods),
            "AML_duties_completed_YTD": processed_history.get(p, 0),
            "Rotation_position_estimate": ""  # could be computed
        })
    df = pd.DataFrame(rows)
    return df

# ---------- SAMPLE / CLI ----------
SAMPLE_VACATIONS = pd.DataFrame([
    {"name": "S", "start": pd.Timestamp("2025-12-20"), "end": pd.Timestamp("2025-12-31")},
    {"name": "N", "start": pd.Timestamp("2025-12-24"), "end": pd.Timestamp("2025-12-26")},
    {"name": "T", "start": pd.Timestamp("2025-12-10"), "end": pd.Timestamp("2025-12-12")},
    # J (CAR-T) maybe off:
    {"name": "J", "start": pd.Timestamp("2025-12-25"), "end": pd.Timestamp("2025-12-26")},
])

SLACK_MESSAGE_TEMPLATE = """Hi everyone,
as we approach the December holiday period, several days currently have limited staff available for AML sample duty and general lab coverage.

To ensure essential tasks are covered fairly, I kindly ask for volunteers to cover a few minimal-coverage shifts (mainly AML sample duty). These shifts apply ONLY if a sample actually arrives on that day, and volunteers will receive Freizeitausgleich (time-off in lieu) for their support.

If you can cover one of the critical staffing days, please add your name in the Volunteers sheet in the shared Excel file.
Please indicate your preferred TOIL arrangement (half-day or full-day).
If you already have approved vacation, you do not need to volunteer.

Thank you — your help keeps the lab functioning smoothly and fairly over the holidays.
— Jeff
"""

EMAIL_TO_PI_TEMPLATE = """Subject: December AML/CAR-T Duty Coverage – Request for Decision on Fully Staffed-Out Days

Dear Claudia,

I have prepared a draft December duty schedule for AML samples, CAR-T samples, and essential lab tasks. Several team members have approved vacation days, and for the following dates we currently have no AML-trained personnel available:

[see attached schedule]

Since colleagues on approved vacation cannot be required to perform sample duties, we need a PI-level decision for the affected dates. Preferred options:
1) Pause research AML sample processing on those dates.
2) Request voluntary backup support from clinical/diagnostic colleagues (with Freizeitausgleich).
3) Designate a PI-decided fallback person to be on-site for those dates (with compensation as applicable).

Please let me know your preferred option and I will finalize the schedule accordingly.

Kind regards,
Jeff
"""

FAIR_ROTATION_TEXT = """Fair Rotation Rules (Ultimate Version):
1. Equal Opportunities: Each AML-trained person should have approximately the same number of duty opportunities over a long-term window.
2. Vacation Exemption: Staff on approved vacation are excluded from rotation during those dates.
3. Worked Duty Counts: Rotation credit only counts when a person actually processes a sample.
4. Automatic Forward Rotation: If Person A processed the last sample, the next sample goes to Person B.
5. Volunteer Bonus: Volunteers on critical days receive TOIL and +1 rotation credit.
6. Emergency Handling: If no one is available, PI decides whether to pause processing or appoint a fallback person.
7. CAR-T Special Rule: CAR-T duties are restricted to qualified staff; both primary + backup unavailable -> escalate to PI.
"""

POLICY_TEXT = f"""
Holiday Season Duty Coverage Policy – AML, CAR-T, and Essential Lab Work
Version: 1.0
Applies to: Your Lab
Period: December 1 – January 7 each year

Purpose:
This document outlines how essential laboratory tasks and sample processing (AML, CAR-T, animals, general duties) are maintained during the holiday period in a fair, transparent, and legally compliant manner.

Key Principles:
- Vacation protection: Staff on approved vacation are exempt from duties during their approved dates.
- Fair rotation: AML duties assigned using a sequential rotation; duty counts only when actually performed.
- Volunteer system: Critical days covered by volunteers, compensated with Freizeitausgleich (time-off in lieu).
- No forced assignments: No one is required to cancel approved leave.
- PI decision for extreme cases: If no one is available, PI decides between pausing processing or appointing a fallback.
- Documentation: All volunteers and TOIL entries are recorded.

TOIL Guidelines:
- Short minimal duty (few hours) => 0.5 day TOIL.
- Full day minimal duty => 1.0 day TOIL.
- TOIL should be taken within {TOIL_VALIDITY_MONTHS} months unless otherwise approved.
"""

def main(year, month, vacations_csv=None, aml_people=None, car_t_main=None, car_t_backup=None):
    if aml_people is None:
        aml_people = AML_ROTATION.copy()
    if car_t_main is None:
        car_t_main = CAR_T_MAIN.copy()
    if car_t_backup is None:
        car_t_backup = CAR_T_BACKUP.copy()

    if vacations_csv and os.path.exists(vacations_csv):
        vacations_df = read_vacations_csv(vacations_csv)
    else:
        vacations_df = SAMPLE_VACATIONS

    cal_df = build_calendar_df(year, month)
    cal_df = apply_vacations_to_calendar(cal_df, vacations_df, aml_people, car_t_main, car_t_backup)

    aml_sheet = generate_aml_rotation_sheet(cal_df, aml_people)
    car_t_sheet = generate_car_t_sheet(cal_df, car_t_main, car_t_backup)
    volunteers_sheet = generate_volunteer_sheet(cal_df)
    toil_log = generate_toil_log()

    messages = {
        "slack": SLACK_MESSAGE_TEMPLATE,
        "email": EMAIL_TO_PI_TEMPLATE,
        "fair_rotation": FAIR_ROTATION_TEXT
    }

    # create Excel
    excel_path = create_excel(cal_df, aml_sheet, car_t_sheet, volunteers_sheet, toil_log, messages, POLICY_TEXT)
    print(f"Excel file written to: {excel_path}")

    # create PDF schedule
    pdf_path = create_pdf_schedule(cal_df, aml_sheet, volunteers_sheet, PDF_SCHEDULE_FILENAME)
    print(f"Schedule PDF written to: {pdf_path}")

    # create policy PDF
    policy_pdf_path = create_policy_pdf(POLICY_TEXT, POLICY_PDF_FILENAME)
    print(f"Policy PDF written to: {policy_pdf_path}")

    # plain text messages
    slack_txt = save_plain_text_message(SLACK_MESSAGE_TEMPLATE, SLACK_FILENAME)
    email_txt = save_plain_text_message(EMAIL_TO_PI_TEMPLATE, PI_EMAIL_FILENAME)
    print(f"Slack message text saved to: {slack_txt}")
    print(f"Email-to-PI text saved to: {email_txt}")

    # fair rotation table
    rotation_summary = build_fair_rotation_summary(aml_people, vacations_df)
    csv_path, pdf_rot_path = export_rotation_csv_pdf(rotation_summary, ROTATION_CSV, ROTATION_PDF)
    print(f"Fair rotation CSV: {csv_path}")
    print(f"Fair rotation PDF: {pdf_rot_path}")

    print("All outputs generated in folder:", ensure_output_dir())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate December duty package")
    parser.add_argument("--year", type=int, default=2025, help="Year (default 2025)")
    parser.add_argument("--month", type=int, default=12, help="Month (1-12) default 12")
    parser.add_argument("--vacation_csv", type=str, default=None, help="Optional vacations CSV path")
    parser.add_argument("--excel_out", type=str, default=None, help="Optional excel output name")
    args = parser.parse_args()
    main(args.year, args.month, vacations_csv=args.vacation_csv)