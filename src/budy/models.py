from datetime import date

from sqlmodel import Field, SQLModel


class Transaction(SQLModel, table=True):
    """Class that defines all transactions."""

    id: int | None = Field(default=None, primary_key=True)
    amount: int
    entry_date: date = Field(index=True)
    receiver: str | None = Field(default=None, index=True)
    description: str | None = Field(default=None)


class Budget(SQLModel, table=True):
    """Class that defines all budgets."""

    id: int | None = Field(default=None, primary_key=True)
    amount: int
    target_month: int = Field(index=True)
    target_year: int = Field(index=True)
