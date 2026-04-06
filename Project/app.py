import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from datetime import date

# Load environment variables
load_dotenv()

# Get API key from .env
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None

# Files
PATIENT_FILE = "patients.json"
BILL_FILE = "bills.json"
DOCTOR_FILE = "doctors.json"
TOKEN_FILE = "tokens.json"


# -------------------------
# Patient functions
# -------------------------
def load_patients():
    if os.path.exists(PATIENT_FILE):
        try:
            with open(PATIENT_FILE, "r") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except (json.JSONDecodeError, ValueError):
            return []
    return []


def save_patients(patients):
    with open(PATIENT_FILE, "w") as file:
        json.dump(patients, file, indent=2)


def add_patient(name, phone, age):
    patients = load_patients()
    patient_id = f"P{len(patients) + 1:03}"

    new_patient = {
        "patient_id": patient_id,
        "name": name,
        "phone": phone,
        "age": age
    }

    patients.append(new_patient)
    save_patients(patients)
    return new_patient


# -------------------------
# Billing functions
# -------------------------
def load_bills():
    if os.path.exists(BILL_FILE):
        try:
            with open(BILL_FILE, "r") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except (json.JSONDecodeError, ValueError):
            return []
    return []


def save_bills(bills):
    with open(BILL_FILE, "w") as file:
        json.dump(bills, file, indent=2)


def add_bill(patient_id, doctor_id, service, amount):
    bills = load_bills()
    patients = load_patients()
    doctors = load_doctors()

    patient_name = "Unknown"
    for p in patients:
        if p.get("patient_id") == patient_id:
            patient_name = p.get("name", "Unknown")
            break

    doctor_name = "Unknown"
    consultation_fee = 0
    for d in doctors:
        if d.get("doctor_id") == doctor_id:
            doctor_name = d.get("doctor_name", "Unknown")
            consultation_fee = d.get("consultation_fee", 0)
            break

    bill_id = f"B{len(bills) + 1:03}"

    new_bill = {
        "bill_id": bill_id,
        "patient_id": patient_id,
        "patient_name": patient_name,
        "doctor_id": doctor_id,
        "doctor_name": doctor_name,
        "service": service,
        "amount": amount,
        "consultation_fee": consultation_fee,
        "status": "PENDING"
    }

    bills.append(new_bill)
    save_bills(bills)
    return new_bill


def mark_bill_as_paid(bill_id):
    bills = load_bills()

    for bill in bills:
        if bill.get("bill_id") == bill_id:
            if bill.get("status") == "PAID":
                return bill, None

            bill["status"] = "PAID"
            save_bills(bills)

            # Generate token only for consultation bills
            if bill.get("service") == "Consultation":
                token = create_token_from_bill(bill)
                return bill, token

            return bill, None

    return None, None


# -------------------------
# Doctor functions
# -------------------------
def load_doctors():
    if os.path.exists(DOCTOR_FILE):
        try:
            with open(DOCTOR_FILE, "r") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except (json.JSONDecodeError, ValueError):
            return []
    return []


def save_doctors(doctors):
    with open(DOCTOR_FILE, "w") as file:
        json.dump(doctors, file, indent=2)


def add_doctor(doctor_name, specialization, consultation_fee, active_status):
    doctors = load_doctors()
    doctor_id = f"D{len(doctors) + 1:03}"

    new_doctor = {
        "doctor_id": doctor_id,
        "doctor_name": doctor_name,
        "specialization": specialization,
        "consultation_fee": consultation_fee,
        "active_status": active_status
    }

    doctors.append(new_doctor)
    save_doctors(doctors)
    return new_doctor


# -------------------------
# Token functions
# -------------------------
def load_tokens():
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except (json.JSONDecodeError, ValueError):
            return []
    return []


def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as file:
        json.dump(tokens, file, indent=2)


def get_next_token_number(doctor_id, token_date):
    tokens = load_tokens()

    doctor_day_tokens = [
        t for t in tokens
        if t.get("doctor_id") == doctor_id and t.get("date") == token_date
    ]

    if not doctor_day_tokens:
        return 1

    max_token = max(t.get("token_number", 0) for t in doctor_day_tokens)
    return max_token + 1


