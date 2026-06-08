"""
╔══════════════════════════════════════════════════════════╗
║         🎓  STUDENT MANAGEMENT SYSTEM  🎓                ║
║         Full-featured academic records manager           ║
╚══════════════════════════════════════════════════════════╝

Features:
  • Register / update / delete students
  • Assign subjects and record grades
  • Calculate GPA and generate report cards
  • Attendance tracking
  • Fee management
  • Search & filter students
  • Class-wise and subject-wise statistics
  • Top performers leaderboard
"""

import datetime
import random
import statistics

SEPARATOR  = "═" * 60
THIN_LINE  = "─" * 60
NEXT_ID    = [1001]          # mutable default so helpers can increment

# ── in-memory stores ──────────────────────────────────────
students    = {}   # {sid: {...}}
subjects    = {}   # {code: {name, teacher, credits}}
attendance  = {}   # {sid: {date: "P"/"A"/"L"}}
fees        = {}   # {sid: [{desc, amount, paid, date}]}

# ── grade scale ───────────────────────────────────────────
GRADE_SCALE = [
    (90, "A+", 4.0), (80, "A",  3.7), (75, "A-", 3.5),
    (70, "B+", 3.3), (65, "B",  3.0), (60, "B-", 2.7),
    (55, "C+", 2.3), (50, "C",  2.0), (45, "C-", 1.7),
    (40, "D",  1.0), (0,  "F",  0.0),
]

CLASSES = ["Grade 9", "Grade 10", "Grade 11", "Grade 12"]


# ════════════════════════════════════════════════════════════
#   UTILITY HELPERS
# ════════════════════════════════════════════════════════════

def today():
    return datetime.date.today().strftime("%Y-%m-%d")


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def header(title):
    print(f"\n{SEPARATOR}")
    print(f"  🎓  {title}")
    print(SEPARATOR)


def section(title):
    print(f"\n{THIN_LINE}")
    print(f"  {title}")
    print(THIN_LINE)


def pause():
    input("\n  ↩  Press Enter to continue...")


def new_id():
    sid = NEXT_ID[0]
    NEXT_ID[0] += 1
    return sid


def score_to_grade(score):
    for minimum, letter, points in GRADE_SCALE:
        if score >= minimum:
            return letter, points
    return "F", 0.0


def gpa_from_grades(grade_map, subject_codes):
    """Weighted GPA using subject credits."""
    total_pts = total_credits = 0
    for code in subject_codes:
        if code in grade_map and code in subjects:
            _, gp = score_to_grade(grade_map[code])
            cr    = subjects[code]["credits"]
            total_pts    += gp * cr
            total_credits += cr
    if total_credits == 0:
        return 0.0
    return round(total_pts / total_credits, 2)


def bar(value, maximum, width=20):
    filled = int((value / maximum) * width) if maximum else 0
    return "█" * filled + "░" * (width - filled)


def pct(part, whole):
    return f"{(part/whole*100):.1f}%" if whole else "N/A"


# ════════════════════════════════════════════════════════════
#   SUBJECT MANAGEMENT
# ════════════════════════════════════════════════════════════

def add_subject():
    header("ADD SUBJECT")
    code    = input("  Subject Code  (e.g. MATH101): ").strip().upper()
    if not code:
        print("  ❌  Code required."); return
    if code in subjects:
        print("  ❌  Subject already exists."); return
    name    = input("  Subject Name  : ").strip()
    teacher = input("  Teacher Name  : ").strip()
    cr_raw  = input("  Credits (1-4) : ").strip()
    if not cr_raw.isdigit() or not (1 <= int(cr_raw) <= 4):
        print("  ❌  Credits must be 1-4."); return
    subjects[code] = {"name": name, "teacher": teacher, "credits": int(cr_raw)}
    print(f"  ✅  Subject '{name}' ({code}) added.")
    pause()


def list_subjects():
    header("ALL SUBJECTS")
    if not subjects:
        print("  No subjects defined yet."); pause(); return
    print(f"\n  {'Code':<10} {'Name':<25} {'Teacher':<20} Credits")
    print(f"  {THIN_LINE}")
    for code, s in subjects.items():
        print(f"  {code:<10} {s['name']:<25} {s['teacher']:<20} {s['credits']}")
    pause()


