import calendar
from collections import defaultdict
from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path
from statistics import mean, median

from sqlmodel import Session, asc, col, desc, func, or_, select

import budy.importers as importers
from budy.database import engine
from budy.models import Budget, Transaction


from collections.abc import Callable








from pathlib import Path

import budy.importers as importers


import statistics


def get_yearly_report_data(year: int) -> list[dict]:
    """
    Gathers all data needed for the yearly report.
    """
    monthly_data = []
    with Session(engine) as session:
        for month in range(1, 13):
            month_name = calendar.month_name[month]
            budget = session.exec(
                select(Budget).where(
                    Budget.target_year == year, Budget.target_month == month
                )
            ).first()

            _, last_day = calendar.monthrange(year, month)
            start_date = date(year, month, 1)
            end_date = date(year, month, last_day)

            total_spent = (
                session.scalar(
                    select(func.sum(Transaction.amount)).where(
                        Transaction.entry_date >= start_date,
                        Transaction.entry_date <= end_date,
                    )
                )
                or 0
            )

            monthly_data.append(
                {
                    "budget": budget,
                    "total_spent": total_spent,
                    "month_name": month_name,
                    "target_year": year,
                }
            )
    return monthly_data


def get_weekday_report_data() -> list[dict]:
    """
    Analyzes spending habits by day of the week.
    """
    with Session(engine) as session:
        transactions = session.exec(select(Transaction)).all()
        if not transactions:
            return []

        day_buckets = defaultdict(list)
        for t in transactions:
            day_buckets[t.entry_date.weekday()].append(t.amount)

        report_data = []
        for day_idx in range(7):
            amounts = day_buckets[day_idx]
            if not amounts:
                report_data.append(
                    {
                        "day_name": calendar.day_name[day_idx],
                        "avg_amount": 0,
                        "total_amount": 0,
                        "count": 0,
                    }
                )
                continue

            report_data.append(
                {
                    "day_name": calendar.day_name[day_idx],
                    "avg_amount": mean(amounts),
                    "total_amount": sum(amounts),
                    "count": len(amounts),
                }
            )
        return report_data


def get_volatility_report_data(year: int | None) -> dict:
    """
    Calculates spending volatility and identifies outliers.
    """
    with Session(engine) as session:
        query = select(Transaction)
        if year:
            query = query.where(
                Transaction.entry_date >= date(year, 1, 1),
                Transaction.entry_date <= date(year, 12, 31),
            )

        transactions = session.exec(query.order_by(desc(Transaction.amount))).all()
        if not transactions:
            return {}

        amounts = [t.amount for t in transactions]
        try:
            stdev = statistics.stdev(amounts)
        except statistics.StatisticsError:
            stdev = 0

        return {
            "total_count": len(amounts),
            "avg_amount": statistics.mean(amounts),
            "stdev_amount": stdev,
            "outliers": transactions[:5],
        }


def get_top_payees(year: int | None, limit: int) -> list[tuple[str, int, int, int]]:
    """
    Ranks payees by total spending for a given year or all time.
    """
    with Session(engine) as session:
        query = select(Transaction)
        if year:
            query = query.where(
                Transaction.entry_date >= date(year, 1, 1),
                Transaction.entry_date <= date(year, 12, 31),
            )

        transactions = session.exec(query).all()
        if not transactions:
            return []

        grouped = defaultdict(list)
        for t in transactions:
            name = (t.receiver or "Unknown").strip()
            if not name:
                name = "Unknown"
            grouped[name].append(t.amount)

        summary = []
        for name, amounts in grouped.items():
            total = sum(amounts)
            count = len(amounts)
            avg = int(total / count)
            summary.append((name, count, total, avg))

        summary.sort(key=lambda x: x[2], reverse=True)
        return summary[:limit]


def search_transactions(query: str, limit: int) -> list[Transaction]:
    """
    Searches for transactions by a keyword in the receiver or description.
    """
    with Session(engine) as session:
        pattern = f"%{query}%"
        stmt = (
            select(Transaction)
            .where(
                or_(
                    col(Transaction.receiver).ilike(pattern),
                    col(Transaction.description).ilike(pattern),
                )
            )
            .order_by(desc(Transaction.entry_date))
            .limit(limit)
        )
        return list(session.exec(stmt).all())