def create_token_from_bill(bill):
    tokens = load_tokens()
    token_id = f"T{len(tokens) + 1:03}"
    today = str(date.today())

    doctor_id = bill.get("doctor_id")
    doctor_name = bill.get("doctor_name", "Unknown")
    patient_id = bill.get("patient_id", "Unknown")
    patient_name = bill.get("patient_name", "Unknown")

    if not doctor_id:
        return None

    next_token_number = get_next_token_number(doctor_id, today)

    new_token = {
        "token_id": token_id,
        "date": today,
        "bill_id": bill.get("bill_id"),
        "patient_id": patient_id,
        "patient_name": patient_name,
        "doctor_id": doctor_id,
        "doctor_name": doctor_name,
        "token_number": next_token_number,
        "status": "WAITING"
    }

    tokens.append(new_token)
    save_tokens(tokens)
    return new_token


# -------------------------
# App UI
# -------------------------
st.set_page_config(page_title="AI Hospital Assistant", layout="wide")

st.title("🏥 AI Hospital Assistant")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["AI Assistant", "Patient Registration", "Billing", "Doctor Management", "Payments & Tokens"]
)


# -------------------------
# AI Assistant Tab
# -------------------------
with tab1:
    st.subheader("Ask Hospital Questions")
    st.write("Ask anything about hospital workflows, appointments, billing, etc.")

    user_input = st.text_input("Enter your question:")

    SYSTEM_PROMPT = """
    You are an AI Hospital Assistant.

    Rules:
    - Follow real hospital workflows
    - Explain step-by-step
    - Use simple English
    - Do NOT give medical diagnosis
    - Focus on:
      - patient registration
      - appointments
      - billing
      - hospital operations
    """

    if st.button("Ask"):
        if not api_key:
            st.error("❌ API key not found. Check your .env file.")
        elif not user_input:
            st.warning("⚠️ Please enter a question")
        elif model is None:
            st.error("❌ Model not loaded. Check your API key.")
        else:
            try:
                with st.spinner("Thinking..."):
                    response = model.generate_content(
                        SYSTEM_PROMPT + "\nUser: " + user_input
                    )
                    st.write("### 🤖 Response:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


# -------------------------
# Patient Registration Tab
# -------------------------
with tab2:
    st.subheader("Register New Patient")

    name = st.text_input("Patient Name")
    phone = st.text_input("Phone Number")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)

    if st.button("Save Patient"):
        if not name or not phone:
            st.warning("⚠️ Please fill all patient details")
        else:
            patient = add_patient(name, phone, age)
            st.success(f"✅ Patient saved successfully! Patient ID: {patient['patient_id']}")

    st.subheader("Saved Patients")
    patients = load_patients()

    if patients:
        st.table(patients)
    else:
        st.info("No patients registered yet.")