# ════════════════════════════════════════════════════════════
#   STUDENT REGISTRATION
# ════════════════════════════════════════════════════════════

def register_student():
    header("REGISTER STUDENT")
    name   = input("  Full Name     : ").strip()
    if not name:
        print("  ❌  Name required."); return
    age_r  = input("  Age           : ").strip()
    if not age_r.isdigit():
        print("  ❌  Invalid age."); return
    gender = input("  Gender (M/F/O): ").strip().upper()
    if gender not in ("M","F","O"):
        print("  ❌  Enter M, F, or O."); return
    print(f"\n  Classes: {', '.join(f'[{i+1}] {c}' for i,c in enumerate(CLASSES))}")
    ci = input("  Select class  : ").strip()
    if not ci.isdigit() or not (1 <= int(ci) <= len(CLASSES)):
        print("  ❌  Invalid class."); return
    cls      = CLASSES[int(ci)-1]
    email    = input("  Email         : ").strip()
    phone    = input("  Phone         : ").strip()
    guardian = input("  Guardian Name : ").strip()

    sid = new_id()
    students[sid] = {
        "name":     name,
        "age":      int(age_r),
        "gender":   gender,
        "class":    cls,
        "email":    email,
        "phone":    phone,
        "guardian": guardian,
        "enrolled": today(),
        "grades":   {},    # {subject_code: score}
        "subjects": [],    # enrolled subject codes
    }
    fees[sid]       = []
    attendance[sid] = {}

    print(f"\n  ✅  Student registered!")
    print(f"  📋  Student ID : S-{sid}")
    pause()


def update_student():
    header("UPDATE STUDENT")
    sid = _ask_sid()
    if sid is None: return
    s = students[sid]
    print(f"\n  Editing: {s['name']} (S-{sid})")
    print("  Leave blank to keep current value.\n")

    new_name  = input(f"  Name     [{s['name']}]     : ").strip()
    new_email = input(f"  Email    [{s['email']}]    : ").strip()
    new_phone = input(f"  Phone    [{s['phone']}]    : ").strip()
    new_gdn   = input(f"  Guardian [{s['guardian']}]: ").strip()

    if new_name:  s["name"]     = new_name
    if new_email: s["email"]    = new_email
    if new_phone: s["phone"]    = new_phone
    if new_gdn:   s["guardian"] = new_gdn
    print("  ✅  Record updated.")
    pause()


def delete_student():
    header("DELETE STUDENT")
    sid = _ask_sid()
    if sid is None: return
    confirm = input(f"  Delete {students[sid]['name']} (S-{sid})? (yes/no): ").strip().lower()
    if confirm in ("yes","y"):
        del students[sid]
        fees.pop(sid, None)
        attendance.pop(sid, None)
        print("  ✅  Student removed.")
    else:
        print("  ↩  Cancelled.")
    pause()


# ════════════════════════════════════════════════════════════
#   SUBJECT ENROLMENT & GRADES
# ════════════════════════════════════════════════════════════

def enrol_subject():
    header("ENROL STUDENT IN SUBJECT")
    sid = _ask_sid()
    if sid is None: return
    if not subjects:
        print("  ❌  No subjects defined."); pause(); return
    s = students[sid]
    list_subjects()
    code = input("  Subject Code  : ").strip().upper()
    if code not in subjects:
        print("  ❌  Subject not found."); pause(); return
    if code in s["subjects"]:
        print("  ⚠️  Already enrolled."); pause(); return
    s["subjects"].append(code)
    print(f"  ✅  {s['name']} enrolled in {subjects[code]['name']}.")
    pause()


