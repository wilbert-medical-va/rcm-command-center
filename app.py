import json
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="End-to-End RCM Command Center",
    page_icon="🏥",
    layout="wide",
)

DATA_DIR = Path(__file__).parent / "data"


@st.cache_data
def load_data():
    claims_df = pd.read_csv(DATA_DIR / "synthetic_claims.csv").fillna("")
    with open(DATA_DIR / "carc_rarc_rules.json", "r", encoding="utf-8") as f:
        carc_rules = json.load(f)
    return claims_df, carc_rules


def scrub_claim(row: pd.Series) -> list[str]:
    """Rule-based pre-submission scrubber checking common RCM error triggers."""
    issues = []
    cpt = str(row["cpt_hcpcs"]).strip()
    modifier = str(row["modifier"]).strip()
    icd10 = str(row["icd10"]).strip()
    auth = str(row["prior_auth_status"]).strip()

    if not cpt:
        issues.append("CRITICAL: Missing CPT/HCPCS procedure code.")
    if not icd10:
        issues.append("CRITICAL: Missing ICD-10 diagnosis code.")
    if auth in ("Missing", "Expired"):
        issues.append(f"HOLD: Prior Authorization is '{auth}'. Verify before billing.")
    if cpt in ("E0601", "E0431") and "RR" not in modifier:
        issues.append("MODIFIER WARNING: Rental DME code typically requires modifier -RR.")
    if cpt in ("E0470", "A7030") and "NU" not in modifier:
        issues.append("MODIFIER WARNING: New DME purchase/supply typically requires modifier -NU.")
    if cpt == "L0650" and "KX" not in modifier:
        issues.append("MODIFIER WARNING: Medicare orthosis requires -KX when medical necessity criteria are met.")

    return issues


df, carc_rules = load_data()

# Sidebar Filters
st.sidebar.title("🏥 RCM Command Center")
st.sidebar.caption("100% Synthetic Clinic Dataset • Zero Real PHI")

payer_filter = st.sidebar.multiselect(
    "Filter by Payer",
    options=sorted(df["payer"].unique()),
    default=sorted(df["payer"].unique()),
)
status_filter = st.sidebar.multiselect(
    "Filter by Claim Status",
    options=sorted(df["status"].unique()),
    default=sorted(df["status"].unique()),
)

filtered_df = df[df["payer"].isin(payer_filter) & df["status"].isin(status_filter)].copy()

# Header
st.title("End-to-End Revenue Cycle Management (RCM) Sandbox")
st.markdown(
    "Operational command center covering **Front-End Intake & Scrubbing**, **ERA/EOB Payment Variance**, "
    "**CARC/RARC Denial Appeals**, and **AR Aging Prioritization**."
)

# Top KPI Bar
submitted_df = filtered_df[filtered_df["status"] != "Ready to Scrub"]
clean_claims = submitted_df[submitted_df["status"].isin(["Paid", "Patient Balance"])]
clean_claim_rate = (len(clean_claims) / len(submitted_df) * 100) if len(submitted_df) else 0.0

total_paid = filtered_df["paid_amount"].sum()
total_expected = (filtered_df["billed_amount"] - filtered_df["contractual_adj"]).sum()
net_collection_rate = (total_paid / total_expected * 100) if total_expected > 0 else 0.0

open_ar_df = filtered_df[~filtered_df["status"].isin(["Paid"])]
avg_days_in_ar = open_ar_df["days_in_ar"].mean() if len(open_ar_df) else 0.0
at_risk_revenue = filtered_df[filtered_df["status"].isin(["Denied", "Underpaid"])]["expected_allowed"].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Clean Claim Rate (CCR)", f"{clean_claim_rate:.1f}%", "Target: ≥ 95.0%")
k2.metric("Net Collection Rate (NCR)", f"{net_collection_rate:.1f}%", "Target: ≥ 96.0%")
k3.metric("Avg Days in Open AR", f"{avg_days_in_ar:.1f} days", "Target: < 35 days")
k4.metric("At-Risk / Recoverable Revenue", f"${at_risk_revenue:,.2f}", f"{len(filtered_df[filtered_df['status'].isin(['Denied', 'Underpaid'])])} claims")

st.divider()

# Workflow Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Pre-Bill Claim Scrubber",
    "2️⃣ Payment Posting & Underpayments",
    "3️⃣ Denial & Appeal Workbench",
    "4️⃣ AR Aging & Timely Filing",
])

# TAB 1: Pre-Bill Claim Scrubber
with tab1:
    st.subheader("Front-End & Mid-Cycle Claim Scrubbing Queue")
    st.caption("Audits unbilled encounters for missing codes, expired prior authorizations, and DME/E&M modifier rules.")

    scrub_queue = filtered_df[filtered_df["status"] == "Ready to Scrub"].copy()
    if scrub_queue.empty:
        st.info("No 'Ready to Scrub' claims match the current filters.")
    else:
        for _, row in scrub_queue.iterrows():
            issues = scrub_claim(row)
            badge = "✅ PASS — Ready for Clearinghouse Batch" if not issues else f"🚨 HOLD — {len(issues)} Issue(s) Detected"
            with st.expander(f"{row['claim_id']} | {row['patient_name']} ({row['payer']}) — {badge}", expanded=bool(issues)):
                c1, c2, c3, c4 = st.columns(4)
                c1.write(f"**DOS:** {row['dos']}")
                c2.write(f"**CPT/HCPCS:** `{row['cpt_hcpcs'] or 'MISSING'}` | **Mod:** `{row['modifier'] or 'None'}`")
                c3.write(f"**ICD-10:** `{row['icd10'] or 'MISSING'}`")
                c4.write(f"**Prior Auth:** {row['prior_auth_status']}")
                st.write(f"**Encounter Note:** {row['notes']}")
                if issues:
                    for issue in issues:
                        st.error(issue)
                else:
                    st.success("All front-end eligibility, authorization, and modifier rules passed.")

