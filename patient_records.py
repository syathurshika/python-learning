"""
🏥  Hospital Patient Records Management System
"""

import datetime

SEPARATOR = "=" * 56

# In-memory patient database {patient_id: record}
patients = {}
next_id = 1000  # Auto-increment patient ID


# ─────────────────────────────────────────
#  Helper utilities
# ─────────────────────────────────────────

def today():
    return datetime.date.today().strftime("%Y-%m-%d")


def get_patient(pid):
    """Return patient record or None."""
    return patients.get(pid)


def print_header(title):
    print(f"\n{SEPARATOR}")
    print(f"  🏥  {title}")
    print(SEPARATOR)


def pause():
    input("\n  Press Enter to continue...")


# ─────────────────────────────────────────
#  Core features
# ─────────────────────────────────────────

def register_patient():
    """Add a new patient to the system."""
    global next_id
    print_header("REGISTER NEW PATIENT")

    name = input("  Full Name       : ").strip()
    if not name:
        print("  ❌  Name cannot be empty.")
        return

    age_raw = input("  Age             : ").strip()
    if not age_raw.isdigit():
        print("  ❌  Age must be a number.")
        return

    gender = input("  Gender (M/F/O)  : ").strip().upper()
    if gender not in ("M", "F", "O"):
        print("  ❌  Enter M, F, or O.")
        return

    blood_group = input("  Blood Group     : ").strip().upper()
    contact     = input("  Contact Number  : ").strip()
    address     = input("  Address         : ").strip()

    pid = next_id
    next_id += 1

    patients[pid] = {
        "name"        : name,
        "age"         : int(age_raw),
        "gender"      : gender,
        "blood_group" : blood_group,
        "contact"     : contact,
        "address"     : address,
        "admitted_on" : today(),
        "diagnosis"   : [],   # list of {date, doctor, notes}
        "prescriptions": [],  # list of {date, medicine, dosage, doctor}
        "bills"       : [],   # list of {date, description, amount}
    }

    print(f"\n  ✅  Patient registered successfully!")
    print(f"  📋  Patient ID : P-{pid}")
    pause()


def view_patient():
    """Display full record of a patient."""
    print_header("VIEW PATIENT RECORD")
    pid = _ask_pid()
    if pid is None:
        return

    p = get_patient(pid)
    print(f"\n  {'─'*50}")
    print(f"  Patient ID   : P-{pid}")
    print(f"  Name         : {p['name']}")
    print(f"  Age          : {p['age']}")
    print(f"  Gender       : {p['gender']}")
    print(f"  Blood Group  : {p['blood_group']}")
    print(f"  Contact      : {p['contact']}")
    print(f"  Address      : {p['address']}")
    print(f"  Admitted On  : {p['admitted_on']}")

    # Diagnoses
    print(f"\n  📝  DIAGNOSES ({len(p['diagnosis'])})")
    if p["diagnosis"]:
        for i, d in enumerate(p["diagnosis"], 1):
            print(f"   {i}. [{d['date']}] Dr. {d['doctor']} — {d['notes']}")
    else:
        print("   None recorded.")

    # Prescriptions
    print(f"\n  💊  PRESCRIPTIONS ({len(p['prescriptions'])})")
    if p["prescriptions"]:
        for i, rx in enumerate(p["prescriptions"], 1):
            print(f"   {i}. [{rx['date']}] {rx['medicine']} {rx['dosage']}  (Dr. {rx['doctor']})")
    else:
        print("   None recorded.")

    # Bills
    print(f"\n  💰  BILLS ({len(p['bills'])})")
    if p["bills"]:
        total = 0
        for i, b in enumerate(p["bills"], 1):
            print(f"   {i}. [{b['date']}] {b['description']:<28} ${b['amount']:.2f}")
            total += b["amount"]
        print(f"   {'─'*44}")
        print(f"   {'Total Outstanding':<32} ${total:.2f}")
    else:
        print("   No bills.")

    print(f"  {'─'*50}")
    pause()


def add_diagnosis():
    """Record a new diagnosis for a patient."""
    print_header("ADD DIAGNOSIS")
    pid = _ask_pid()
    if pid is None:
        return

    p = get_patient(pid)
    doctor = input("  Doctor's Name   : ").strip()
    notes  = input("  Diagnosis Notes : ").strip()

    if not doctor or not notes:
        print("  ❌  Doctor name and notes are required.")
        return

    p["diagnosis"].append({"date": today(), "doctor": doctor, "notes": notes})
    print(f"  ✅  Diagnosis added for {p['name']}.")
    pause()


def add_prescription():
    """Add a prescription for a patient."""
    print_header("ADD PRESCRIPTION")
    pid = _ask_pid()
    if pid is None:
        return

    p = get_patient(pid)
    doctor   = input("  Doctor's Name   : ").strip()
    medicine = input("  Medicine        : ").strip()
    dosage   = input("  Dosage          : ").strip()

    if not all([doctor, medicine, dosage]):
        print("  ❌  All fields are required.")
        return

    p["prescriptions"].append({
        "date": today(), "doctor": doctor,
        "medicine": medicine, "dosage": dosage
    })
    print(f"  ✅  Prescription added for {p['name']}.")
    pause()