def enter_grades():
    header("ENTER / UPDATE GRADES")
    sid = _ask_sid()
    if sid is None: return
    s = students[sid]
    if not s["subjects"]:
        print("  ❌  Student not enrolled in any subject."); pause(); return
    print(f"\n  Enrolled subjects for {s['name']}:")
    for code in s["subjects"]:
        current = s["grades"].get(code, "–")
        print(f"    {code:<10} {subjects[code]['name']:<25}  Current score: {current}")
    print()
    for code in s["subjects"]:
        raw = input(f"  Score for {code} (0-100, Enter to skip): ").strip()
        if raw == "": continue
        if not raw.isdigit() or not (0 <= int(raw) <= 100):
            print(f"  ⚠️  Invalid score for {code}, skipped.")
            continue
        s["grades"][code] = int(raw)
    print("  ✅  Grades saved.")
    pause()


# ════════════════════════════════════════════════════════════
#   REPORT CARD
# ════════════════════════════════════════════════════════════

def print_report_card():
    header("STUDENT REPORT CARD")
    sid = _ask_sid()
    if sid is None: return
    s = students[sid]

    print(f"\n{'═'*56}")
    print(f"  {'REPORT CARD':^52}")
    print(f"  {'─'*52}")
    print(f"  Name      : {s['name']:<30}  ID  : S-{sid}")
    print(f"  Class     : {s['class']:<30}  Age : {s['age']}")
    print(f"  Enrolled  : {s['enrolled']}")
    print(f"  {'─'*52}")
    print(f"  {'Subject':<20} {'Score':>6}  {'Grade':>5}  {'Points':>6}  Credits")
    print(f"  {'─'*52}")

    if not s["subjects"]:
        print("  No subjects enrolled.")
    else:
        for code in s["subjects"]:
            sub   = subjects.get(code, {"name": code, "credits": 1})
            score = s["grades"].get(code)
            if score is None:
                print(f"  {sub['name']:<20} {'–':>6}  {'–':>5}  {'–':>6}  {sub['credits']}")
            else:
                ltr, gp = score_to_grade(score)
                print(f"  {sub['name']:<20} {score:>6}  {ltr:>5}  {gp:>6.1f}  {sub['credits']}")

        gpa = gpa_from_grades(s["grades"], s["subjects"])
        scored = {c: s["grades"][c] for c in s["subjects"] if c in s["grades"]}
        avg = round(statistics.mean(scored.values()), 1) if scored else 0

        print(f"  {'─'*52}")
        print(f"  Average Score : {avg}")
        print(f"  GPA           : {gpa:.2f} / 4.00")

        # attendance summary
        att = attendance.get(sid, {})
        total_days = len(att)
        present    = sum(1 for v in att.values() if v == "P")
        att_pct    = pct(present, total_days)
        print(f"  Attendance    : {present}/{total_days} days ({att_pct})")

        # fee status
        bill = fees.get(sid, [])
        outstanding = sum(f["amount"] for f in bill if not f["paid"])
        print(f"  Outstanding   : ${outstanding:.2f}")

    print(f"{'═'*56}")
    pause()


# ════════════════════════════════════════════════════════════
#   ATTENDANCE
# ════════════════════════════════════════════════════════════

def mark_attendance():
    header("MARK ATTENDANCE")
    date = input(f"  Date (YYYY-MM-DD) [today={today()}]: ").strip() or today()
    section(f"Marking attendance for {date}")
    if not students:
        print("  No students."); pause(); return

    for sid, s in students.items():
        while True:
            mark = input(f"  {s['name']:<25} (P=Present / A=Absent / L=Leave): ").strip().upper()
            if mark in ("P","A","L"):
                attendance[sid][date] = mark
                break
            print("  ⚠️  Enter P, A, or L.")
    print("  ✅  Attendance saved.")
    pause()


def view_attendance():
    header("VIEW ATTENDANCE")
    sid = _ask_sid()
    if sid is None: return
    s   = students[sid]
    att = attendance.get(sid, {})

    print(f"\n  Attendance for {s['name']} (S-{sid})\n")
    if not att:
        print("  No attendance records."); pause(); return

    for date in sorted(att):
        symbol = {"P": "✅", "A": "❌", "L": "🟡"}[att[date]]
        print(f"  {date}  {symbol}  {att[date]}")

    total   = len(att)
    present = sum(1 for v in att.values() if v == "P")
    absent  = sum(1 for v in att.values() if v == "A")
    leave   = sum(1 for v in att.values() if v == "L")
    print(f"\n  Total: {total}  Present: {present}  Absent: {absent}  Leave: {leave}")
    print(f"  Attendance Rate: {pct(present, total)}")
    pause()


