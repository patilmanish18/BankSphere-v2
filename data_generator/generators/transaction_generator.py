"""Generates synthetic transaction records, tied to existing accounts."""

import random
from collections import defaultdict
from faker import Faker
from data_generator.config import RANDOM_SEED

fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

TRANSACTION_TYPES = ["DEPOSIT", "WITHDRAWAL", "TRANSFER", "PAYMENT"]
TYPE_WEIGHTS = [0.35, 0.30, 0.20, 0.15]

DESCRIPTIONS = {
    "DEPOSIT": ["Salary credit", "Cash deposit", "Cheque deposit", "Interest credit"],
    "WITHDRAWAL": ["ATM withdrawal", "Cash withdrawal", "Branch withdrawal"],
    "TRANSFER": ["NEFT transfer", "IMPS transfer", "UPI transfer"],
    "PAYMENT": ["Bill payment", "Merchant payment", "Loan EMI payment"],
}


def generate_transactions(accounts: list[dict], count: int) -> list[dict]:
    """Generate `count` synthetic transaction records.

    Critical: dates are generated PER ACCOUNT and sorted BEFORE the running
    balance is applied, so that sorting any account's transactions by
    transaction_date always produces a mathematically consistent ledger.
    Generating dates and balance updates independently (as an earlier
    version of this function did) breaks that guarantee.
    """
    # Decide how many transactions each account gets
    account_indices = [random.randrange(len(accounts)) for _ in range(count)]
    counts_per_account = defaultdict(int)
    for idx in account_indices:
        counts_per_account[idx] += 1

    transactions = []

    for account_index, n in counts_per_account.items():
        account = accounts[account_index]

        # Generate this account's transaction dates FIRST, then sort —
        # this is the fix. Balance math below now walks in true time order.
        dates = sorted(
            fake.date_time_between(start_date=account["opened_date"], end_date="now")
            for _ in range(n)
        )

        running_balance = account["balance"]

        for txn_date in dates:
            txn_type = random.choices(TRANSACTION_TYPES, weights=TYPE_WEIGHTS, k=1)[0]
            amount = round(random.uniform(100, 50000), 2)

            if txn_type == "DEPOSIT":
                new_balance = running_balance + amount
            else:
                amount = min(amount, running_balance + 5000)
                new_balance = running_balance - amount

            new_balance = round(new_balance, 2)

            transactions.append({
                "account_index": account_index,
                "transaction_type": txn_type,
                "amount": round(amount, 2),
                "balance_after": new_balance,
                "description": random.choice(DESCRIPTIONS[txn_type]),
                "transaction_date": txn_date,
            })

            running_balance = new_balance

    # Shuffle so the output table isn't visibly grouped by account —
    # matches how a real transactions table would actually look, while
    # each account's own history remains internally chronological.
    random.shuffle(transactions)
    return transactions


if __name__ == "__main__":
    from data_generator.generators.branch_generator import generate_branches
    from data_generator.generators.customer_generator import generate_customers
    from data_generator.generators.account_generator import generate_accounts

    branches = generate_branches(5)
    customers = generate_customers(5)
    accounts = generate_accounts(customers, branches, 5)
    sample = generate_transactions(accounts, 15)

    # Self-verification: group by account, sort by date, confirm the
    # ledger math actually holds in chronological order.
    by_account = defaultdict(list)
    for txn in sample:
        by_account[txn["account_index"]].append(txn)

    for account_index, txns in sorted(by_account.items()):
        txns.sort(key=lambda t: t["transaction_date"])
        print(f"\n--- Account {account_index} (start balance: {accounts[account_index]['balance']}) ---")
        running = accounts[account_index]["balance"]
        for t in txns:
            expected = running + t["amount"] if t["transaction_type"] == "DEPOSIT" else running - t["amount"]
            expected = round(expected, 2)
            check = "OK" if abs(expected - t["balance_after"]) < 0.01 else "MISMATCH"
            print(f"  {t['transaction_date']} | {t['transaction_type']:10} | "
                  f"amt={t['amount']:>10.2f} | balance_after={t['balance_after']:>12.2f} | "
                  f"expected={expected:>12.2f} | {check}")
            running = t["balance_after"]
