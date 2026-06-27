# =============================================================
#Discarding gemini API because of the Qouta issues
# =============================================================

import pandas as pd
import os

print("=" * 60)
print("B2B SaaS Retention Recommendation Engine")
print("=" * 60)

# -------------------------------------------------------------
# SECTION 1: Load Data
# -------------------------------------------------------------
print("\n[1/4] Loading customer data...")

at_risk    = pd.read_csv('processed/result_at_risk_customers.csv')
accounts   = pd.read_csv('processed/clean_accounts.csv')
subs       = pd.read_csv('processed/clean_subscriptions.csv')

# Work with all at-risk customers (not just HIGH/CRITICAL)
customers  = at_risk.copy()

print(f"  Total customers loaded : {len(customers)}")
print(f"  Risk breakdown:\n{customers['risk_level'].value_counts()}")


# -------------------------------------------------------------
# SECTION 2: Enrich with Financial Data
# -------------------------------------------------------------
print("\n[2/4] Enriching with financial data...")

# Calculate total MRR per account
mrr_per_account = (
    subs.groupby('account_id')['mrr_amount']
    .sum()
    .reset_index()
    .rename(columns={'mrr_amount': 'total_mrr'})
)

# Calculate average MRR per account
avg_mrr = (
    subs.groupby('account_id')['mrr_amount']
    .mean()
    .reset_index()
    .rename(columns={'mrr_amount': 'avg_mrr'})
)

# Merge financial data into customers
customers = customers.merge(mrr_per_account, on='account_id', how='left')
customers = customers.merge(avg_mrr,         on='account_id', how='left')
customers = customers.merge(
    accounts[['account_id', 'country', 'seats']],
    on='account_id', how='left'
)
customers['total_mrr'] = customers['total_mrr'].fillna(0).round(2)
customers['avg_mrr']   = customers['avg_mrr'].fillna(0).round(2)

print(f"  Financial data merged successfully")


# -------------------------------------------------------------
# SECTION 3: Rule-Based Recommendation Engine
# -------------------------------------------------------------
print("\n[3/4] Generating recommendations...")

def get_primary_action(row):
    sat   = row.get('avg_satisfaction', 3)
    usage = row.get('usage_events', 0)
    esc   = row.get('escalations', 0)
    mrr   = row.get('total_mrr', 0)

    if sat < 2.5:
        return "Schedule urgent executive call within 48 hours — satisfaction is critically low"
    elif esc >= 2:
        return "Escalate all open tickets to VP Support — resolve every issue within 24 hours"
    elif usage < 5:
        return "Assign dedicated CSM to run personalised onboarding session this week"
    elif mrr > 5000:
        return "Offer executive business review — highlight ROI and strategic roadmap alignment"
    else:
        return "Send personalised check-in email with industry-specific product tips"

def get_secondary_action(row):
    plan  = str(row.get('plan_tier', '')).upper()
    usage = row.get('usage_events', 0)
    sat   = row.get('avg_satisfaction', 3)

    if plan == 'ENTERPRISE':
        return "Schedule quarterly business review and present detailed ROI report"
    elif plan == 'PRO':
        return "Invite to power-user webinar and introduce premium feature training"
    elif usage < 10:
        return "Enrol in structured 30-day onboarding programme with weekly check-ins"
    elif sat < 3:
        return "Conduct product satisfaction survey and share results with product team"
    else:
        return "Share success stories from similar companies in same industry"

def get_offer(row):
    plan  = str(row.get('plan_tier', '')).upper()
    sat   = row.get('avg_satisfaction', 3)
    esc   = row.get('escalations', 0)
    mrr   = row.get('total_mrr', 0)

    if sat < 2.0 or esc >= 3:
        return "2 months free + dedicated technical account manager for 90 days"
    elif plan == 'BASIC':
        return "Free upgrade to PRO for 3 months to demonstrate advanced platform value"
    elif plan == 'ENTERPRISE' and mrr > 5000:
        return "Custom SLA agreement + 10% discount on next annual renewal"
    elif plan == 'PRO':
        return "15% loyalty discount on annual renewal if committed within 30 days"
    else:
        return "1 month free extension + complimentary onboarding support session"