# ════════════════════════════════════════════════════════════
#   FEE MANAGEMENT
# ════════════════════════════════════════════════════════════

def add_fee():
    header("ADD FEE")
    sid = _ask_sid()
    if sid is None: return
    desc   = input("  Description   : ").strip()
    amt_r  = input("  Amount ($)    : ").strip()
    try:
        amt = float(amt_r)
        assert amt > 0
    except:
        print("  ❌  Invalid amount."); return
    fees[sid].append({"desc": desc, "amount": amt, "paid": False, "date": today()})
    print(f"  ✅  Fee of ${amt:.2f} added for {students[sid]['name']}.")
    pause()


def pay_fee():
    header("MARK FEE AS PAID")
    sid = _ask_sid()
    if sid is None: return
    bill = fees.get(sid, [])
    unpaid = [(i, f) for i, f in enumerate(bill) if not f["paid"]]
    if not unpaid:
        print("  ✅  No outstanding fees."); pause(); return
    print(f"\n  Unpaid fees for {students[sid]['name']}:\n")
    for i, f in unpaid:
        print(f"   [{i}] {f['date']}  {f['desc']:<28} ${f['amount']:.2f}")
    idx_r = input("\n  Enter index to mark as paid: ").strip()
    if idx_r.isdigit() and int(idx_r) < len(bill):
        bill[int(idx_r)]["paid"] = True
        print("  ✅  Fee marked as paid.")
    else:
        print("  ❌  Invalid index.")
    pause()


def fee_summary():
    header("FEE SUMMARY")
    sid = _ask_sid()
    if sid is None: return
    bill = fees.get(sid, [])
    print(f"\n  Fees for {students[sid]['name']} (S-{sid})\n")
    if not bill:
        print("  No fee records."); pause(); return
    total = paid_total = 0
    for f in bill:
        status = "✅ Paid" if f["paid"] else "❌ Due"
        print(f"  {f['date']}  {f['desc']:<28} ${f['amount']:.2f}  {status}")
        total += f["amount"]
        if f["paid"]: paid_total += f["amount"]
    print(f"\n  Total Billed   : ${total:.2f}")
    print(f"  Total Paid     : ${paid_total:.2f}")
    print(f"  Outstanding    : ${total - paid_total:.2f}")
    pause()


# ════════════════════════════════════════════════════════════
#   SEARCH & FILTER
# ════════════════════════════════════════════════════════════

def search_students():
    header("SEARCH STUDENTS")
    print("  [1] By Name   [2] By Class   [3] By Subject")
    opt = input("  Option: ").strip()
    results = []

    if opt == "1":
        q = input("  Name contains: ").strip().lower()
        results = [(sid, s) for sid, s in students.items() if q in s["name"].lower()]
    elif opt == "2":
        print(f"  Classes: {', '.join(f'[{i+1}] {c}' for i,c in enumerate(CLASSES))}")
        ci = input("  Select: ").strip()
        if ci.isdigit() and 1 <= int(ci) <= len(CLASSES):
            cls = CLASSES[int(ci)-1]
            results = [(sid, s) for sid, s in students.items() if s["class"] == cls]
    elif opt == "3":
        code = input("  Subject Code: ").strip().upper()
        results = [(sid, s) for sid, s in students.items() if code in s["subjects"]]
    else:
        print("  ❌  Invalid option."); pause(); return

    if not results:
        print("  No students found."); pause(); return

    print(f"\n  Found {len(results)} student(s):\n")
    print(f"  {'ID':<8} {'Name':<22} {'Class':<12} {'GPA'}")
    print(f"  {THIN_LINE}")
    for sid, s in results:
        gpa = gpa_from_grades(s["grades"], s["subjects"])
        print(f"  S-{sid:<6} {s['name']:<22} {s['class']:<12} {gpa:.2f}")
    pause()


