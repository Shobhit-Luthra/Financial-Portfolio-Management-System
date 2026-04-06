"""
Seed script: Inserts dummy data into the Financial Portfolio Management System database.

Creates a demo user with a diversified portfolio and realistic transaction history.

Usage:
    python seed_data.py

Demo credentials:
    Email:    demo@portfolio.com
    Password: demo123
"""

import db
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

# ─── Configuration ────────────────────────────────────────────────────────────

DEMO_EMAIL = "demo@portfolio.com"
DEMO_PASSWORD = "demo123"
DEMO_NAME = "Alex Morgan"

# Assets: (symbol, name, type, quantity, avg_buy_price, current_price)
ASSETS = [
    # Stocks
    ("AAPL",  "Apple Inc.",                  "stock",       25,   145.00,  178.50),
    ("MSFT",  "Microsoft Corp.",             "stock",       15,   280.00,  338.20),
    ("GOOGL", "Alphabet Inc.",               "stock",        8,   120.00,  142.65),
    ("AMZN",  "Amazon.com Inc.",             "stock",       12,   130.00,  168.40),
    ("TSLA",  "Tesla Inc.",                  "stock",       10,   210.00,  245.80),
    ("NVDA",  "NVIDIA Corp.",                "stock",        6,   450.00,  620.30),
    # Bonds
    ("BND",   "Vanguard Total Bond ETF",     "bond",        40,    73.50,   75.20),
    ("TLT",   "iShares 20+ Year Treasury",   "bond",        20,    95.00,   98.40),
    # Mutual Funds
    ("VTI",   "Vanguard Total Market Index",  "mutual_fund", 30,   210.00,  228.60),
    ("VXUS",  "Vanguard Intl Stock Index",    "mutual_fund", 25,    52.00,   55.30),
    # Other / Crypto
    ("BTC",   "Bitcoin",                      "other",        0.5, 42000.00, 63500.00),
    ("ETH",   "Ethereum",                     "other",        4,   2200.00,  3350.00),
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def random_date(days_back_start, days_back_end=0):
    """Return a random date between `days_back_start` and `days_back_end` days ago."""
    delta = random.randint(days_back_end, days_back_start)
    return (datetime.utcnow() - timedelta(days=delta)).strftime("%Y-%m-%d")


# ─── Main ─────────────────────────────────────────────────────────────────────

def seed():
    print("🌱 Starting seed …")

    # 1. Clean up any previous demo data
    existing = db.execute_query(
        "SELECT user_id FROM users WHERE email = %s",
        (DEMO_EMAIL,), fetch=True, fetchall=False,
    )
    if existing:
        uid = existing["user_id"]
        print(f"   ↳ Removing old demo user (id={uid}) …")
        db.execute_query("DELETE FROM transactions WHERE user_id = %s", (uid,))
        db.execute_query("DELETE FROM assets WHERE user_id = %s", (uid,))
        db.execute_query("DELETE FROM users WHERE user_id = %s", (uid,))

    # 2. Create demo user
    hashed = generate_password_hash(DEMO_PASSWORD, method="pbkdf2:sha256")
    user_id = db.execute_query(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
        (DEMO_NAME, DEMO_EMAIL, hashed),
    )
    print(f"   ✅ Created user '{DEMO_NAME}' (id={user_id})")

    # 3. Insert assets
    asset_ids = {}  # symbol → asset_id
    for symbol, name, a_type, qty, avg_bp, cur_p in ASSETS:
        aid = db.execute_query(
            "INSERT INTO assets (user_id, symbol, name, type, quantity, avg_buy_price, current_price) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (user_id, symbol, name, a_type, qty, round(avg_bp, 2), round(cur_p, 2)),
        )
        asset_ids[symbol] = aid

    print(f"   ✅ Inserted {len(ASSETS)} assets")

    # 4. Generate realistic transactions
    tx_count = 0

    for symbol, name, a_type, qty, avg_bp, cur_p in ASSETS:
        aid = asset_ids[symbol]

        # --- Initial BUY (3–6 months ago) ---
        initial_qty = round(qty * 0.6, 4)
        initial_price = round(avg_bp * random.uniform(0.92, 1.02), 2)
        initial_total = round(initial_qty * initial_price, 2)
        db.execute_query(
            "INSERT INTO transactions "
            "(user_id, asset_id, type, quantity, price_per_unit, total_amount, transaction_date, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, aid, "buy", initial_qty, initial_price, initial_total,
             random_date(180, 90), "Initial purchase"),
        )
        tx_count += 1

        # --- Second BUY / DCA (1–3 months ago) ---
        second_qty = round(qty * 0.3, 4)
        second_price = round(avg_bp * random.uniform(0.97, 1.08), 2)
        second_total = round(second_qty * second_price, 2)
        db.execute_query(
            "INSERT INTO transactions "
            "(user_id, asset_id, type, quantity, price_per_unit, total_amount, transaction_date, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, aid, "buy", second_qty, second_price, second_total,
             random_date(90, 30), "Dollar-cost averaging"),
        )
        tx_count += 1

        # --- Third BUY (recent, last month) ---
        third_qty = round(qty * 0.1, 4)
        third_price = round(cur_p * random.uniform(0.95, 1.0), 2)
        third_total = round(third_qty * third_price, 2)
        db.execute_query(
            "INSERT INTO transactions "
            "(user_id, asset_id, type, quantity, price_per_unit, total_amount, transaction_date, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, aid, "buy", third_qty, third_price, third_total,
             random_date(30, 1), "Recent top-up"),
        )
        tx_count += 1

    # --- A few SELL transactions for realism ---
    sell_targets = [("AAPL", 3), ("TSLA", 2), ("BTC", 0.05)]
    for symbol, sell_qty in sell_targets:
        aid = asset_ids.get(symbol)
        if not aid:
            continue
        asset_info = next((a for a in ASSETS if a[0] == symbol), None)
        if not asset_info:
            continue
        sell_price = round(asset_info[5] * random.uniform(0.98, 1.05), 2)
        sell_total = round(sell_qty * sell_price, 2)
        db.execute_query(
            "INSERT INTO transactions "
            "(user_id, asset_id, type, quantity, price_per_unit, total_amount, transaction_date, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, aid, "sell", sell_qty, sell_price, sell_total,
             random_date(20, 2), "Partial profit booking"),
        )
        tx_count += 1

    # --- A few DIVIDEND transactions ---
    dividend_targets = [("AAPL", 22.50), ("MSFT", 18.00), ("BND", 45.60), ("VTI", 32.10)]
    for symbol, div_amount in dividend_targets:
        aid = asset_ids.get(symbol)
        if not aid:
            continue
        db.execute_query(
            "INSERT INTO transactions "
            "(user_id, asset_id, type, quantity, price_per_unit, total_amount, transaction_date, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, aid, "dividend", 0, 0, div_amount,
             random_date(15, 1), "Quarterly dividend"),
        )
        tx_count += 1

    # --- A SIP transaction ---
    sip_targets = [("VTI", 2, 225.40), ("VXUS", 3, 54.10)]
    for symbol, sip_qty, sip_price in sip_targets:
        aid = asset_ids.get(symbol)
        if not aid:
            continue
        sip_total = round(sip_qty * sip_price, 2)
        db.execute_query(
            "INSERT INTO transactions "
            "(user_id, asset_id, type, quantity, price_per_unit, total_amount, transaction_date, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, aid, "sip", sip_qty, sip_price, sip_total,
             random_date(28, 7), "Systematic investment plan"),
        )
        tx_count += 1

    print(f"   ✅ Inserted {tx_count} transactions")
    print()
    print("🎉 Seed complete!")
    print(f"   Login → Email: {DEMO_EMAIL}  |  Password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    seed()