def get_key_risk(row):
    usage   = row.get('usage_events', 0)
    sat     = row.get('avg_satisfaction', 3)
    tickets = row.get('support_tickets', 0)
    errors  = row.get('total_errors', 0)
    esc     = row.get('escalations', 0)

    if usage < 5 and sat < 3:
        return "Critically low adoption + poor support experience — double churn signal"
    elif esc >= 2:
        return "Repeated escalations indicate unresolved critical issues damaging trust"
    elif errors > 50:
        return "High error count suggests product integration or technical failure"
    elif tickets > 8:
        return "Excessive support load signals product is not meeting basic expectations"
    elif sat < 3:
        return "Below-average satisfaction — customer is actively dissatisfied"
    elif usage < 10:
        return "Low engagement — customer has not discovered core product value yet"
    else:
        return "Moderate risk — monitor closely for any further decline in engagement"

def get_success_metric(row):
    usage = row.get('usage_events', 0)
    sat   = row.get('avg_satisfaction', 3)
    esc   = row.get('escalations', 0)

    if sat < 3:
        return f"Satisfaction score rises from {sat:.1f} to above 3.5 within 45 days"
    elif esc >= 2:
        return "Zero new escalations for 60 consecutive days"
    elif usage < 10:
        return f"Usage events increase from {int(usage)} to above 25 within 30 days"
    else:
        return "Customer renews subscription before end of current billing cycle"

def get_priority_action(row):
    """Overall retention priority label"""
    score = row.get('risk_score', 0)
    sat   = row.get('avg_satisfaction', 3)
    esc   = row.get('escalations', 0)

    if score >= 7 or sat < 2 or esc >= 3:
        return "ACT TODAY"
    elif score >= 4 or sat < 3:
        return "ACT THIS WEEK"
    elif score >= 2:
        return "ACT THIS MONTH"
    else:
        return "MONITOR"

def get_churn_probability(row):
    """Estimate churn probability as a percentage"""
    score = row.get('risk_score', 0)
    max_score = 11
    base_prob = (score / max_score) * 100

    # Adjust for satisfaction
    sat = row.get('avg_satisfaction', 3)
    if sat < 2:
        base_prob = min(base_prob + 20, 95)
    elif sat < 3:
        base_prob = min(base_prob + 10, 95)

    return round(base_prob, 1)

# Apply all rules to every customer
print("  Applying recommendation rules...")
customers['primary_action']    = customers.apply(get_primary_action,    axis=1)
customers['secondary_action']  = customers.apply(get_secondary_action,  axis=1)
customers['offer']             = customers.apply(get_offer,             axis=1)
customers['key_risk_factor']   = customers.apply(get_key_risk,          axis=1)
customers['success_metric']    = customers.apply(get_success_metric,    axis=1)
customers['priority_action']   = customers.apply(get_priority_action,   axis=1)
customers['churn_probability'] = customers.apply(get_churn_probability, axis=1)


# -------------------------------------------------------------
# SECTION 4: Save Output
# -------------------------------------------------------------
print("\n[4/4] Saving results...")

final_output = customers[[
    'account_id', 'account_name', 'plan_tier', 'industry',
    'country', 'seats', 'total_mrr', 'avg_mrr',
    'risk_level', 'risk_score', 'churn_probability',
    'priority_action', 'usage_events', 'total_errors',
    'support_tickets', 'avg_satisfaction', 'escalations',
    'sla_breaches', 'primary_action', 'secondary_action',
    'offer', 'key_risk_factor', 'success_metric'
]].sort_values('risk_score', ascending=False)

final_output.to_csv(
    'processed/result_retention_recommendations.csv',
    index=False
)

# -------------------------------------------------------------
# FINAL SUMMARY
# -------------------------------------------------------------
print("\n" + "=" * 60)
print("RETENTION ENGINE — Complete!")
print("=" * 60)
print(f"  Total customers analysed : {len(final_output)}")
print(f"  Saved to : processed/result_retention_recommendations.csv")

print("\nPRIORITY BREAKDOWN:")
print(final_output['priority_action'].value_counts().to_string())

print("\n" + "-" * 60)
print("TOP 5 AT-RISK CUSTOMERS:")
print("-" * 60)

for _, row in final_output.head(5).iterrows():
    print(f"\n  Account      : {row['account_name']}")
    print(f"  Plan         : {row['plan_tier']}")
    print(f"  Churn Risk   : {row['churn_probability']}%")
    print(f"  Priority     : {row['priority_action']}")
    print(f"  Primary      : {row['primary_action']}")
    print(f"  Offer        : {row['offer']}")
    print(f"  Key Risk     : {row['key_risk_factor']}")
    print(f"  Success KPI  : {row['success_metric']}")
    print(f"  {'─'*50}")

print("\n✓ Step 6 complete — Ready for Excel modeling (Step 7)")