def list_all_students():
    header("ALL STUDENTS")
    if not students:
        print("  No students registered."); pause(); return
    print(f"\n  {'ID':<8} {'Name':<22} {'Age':<5} {'Class':<12} {'Enrolled':<12} {'GPA'}")
    print(f"  {THIN_LINE}")
    for sid, s in students.items():
        gpa = gpa_from_grades(s["grades"], s["subjects"])
        print(f"  S-{sid:<6} {s['name']:<22} {s['age']:<5} {s['class']:<12} {s['enrolled']:<12} {gpa:.2f}")
    print(f"\n  Total: {len(students)} students")
    pause()


# ════════════════════════════════════════════════════════════
#   STATISTICS & LEADERBOARD
# ════════════════════════════════════════════════════════════

def class_statistics():
    header("CLASS STATISTICS")
    if not students:
        print("  No data."); pause(); return
    for cls in CLASSES:
        cls_students = [(sid, s) for sid, s in students.items() if s["class"] == cls]
        if not cls_students: continue
        gpas = [gpa_from_grades(s["grades"], s["subjects"]) for _, s in cls_students]
        avg_gpa = round(statistics.mean(gpas), 2) if gpas else 0
        print(f"\n  {cls}")
        print(f"  Students : {len(cls_students)}")
        print(f"  Avg GPA  : {avg_gpa:.2f}  [{bar(avg_gpa, 4.0)}]")
    pause()


def subject_statistics():
    header("SUBJECT STATISTICS")
    if not subjects:
        print("  No subjects."); pause(); return
    for code, sub in subjects.items():
        scores = [s["grades"][code] for s in students.values()
                  if code in s["grades"]]
        if not scores:
            print(f"\n  {sub['name']} ({code}) — No scores yet")
            continue
        avg = round(statistics.mean(scores), 1)
        hi  = max(scores)
        lo  = min(scores)
        print(f"\n  {sub['name']:<25} ({code})")
        print(f"  Students graded : {len(scores)}")
        print(f"  Average : {avg}   High : {hi}   Low : {lo}")
        print(f"  [{bar(avg, 100, 30)}] {avg}/100")
    pause()


def top_performers():
    header("🏆  TOP PERFORMERS")
    if not students:
        print("  No students."); pause(); return
    ranked = []
    for sid, s in students.items():
        gpa = gpa_from_grades(s["grades"], s["subjects"])
        ranked.append((sid, s["name"], s["class"], gpa))
    ranked.sort(key=lambda x: x[3], reverse=True)
    print(f"\n  {'#':<4} {'Name':<22} {'Class':<12} {'GPA':<6}  Bar")
    print(f"  {THIN_LINE}")
    medals = ["🥇","🥈","🥉"]
    for i, (sid, name, cls, gpa) in enumerate(ranked[:10], 1):
        m = medals[i-1] if i <= 3 else f" {i}."
        print(f"  {m:<4} {name:<22} {cls:<12} {gpa:<6.2f} [{bar(gpa, 4.0, 15)}]")
    pause()


# ════════════════════════════════════════════════════════════
#   SEED DEMO DATA
# ════════════════════════════════════════════════════════════

def seed_demo():
    """Populate with sample subjects and students for quick testing."""
    demo_subjects = [
        ("MATH101", "Mathematics",  "Mr. Perera",  4),
        ("SCI101",  "Science",      "Ms. Fernando",3),
        ("ENG101",  "English",      "Mrs. Silva",  3),
        ("HIS101",  "History",      "Mr. Jayawardena", 2),
        ("ICT101",  "ICT",          "Ms. Wijeratne",3),
    ]
    for code, name, teacher, cr in demo_subjects:
        subjects[code] = {"name": name, "teacher": teacher, "credits": cr}

    demo_students = [
        ("Amal Perera",    16, "M", "Grade 10", "amal@mail.com",    "0771111111", "Mr. D. Perera"),
        ("Nimali Fernando",15, "F", "Grade 9",  "nimali@mail.com",  "0772222222", "Mrs. R. Fernando"),
        ("Kasun Silva",    17, "M", "Grade 11", "kasun@mail.com",   "0773333333", "Mr. T. Silva"),
        ("Dilini Gunawardena",16,"F","Grade 10","dilini@mail.com",  "0774444444", "Mrs. P. Gunawardena"),
        ("Roshan Mendis",  18, "M", "Grade 12", "roshan@mail.com",  "0775555555", "Mr. K. Mendis"),
    ]
    for name, age, gender, cls, email, phone, guardian in demo_students:
        sid = new_id()
        codes = list(subjects.keys())
        enr   = random.sample(codes, k=random.randint(3, 5))
        grades = {c: random.randint(45, 98) for c in enr}
        students[sid] = {
            "name": name, "age": age, "gender": gender, "class": cls,
            "email": email, "phone": phone, "guardian": guardian,
            "enrolled": "2026-01-10", "grades": grades, "subjects": enr,
        }
        fees[sid] = [
            {"desc": "Tuition Fee", "amount": 150.00, "paid": True,  "date": "2026-01-10"},
            {"desc": "Lab Fee",     "amount":  30.00, "paid": False, "date": "2026-03-01"},
        ]
        attendance[sid] = {
            f"2026-0{m}-{d:02d}": random.choice(["P","P","P","A","L"])
            for m in range(1, 6) for d in range(1, 20)
            if datetime.date(2026, m, d).weekday() < 5
        }
    print("  ✅  Demo data loaded (5 students, 5 subjects).")