# -------------------------
# Billing Tab
# -------------------------
with tab3:
    st.subheader("Create Bill")

    patients = load_patients()
    doctors = load_doctors()
    selected_doctor_data = None

    # Patient selection
    if patients:
        patient_options = {
            f"{p.get('patient_id')} - {p.get('name', 'Unknown')}": p.get("patient_id")
            for p in patients if p.get("patient_id")
        }

        if patient_options:
            selected_patient = st.selectbox(
                "Select Patient",
                list(patient_options.keys())
            )

            patient_id = patient_options[selected_patient]
            st.info(f"Selected Patient ID: {patient_id}")
        else:
            st.warning("No valid patients available.")
            patient_id = None
    else:
        st.warning("No patients available. Please register a patient first.")
        patient_id = None

    # Doctor selection
    if doctors:
        active_doctors = [d for d in doctors if d.get("active_status") == "Active"]

        if active_doctors:
            doctor_options = {
                f"{d.get('doctor_id')} - {d.get('doctor_name', 'Unknown')} ({d.get('specialization', 'Unknown')})": d.get("doctor_id")
                for d in active_doctors if d.get("doctor_id")
            }

            if doctor_options:
                selected_doctor = st.selectbox(
                    "Select Doctor",
                    list(doctor_options.keys())
                )

                doctor_id = doctor_options[selected_doctor]

                selected_doctor_data = next(
                    (d for d in active_doctors if d.get("doctor_id") == doctor_id),
                    None
                )

                if selected_doctor_data:
                    st.info(f"Doctor Fee: {selected_doctor_data.get('consultation_fee', 0)}")
            else:
                st.warning("No valid active doctors available.")
                doctor_id = None
        else:
            st.warning("No active doctors available.")
            doctor_id = None
    else:
        st.warning("No doctors available. Please add a doctor first.")
        doctor_id = None

    service = st.selectbox(
        "Service",
        ["Consultation", "Laboratory", "Pharmacy", "X-Ray", "Scan", "Other"]
    )

    # Auto-fill amount for consultation
    if service == "Consultation" and selected_doctor_data:
        amount = st.number_input(
            "Amount",
            min_value=0.0,
            value=float(selected_doctor_data.get("consultation_fee", 0)),
            step=100.0
        )
    else:
        amount = st.number_input("Amount", min_value=0.0, step=100.0)

    if st.button("Save Bill"):
        if not patient_id:
            st.warning("⚠️ Please select a patient")
        elif not doctor_id:
            st.warning("⚠️ Please select a doctor")
        elif amount <= 0:
            st.warning("⚠️ Enter valid amount")
        else:
            bill = add_bill(patient_id, doctor_id, service, amount)
            st.success(f"✅ Bill saved! Bill ID: {bill['bill_id']}")

    st.subheader("Saved Bills")
    bills = load_bills()

    if bills:
        st.table(bills)
    else:
        st.info("No bills created yet.")


# -------------------------
# Doctor Management Tab
# -------------------------
with tab4:
    st.subheader("Add New Doctor")

    doctor_name = st.text_input("Doctor Name")
    specialization = st.text_input("Specialization")
    consultation_fee = st.number_input("Consultation Fee", min_value=0.0, step=100.0)
    active_status = st.selectbox("Status", ["Active", "Inactive"])

    if st.button("Save Doctor"):
        if not doctor_name or not specialization:
            st.warning("⚠️ Please fill all doctor details")
        elif consultation_fee <= 0:
            st.warning("⚠️ Please enter a valid consultation fee")
        else:
            doctor = add_doctor(doctor_name, specialization, consultation_fee, active_status)
            st.success(f"✅ Doctor saved successfully! Doctor ID: {doctor['doctor_id']}")

    st.subheader("Saved Doctors")
    doctors = load_doctors()

    if doctors:
        st.table(doctors)
    else:
        st.info("No doctors added yet.")


# -------------------------
# Payments & Tokens Tab
# -------------------------
with tab5:
    st.subheader("Mark Bill as Paid")

    bills = load_bills()

    pending_bills = [b for b in bills if b.get("status") == "PENDING"]

    if pending_bills:
        bill_options = {
            f"{b.get('bill_id', 'N/A')} - {b.get('patient_name', 'Unknown')} - {b.get('doctor_name', 'Unknown')} - {b.get('service', 'Unknown')} - Rs.{b.get('amount', 0)}": b.get("bill_id")
            for b in pending_bills if b.get("bill_id")
        }

        if bill_options:
            selected_bill_label = st.selectbox(
                "Select Pending Bill",
                list(bill_options.keys())
            )

            selected_bill_id = bill_options[selected_bill_label]

            if st.button("Mark as Paid"):
                updated_bill, token = mark_bill_as_paid(selected_bill_id)

                if updated_bill:
                    st.success(f"✅ Bill {updated_bill['bill_id']} marked as PAID")

                    if token:
                        st.success(
                            f"🎟️ Token generated successfully! Token No: {token['token_number']} | Doctor: {token['doctor_name']} | Patient: {token['patient_name']}"
                        )
                    elif updated_bill.get("service") == "Consultation":
                        st.warning("⚠️ Bill marked as PAID, but token was not generated.")
                    else:
                        st.info("No token generated because this is not a consultation bill.")
                else:
                    st.error("❌ Bill not found.")
        else:
            st.info("No valid pending bills available.")
    else:
        st.info("No pending bills available.")

    st.subheader("Saved Tokens")
    tokens = load_tokens()

    if tokens:
        st.table(tokens)
    else:
        st.info("No tokens generated yet.")