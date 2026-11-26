# 🏥 End-to-End Revenue Cycle Management (RCM) Command Center

An interactive healthcare billing and Revenue Cycle Management (RCM) operations sandbox built to automate **pre-bill claim scrubbing**, **ERA/EOB underpayment detection**, **CARC/RARC denial resolution**, and **timely filing AR prioritization**.

> **HIPAA & Data Privacy Notice:** All patient names, member IDs, authorization numbers, and clinical encounters in this repository are **100% synthetic** and created strictly for workflow demonstration. Zero real Protected Health Information (PHI) is stored or processed.

---

## 🎯 Operational Problem Solved
Medical billing teams and virtual assistants lose hours every week manually cross-checking modifiers, hunting down CARC/RARC denial explanations, spotting underpaid EOB lines, and tracking timely filing deadlines across spreadsheets. This command center centralizes the full RCM lifecycle into a single audit workflow:

1. **Front-End Intake & Pre-Bill Claim Scrubber:** Flags missing CPT/ICD-10 codes, expired prior authorizations, and missing DME/E&M modifiers (`-25`, `-RR`, `-NU`, `-KX`) *before* clearinghouse submission.
2. **Payment Posting & Underpayment Audit:** Compares payer remittance (`Paid + Patient Responsibility`) against expected contracted fee schedules to catch silent underpayments and missed Medicare Supplement (Medigap) crossovers.
3. **CARC/RARC Denial & Appeal Workbench:** Maps denial codes (`CO-16`, `CO-97`, `CO-197`, `CO-29`, `PR-1`) to step-by-step biller verification checklists and auto-populates editable appeal cover letters.
4. **AR Aging & Timely Filing Prioritizer:** Groups open receivables into `0–30`, `31–60`, `61–90`, and `90+` day buckets and triggers urgent alerts when a claim is within 15 days of a payer's timely filing cutoff.

---

## 📊 Key RCM Metrics Tracked
- **Clean Claim Rate (CCR):** First-pass claim acceptance rate (`Target: ≥ 95%`)
- **Net Collection Rate (NCR):** Collected reimbursement divided by net collectible allowed amount (`Target: ≥ 96%`)
- **Days in Accounts Receivable:** Average turnaround time on unresolved claims
- **Recoverable Revenue at Risk:** Total dollar value tied up in actionable denials and underpayments

---

## 🚀 Quick Start (Run Locally)

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/rcm-command-center.git](https://github.com/YOUR_USERNAME/rcm-command-center.git)
   cd rcm-command-center