# ════════════════════════════════════════════════════════════
#   INTERNAL HELPER
# ════════════════════════════════════════════════════════════

def _ask_sid():
    raw = input("  Student ID (e.g. S-1001): ").strip().upper()
    if raw.startswith("S-") and raw[2:].isdigit():
        sid = int(raw[2:])
    elif raw.isdigit():
        sid = int(raw)
    else:
        print("  ❌  Invalid ID format."); return None
    if sid not in students:
        print(f"  ❌  Student S-{sid} not found."); return None
    return sid


# ════════════════════════════════════════════════════════════
#   MAIN MENU
# ════════════════════════════════════════════════════════════

MENU = [
    ("── STUDENTS ──────────────────", None),
    ("Register New Student",          register_student),
    ("Update Student Info",           update_student),
    ("Delete Student",                delete_student),
    ("List All Students",             list_all_students),
    ("Search / Filter Students",      search_students),
    ("── ACADEMICS ─────────────────", None),
    ("Enrol Student in Subject",      enrol_subject),
    ("Enter / Update Grades",         enter_grades),
    ("Print Report Card",             print_report_card),
    ("── SUBJECTS ──────────────────", None),
    ("Add Subject",                   add_subject),
    ("List Subjects",                 list_subjects),
    ("── ATTENDANCE ────────────────", None),
    ("Mark Attendance",               mark_attendance),
    ("View Student Attendance",       view_attendance),
    ("── FEES ──────────────────────", None),
    ("Add Fee",                       add_fee),
    ("Mark Fee as Paid",              pay_fee),
    ("Fee Summary",                   fee_summary),
    ("── REPORTS & STATS ───────────", None),
    ("Class Statistics",              class_statistics),
    ("Subject Statistics",            subject_statistics),
    ("Top Performers Leaderboard",    top_performers),
    ("── ────────────────────────────", None),
    ("Exit",                          None),
]


def main():
    print(f"\n{SEPARATOR}")
    print("  🎓  STUDENT MANAGEMENT SYSTEM")
    print("      City Academy — Academic Portal")
    print(SEPARATOR)
    print("\n  Loading demo data...")
    seed_demo()
    pause()

    while True:
        print(f"\n{SEPARATOR}")
        print("  📋  MAIN MENU")
        print(SEPARATOR)
        option_map = {}
        opt_num    = 0
        for label, func in MENU:
            if func is None and label.startswith("──"):
                print(f"\n  {label}")
            elif func is None:
                print(f"\n   0.  {label}")
            else:
                opt_num += 1
                option_map[str(opt_num)] = (label, func)
                print(f"  {opt_num:>2}.  {label}")

        choice = input("\n  Select option (0 to exit): ").strip()

        if choice == "0":
            print("\n  Goodbye! Have a great day. 👋\n")
            break
        elif choice in option_map:
            _, func = option_map[choice]
            func()
        else:
            print("  ❌  Invalid choice. Try again.")


if __name__ == "__main__":
    main()