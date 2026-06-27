
# Create tables and load cleaned CSVs into PostgreSQL
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# -------------------------------------------------------------
#  Load credentials from .env file
# -------------------------------------------------------------
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

CONNECTION_STRING = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print("=" * 60)
print("B2B SaaS Retention Pipeline — PostgreSQL Loader")
print("=" * 60)

try:
    engine = create_engine(CONNECTION_STRING)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✓ Connected to PostgreSQL successfully!")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("Check your .env file credentials")
    exit()

# -------------------------------------------------------------
#  Load ACCOUNTS table
# -------------------------------------------------------------
print("\n[1/5] Loading accounts table...")
accounts = pd.read_csv('processed/clean_accounts.csv')
accounts['signup_date'] = pd.to_datetime(accounts['signup_date'])
accounts.to_sql(
    name='accounts',
    con=engine,
    if_exists='replace',
    index=False,
    method='multi'
)
print(f"  ✓ accounts table loaded — {len(accounts)} rows")

# -------------------------------------------------------------
# Load SUBSCRIPTIONS table
# -------------------------------------------------------------
print("\n[2/5] Loading subscriptions table...")
subs = pd.read_csv('processed/clean_subscriptions.csv')
subs['start_date'] = pd.to_datetime(subs['start_date'])
subs['end_date'] = pd.to_datetime(subs['end_date'])
subs.to_sql(
    name='subscriptions',
    con=engine,
    if_exists='replace',
    index=False,
    method='multi'
)
print(f"  ✓ subscriptions table loaded — {len(subs)} rows")

# -------------------------------------------------------------
# Load CHURN EVENTS table
# -------------------------------------------------------------
print("\n[3/5] Loading churn_events table...")
churn = pd.read_csv('processed/clean_churn_events.csv')
churn['churn_date'] = pd.to_datetime(churn['churn_date'])
churn.to_sql(
    name='churn_events',
    con=engine,
    if_exists='replace',
    index=False,
    method='multi'
)
print(f"  ✓ churn_events table loaded — {len(churn)} rows")

# -------------------------------------------------------------
# Load FEATURE USAGE table
# -------------------------------------------------------------
print("\n[4/5] Loading feature_usage table...")
usage = pd.read_csv('processed/clean_feature_usage.csv')
usage['usage_date'] = pd.to_datetime(usage['usage_date'])
usage.to_sql(
    name='feature_usage',
    con=engine,
    if_exists='replace',
    index=False,
    method='multi'
)
print(f"  ✓ feature_usage table loaded — {len(usage)} rows")

# -------------------------------------------------------------
# Load SUPPORT TICKETS table
# -------------------------------------------------------------
print("\n[5/5] Loading support_tickets table...")
tickets = pd.read_csv('processed/clean_support_tickets.csv')
tickets['submitted_at'] = pd.to_datetime(tickets['submitted_at'])
tickets['closed_at'] = pd.to_datetime(tickets['closed_at'])
tickets.to_sql(
    name='support_tickets',
    con=engine,
    if_exists='replace',
    index=False,
    method='multi'
)
print(f"  ✓ support_tickets table loaded — {len(tickets)} rows")

# -------------------------------------------------------------
# FINAL VERIFICATION
# -------------------------------------------------------------
print("\n" + "=" * 60)
print("VERIFICATION — Row counts from PostgreSQL:")
print("=" * 60)

tables = ['accounts', 'subscriptions', 'churn_events',
          'feature_usage', 'support_tickets']

with engine.connect() as conn:
    for table in tables:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.fetchone()[0]
        print(f"  {table:<25} → {count} rows")

print("\n✓ All tables loaded successfully!")
print("✓ Ready for SQL Analysis (Step 5)")
engine.dispose()