# TAB 2: Payment Posting & Underpayments
with tab2:
    st.subheader("ERA / EOB Payment Variance & Underpayment Audit")
    st.caption("Compares actual payer remittance against expected contracted fee schedule allowed amounts.")

    posted_df = filtered_df[filtered_df["status"].isin(["Paid", "Underpaid", "Patient Balance"])].copy()
    posted_df["variance"] = posted_df["paid_amount"] + posted_df["patient_resp"] - posted_df["expected_allowed"]

    st.dataframe(
        posted_df[[
            "claim_id", "patient_name", "payer", "cpt_hcpcs", "billed_amount",
            "expected_allowed", "paid_amount", "patient_resp", "variance", "status", "notes"
        ]],
        use_container_width=True,
        hide_index=True,
    )

    underpaid_df = posted_df[posted_df["variance"] < -0.01]
    if not underpaid_df.empty:
        st.warning(f"Detected {len(underpaid_df)} underpaid claim(s) totaling ${abs(underpaid_df['variance'].sum()):,.2f} in recoverable variance.")

# TAB 3: Denial & Appeal Workbench
with tab3:
    st.subheader("CARC/RARC Denial Playbook & Appeal Letter Generator")
    denied_df = filtered_df[filtered_df["status"].isin(["Denied", "Patient Balance"])].copy()

    if denied_df.empty:
        st.info("No denied claims in the current filter selection.")
    else:
        selected_id = st.selectbox(
            "Select a Denied / Exception Claim to Work:",
            options=denied_df["claim_id"].tolist(),
            format_func=lambda cid: (
                f"{cid} — {denied_df.loc[denied_df['claim_id'] == cid, 'patient_name'].values[0]} "
                f"({denied_df.loc[denied_df['claim_id'] == cid, 'carc_code'].values[0]} | "
                f"${denied_df.loc[denied_df['claim_id'] == cid, 'expected_allowed'].values[0]:,.2f})"
            ),
        )

        claim = denied_df[denied_df["claim_id"] == selected_id].iloc[0]
        code = claim["carc_code"]
        rule = carc_rules.get(code, {})

        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.markdown(f"### {code}: {rule.get('title', 'Unmapped Code')}")
            st.write(f"**Root Cause Category:** `{rule.get('root_cause', 'General')}`")
            st.write(f"**Payer:** {claim['payer']} ({claim['plan_type']})")
            st.write(f"**DOS:** {claim['dos']} | **CPT/HCPCS:** `{claim['cpt_hcpcs']}` | **ICD-10:** `{claim['icd10']}`")
            st.write(f"**Biller Audit Note:** {claim['notes']}")
            st.markdown("#### Required Biller Action Checklist")
            for step in rule.get("action_checklist", ["Review EOB and payer policy guidelines."]):
                st.checkbox(step, key=f"{selected_id}_{step[:20]}")

        with col_right:
            st.markdown("### Auto-Generated Appeal / Action Draft")
            template = rule.get("appeal_template", "")
            filled_letter = template.format(
                dos=claim["dos"],
                cpt=claim["cpt_hcpcs"],
                modifier=claim["modifier"] or "[INSERT MODIFIER]",
                auth_number=claim["prior_auth_status"].replace("Approved (", "").replace(")", "") if "PA-" in claim["prior_auth_status"] else "[INSERT AUTH #]",
                missing_detail=claim["notes"],
                patient_resp=f"{claim['patient_resp']:,.2f}",
                claim_id=claim["claim_id"],
            )
            st.text_area("Edit & Copy for Payer Portal / Fax:", value=filled_letter, height=230)

# TAB 4: AR Aging & Timely Filing
with tab4:
    st.subheader("Accounts Receivable (AR) Aging & Timely Filing Countdown")

    ar_df = filtered_df[filtered_df["status"] != "Paid"].copy()
    ar_df["days_left_to_file"] = ar_df["timely_filing_limit_days"] - ar_df["days_in_ar"]

    def bucket_label(days: int) -> str:
        if days <= 30:
            return "0-30 Days"
        if days <= 60:
            return "31-60 Days"
        if days <= 90:
            return "61-90 Days"
        return "90+ Days"

    ar_df["aging_bucket"] = ar_df["days_in_ar"].apply(bucket_label)

    bucket_summary = (
        ar_df.groupby("aging_bucket", as_index=False)["expected_allowed"]
        .sum()
        .rename(columns={"aging_bucket": "Aging Bucket", "expected_allowed": "Open Expected Revenue ($)"})
    )
    st.bar_chart(bucket_summary.set_index("Aging Bucket"))

    urgent_tf = ar_df[ar_df["days_left_to_file"] <= 15]
    if not urgent_tf.empty:
        st.error(f"🚨 TIMELY FILING ALERT: {len(urgent_tf)} claim(s) have 15 or fewer days remaining before payer timely filing expires!")

    st.dataframe(
        ar_df[[
            "claim_id", "patient_name", "payer", "status", "carc_code",
            "expected_allowed", "days_in_ar", "days_left_to_file", "aging_bucket", "notes"
        ]].sort_values(by="days_left_to_file"),
        use_container_width=True,
        hide_index=True,
    )