def import_transactions(
    bank: str, file_path: Path, dry_run: bool
) -> dict:
    """
    Imports transactions from a bank CSV file.
    """
    if bank.lower() == "lhv":
        importer = importers.LHVImporter()
    elif bank.lower() == "seb":
        importer = importers.SEBImporter()
    elif bank.lower() == "swedbank":
        importer = importers.SwedbankImporter()
    else:
        raise ValueError(f"No importer found for {bank}")

    transactions = importer.process_file(file_path)

    if not dry_run and transactions:
        with Session(engine) as session:
            session.add_all(transactions)
            session.commit()

    return {"transactions": transactions, "count": len(transactions)}


def create_transaction(amount: float, entry_date: date | None) -> Transaction:
    """
    Creates and saves a new transaction.
    """
    with Session(engine) as session:
        final_date = entry_date if entry_date else date.today()
        amount_cents = int(round(amount * 100))
        transaction = Transaction(amount=amount_cents, entry_date=final_date)
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction


def save_budget_suggestions(suggestions: list[dict]) -> int:
    """
    Saves a list of budget suggestions to the database.
    """
    with Session(engine) as session:
        count = 0
        for item in suggestions:
            if item["existing"]:
                item["existing"].amount = item["amount"]
                session.add(item["existing"])
            else:
                new_budget = Budget(
                    target_year=item["year"],
                    target_month=item["month"],
                    amount=item["amount"],
                )
                session.add(new_budget)
            count += 1
        session.commit()
    return count


def generate_budgets_suggestions(target_year: int, force: bool) -> list[dict]:
    """
    Generates budget suggestions for a given year based on historical data.
    """
    suggestions = []
    with Session(engine) as session:
        existing_budgets = session.exec(
            select(Budget).where(Budget.target_year == target_year)
        ).all()
        existing_map = {b.target_month: b for b in existing_budgets}

        for month in range(1, 13):
            month_name = calendar.month_name[month]

            if month in existing_map and not force:
                continue

            suggested_amount = suggest_budget_amount(session, month, target_year)

            if suggested_amount > 0:
                suggestions.append(
                    {
                        "month": month,
                        "month_name": month_name,
                        "amount": suggested_amount,
                        "existing": existing_map.get(month),
                    }
                )
    return suggestions


def add_or_update_budget(


    target_amount: float,


    target_month: int,


    target_year: int,


    confirmation_callback: Callable[[str], bool],


) -> dict:


    """


    Adds a new budget or updates an existing one after confirmation.


    Returns a dict with the result of the operation.


    """


    with Session(engine) as session:


        month_name = calendar.month_name[target_month]


        target_cents = int(round(target_amount * 100))





        existing_budget = session.exec(


            select(Budget).where(


                Budget.target_year == target_year,


                Budget.target_month == target_month,


            )


        ).first()





        if existing_budget:


            old_amount = existing_budget.amount


            if not confirmation_callback(


                f"A budget for {month_name} {target_year} already exists. Overwrite?"


            ):


                return {"action": "cancelled"}





            existing_budget.amount = target_cents


            session.add(existing_budget)


            session.commit()


            return {


                "action": "updated",


                "old_amount": old_amount,


                "new_amount": target_cents,


                "month_name": month_name,


                "year": target_year,


            }





        new_budget = Budget(


            amount=target_cents,


            target_month=target_month,


            target_year=target_year,


        )


        session.add(new_budget)


        session.commit()


        return {


            "action": "created",


            "new_amount": target_cents,


            "month_name": month_name,


            "year": target_year,


        }








def generate_monthly_report_data(


    target_month: int, target_year: int


) -> dict:
    """
    Generates all data needed for the monthly budget status report.
    """
    today = date.today()
    month_name = calendar.month_name[target_month]
    _, last_day = calendar.monthrange(target_year, target_month)
    start_date = date(target_year, target_month, 1)
    end_date = date(target_year, target_month, last_day)

    with Session(engine) as session:
        budget = session.exec(
            select(Budget).where(
                Budget.target_year == target_year,
                Budget.target_month == target_month,
            )
        ).first()

        total_spent = (
            session.scalar(
                select(func.sum(Transaction.amount)).where(
                    Transaction.entry_date >= start_date,
                    Transaction.entry_date <= end_date,
                )
            )
            or 0
        )

    report_data = {
        "budget": budget,
        "total_spent": total_spent,
        "month_name": month_name,
        "target_year": target_year,
        "forecast": None,
    }

    is_current_month = (target_month == today.month) and (target_year == today.year)
    if is_current_month:
        days_passed = today.day
        if days_passed == 0:
            days_passed = 1

        avg_per_day = total_spent / days_passed
        projected_total = avg_per_day * last_day
        projected_overage = (projected_total - budget.amount) if budget else None

        report_data["forecast"] = {
            "avg_per_day": avg_per_day,
            "projected_total": projected_total,
            "projected_overage": projected_overage,
        }

    return report_data