def add_bill():
    """Add a billing entry for a patient."""
    print_header("ADD BILL")
    pid = _ask_pid()
    if pid is None:
        return

    p = get_patient(pid)
    description = input("  Description     : ").strip()
    amount_raw  = input("  Amount ($)      : ").strip()

    try:
        amount = float(amount_raw)
        if amount <= 0:
            raise ValueError
    except ValueError:
        print("  ❌  Enter a valid positive amount.")
        return

    p["bills"].append({"date": today(), "description": description, "amount": amount})
    print(f"  ✅  Bill of ${amount:.2f} added for {p['name']}.")
    pause()


def search_patient():
    """Search patients by name."""
    print_header("SEARCH PATIENT")
    query = input("  Enter name to search: ").strip().lower()
    results = [(pid, p) for pid, p in patients.items()
               if query in p["name"].lower()]

    if not results:
        print("  ❌  No patients found.")
    else:
        print(f"\n  Found {len(results)} result(s):\n")
        print(f"  {'ID':<8} {'Name':<22} {'Age':<5} {'Blood':<7} {'Admitted'}")
        print(f"  {'─'*52}")
        for pid, p in results:
            print(f"  P-{pid:<6} {p['name']:<22} {p['age']:<5} {p['blood_group']:<7} {p['admitted_on']}")
    pause()


def list_all_patients():
    """List every registered patient."""
    print_header("ALL PATIENTS")
    if not patients:
        print("  No patients registered yet.")
        pause()
        return

    print(f"\n  {'ID':<8} {'Name':<22} {'Age':<5} {'Gender':<7} {'Blood':<7} {'Admitted'}")
    print(f"  {'─'*58}")
    for pid, p in patients.items():
        print(f"  P-{pid:<6} {p['name']:<22} {p['age']:<5} {p['gender']:<7} {p['blood_group']:<7} {p['admitted_on']}")
    print(f"\n  Total patients: {len(patients)}")
    pause()


def discharge_patient():
    """Remove a patient from active records."""
    print_header("DISCHARGE PATIENT")
    pid = _ask_pid()
    if pid is None:
        return

    p = get_patient(pid)
    confirm = input(f"  Discharge {p['name']} (P-{pid})? (yes/no): ").strip().lower()
    if confirm in ("yes", "y"):
        del patients[pid]
        print(f"  ✅  Patient P-{pid} has been discharged.")
    else:
        print("  ↩️  Discharge cancelled.")
    pause()


# ─────────────────────────────────────────
#  Internal helper
# ─────────────────────────────────────────

def _ask_pid():
    """Prompt for a patient ID and validate it."""
    raw = input("  Enter Patient ID (e.g. P-1000): ").strip().upper()
    if raw.startswith("P-") and raw[2:].isdigit():
        pid = int(raw[2:])
    elif raw.isdigit():
        pid = int(raw)
    else:
        print("  ❌  Invalid ID format.")
        return None

    if pid not in patients:
        print(f"  ❌  Patient P-{pid} not found.")
        return None
    return pid


# ─────────────────────────────────────────
#  Main menu
# ─────────────────────────────────────────

MENU_OPTIONS = {
    "1": ("Register New Patient",   register_patient),
    "2": ("View Patient Record",    view_patient),
    "3": ("Add Diagnosis",          add_diagnosis),
    "4": ("Add Prescription",       add_prescription),
    "5": ("Add Bill",               add_bill),
    "6": ("Search Patient by Name", search_patient),
    "7": ("List All Patients",      list_all_patients),
    "8": ("Discharge Patient",      discharge_patient),
    "9": ("Exit",                   None),
}


def main_menu():
    while True:
        print(f"\n{SEPARATOR}")
        print("  🏥  CITY GENERAL HOSPITAL — Patient Records")
        print(SEPARATOR)
        for key, (label, _) in MENU_OPTIONS.items():
            icon = "🚪" if key == "0" else f" {key}."
            print(f"  {icon}  {label}")
        print(SEPARATOR)

        choice = input("  Select option: ").strip()
        if choice not in MENU_OPTIONS:
            print("  ❌  Invalid choice. Please try again.")
            continue

        label, func = MENU_OPTIONS[choice]
        if func is None:
            print("\n  Goodbye! Stay healthy. 👋\n")
            break
        func()


if __name__ == "__main__":
    # Preload sample data for demo purposes
    patients[1000] = {
        "name": "Amal Perera", "age": 34, "gender": "M",
        "blood_group": "O+", "contact": "0771234567",
        "address": "12 Galle Rd, Colombo",
        "admitted_on": "2026-06-01",
        "diagnosis": [{"date": "2026-06-01", "doctor": "Silva", "notes": "Viral fever, mild dehydration"}],
        "prescriptions": [{"date": "2026-06-01", "doctor": "Silva", "medicine": "Paracetamol", "dosage": "500mg 3x/day"}],
        "bills": [{"date": "2026-06-01", "description": "Consultation", "amount": 25.00},
                  {"date": "2026-06-02", "description": "Blood Test", "amount": 40.00}],
    }
    next_id = 1001
    print("  ℹ️  Sample patient loaded: P-1000 (Amal Perera)")
    main_menu()