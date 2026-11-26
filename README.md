# 🏥 End-to-End Revenue Cycle Management (RCM) Command Center

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![HIPAA Safe](https://img.shields.io/badge/Data-100%25%20Synthetic%20%7C%20Zero%20PHI-2ea44f)](#hipaa--data-privacy-notice)
[![Domain](https://img.shields.io/badge/Healthcare-U.S.%20Medical%20Billing%20%26%20RCM-0077b5)](#core-rcm-workflow-modules)

An interactive U.S. healthcare billing and **Revenue Cycle Management (RCM)** operations sandbox built to streamline **front-end claim scrubbing**, **ERA/EOB underpayment detection**, **CARC/RARC denial resolution**, and **timely filing AR prioritization**.

> ### 🔒 HIPAA & Data Privacy Notice
> All patient names, subscriber/member IDs, authorization numbers, provider references, and clinical encounters in this repository are **100% synthetic** and created strictly for workflow demonstration. **Zero real Protected Health Information (PHI)** is stored, processed, or transmitted.

---

## 🎯 Why I Built This
In U.S. medical billing and healthcare virtual assistance, revenue leakage rarely happens in just one place—it builds up across missed eligibility checks, omitted DME/E&M modifiers, silent payer underpayments, and unworked denial queues nearing timely filing limits.

Drawing from hands-on experience in **Medicare Supplement member services, Durable Medical Equipment (DME) order processing, insurance verification, prior authorization coordination, and medical coding**, I built this tool to bridge **standard billing SOPs** with **lightweight automation** so small practices and billing teams can catch errors *before* submission and recover revenue *faster* after adjudication.

---

## 🔄 Core RCM Workflow Modules

| Module | RCM Stage | Operational Problem Solved | Key Features |
| :--- | :--- | :--- | :--- |
| **1. Pre-Bill Claim Scrubber** | Front-End & Mid-Cycle | Avoidable clearinghouse rejections caused by missing codes, expired auths, or omitted modifiers | Validates ICD-10 & CPT/HCPCS presence, flags `Missing`/`Expired` prior auths, and checks DME/E&M modifiers (`-25`, `-RR`, `-NU`, `-KX`) |
| **2. ERA/EOB Payment Audit** | Payment Posting | Contracted fee schedule underpayments and missed Medigap secondary crossovers | Calculates `Paid + Patient Responsibility - Expected Allowed` variance and isolates underpaid encounters |
| **3. Denial & Appeal Workbench** | Denial Management | Slow manual lookups of remittance codes and repetitive appeal drafting | Maps CARC/RARC codes (`CO-16`, `CO-97`, `CO-197`, `CO-29`, `PR-1`) to biller action checklists and auto-fills editable appeal letters |
| **4. AR Aging & Timely Filing** | Back-End Collections | High-dollar open claims expiring past payer timely filing windows | Groups open AR into `0–30`, `31–60`, `61–90`, and `90+` day buckets and triggers urgent alerts when `≤ 15 days` remain to file |

---

## 📊 Executive RCM KPIs Tracked
The dashboard calculates real-time revenue cycle health metrics across filtered payers and claim statuses:
- **Clean Claim Rate (CCR):** Percentage of submitted claims accepted without front-end/coding denials (`Benchmark: ≥ 95.0%`)
- **Net Collection Rate (NCR):** Collected reimbursement divided by net collectible allowed amount (`Benchmark: ≥ 96.0%`)
- **Average Days in Open AR:** Mean turnaround age of unresolved encounters (`Benchmark: < 35 days`)
- **Recoverable Revenue at Risk:** Total dollar value tied up in actionable denials and payer underpayments

---

## 📁 Repository Structure

```text
rcm-command-center/
├── README.md                    # Project overview, RCM workflow breakdown & setup guide
├── requirements.txt             # Python dependencies (Streamlit, Pandas)
├── app.py                       # Main interactive RCM dashboard & rules engine
└── data/
    ├── synthetic_claims.csv     # 15 synthetic encounters across Medicare, Medigap, Commercial & DME
    └── carc_rarc_rules.json     # Structured CARC/RARC root-cause rules, checklists & appeal templates