def get_budgets(
    target_year: int, offset: int, limit: int
) -> list[tuple[int, Budget | None]]:
    """
    Fetches budgets for a given year, with optional pagination.
    """
    with Session(engine) as session:
        budgets = list(
            session.exec(
                select(Budget)
                .where(Budget.target_year == target_year)
                .order_by(asc(Budget.target_month))
                .offset(offset)
                .limit(limit)
            ).all()
        )

        budget_map = {b.target_month: b for b in budgets}
        all_months_data = []

        for month in range(1, 13):
            all_months_data.append((month, budget_map.get(month)))

        return all_months_data[offset : offset + limit]


def get_transactions(offset: int, limit: int) -> list[tuple[date, list[Transaction]]]:
    """
    Fetches transactions for a date range determined by offset and limit.
    """
    today = date.today()
    start_date = today - timedelta(days=offset)
    dates_desc = [start_date - timedelta(days=i) for i in range(limit)]
    dates_to_show = sorted(dates_desc)

    if not dates_to_show:
        return []

    min_date = dates_to_show[0]
    max_date = dates_to_show[-1]

    with Session(engine) as session:
        transactions = list(
            session.exec(
                select(Transaction)
                .where(Transaction.entry_date >= min_date)
                .where(Transaction.entry_date <= max_date)
                .order_by(asc(Transaction.entry_date))
            ).all()
        )

        tx_map = defaultdict(list)
        for t in transactions:
            tx_map[t.entry_date].append(t)

        display_data = []
        for d in dates_to_show:
            display_data.append((d, tx_map.get(d, [])))

        return display_data


def get_monthly_totals(
    session: Session, start_date: date, end_date: date
) -> dict[tuple[int, int], int]:
    """
    Fetches transactions within a range and aggregates them by (year, month).
    Returns a dict: {(year, month): total_cents}
    """
    transactions = session.exec(
        select(Transaction).where(
            Transaction.entry_date >= start_date,
            Transaction.entry_date < end_date,
        )
    ).all()

    totals = defaultdict(int)
    for t in transactions:
        totals[(t.entry_date.year, t.entry_date.month)] += t.amount

    return totals


def suggest_budget_amount(session: Session, target_month: int, target_year: int) -> int:
    """
    Calculates a suggested budget amount (in cents) based on historical data.
    Algorithm: Average of (Median of Recent Trend) and (Median of Historical Seasonality).
    """
    target_date = date(target_year, target_month, 1)

    # 1. Recent Trend: Look at the last 6 months
    # We go back ~180 days. A simple approximation is fine here.
    trend_start = date(target_year, target_month, 1)  # Placeholder
    # Logic to subtract 6 months
    y, m = target_year, target_month
    for _ in range(6):
        m -= 1
        if m < 1:
            m = 12
            y -= 1
    trend_start = date(y, m, 1)

    recent_data = get_monthly_totals(session, trend_start, target_date)
    recent_values = list(recent_data.values())

    # 2. Seasonality: Look at this exact month in the last 3 years
    history_values = []
    for i in range(1, 4):
        prev_year = target_year - i
        # Get totals for that specific month
        # We construct a range of [1st, 1st of next month)
        m_start = date(prev_year, target_month, 1)
        # simplistic next month calculation
        next_m = target_month + 1
        next_y = prev_year
        if next_m > 12:
            next_m = 1
            next_y += 1
        m_end = date(next_y, next_m, 1)

        totals = get_monthly_totals(session, m_start, m_end)
        if totals:
            history_values.extend(totals.values())

    signals = []

    if recent_values:
        signals.append(median(recent_values))

    if history_values:
        signals.append(median(history_values))

    if not signals:
        return 0

    # Return the mean of our signals (Trend + Seasonality)
    return int(mean(signals))
