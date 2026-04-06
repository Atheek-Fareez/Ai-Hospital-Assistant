---
name: hospital-assistant
description: Use this skill when building or working on a Hospital Management System (HIMS). This skill provides hospital workflows, billing logic, appointment handling, and patient management guidance.
---

# Project Purpose

This project is an AI Hospital Assistant integrated into a Hospital Information Management System (HIMS).

It helps automate hospital workflows such as:
- patient registration
- appointment booking
- billing
- department navigation
- patient summaries

# Core Modules

- Reception & Registration
- Appointment / Channeling
- Billing & Payments
- Laboratory
- Pharmacy
- Inward / IPD

# Behavior Rules

- Always follow real hospital workflow logic
- Do not invent unrealistic medical processes
- Keep responses simple and structured
- Prioritize clarity and correctness
- Do not give medical diagnosis

# Workflow Logic

## Patient Registration
1. Check if patient exists
2. If not, create new patient ID
3. Store name, phone, basic details

## Appointment Booking
1. Select doctor
2. Select date and session
3. Assign token number
4. Store appointment

## Billing
1. Add service items
2. Calculate total
3. Apply discount (if any)
4. Mark payment status

# Response Style

- Use simple English
- Give step-by-step explanations
- Be clear and structured