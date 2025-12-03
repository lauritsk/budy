from pathlib import Path
from typing import Optional

import polars as pl
from sqlmodel import SQLModel

from budy.models import Transaction


def get_bank_importers() -> dict[str, type["BaseBankImporter"]]:
    """
    Dynamically discover all BaseBankImporter subclasses.
    Returns a dict mapping 'bank_name' -> ImporterClass.
    """
    banks = {}
    for cls in BaseBankImporter.__subclasses__():
        name = cls.__name__.replace("Importer", "").lower()
        banks[name] = cls
    return banks


class ImportResult(SQLModel):
    success: bool
    count: int = 0
    message: str = ""
    error: Optional[str] = None


class BaseBankImporter(SQLModel):
    delimiter: str = ","
    encoding: str = "utf-8"
    decimal: str = "."
    date_fmt: str = "%Y-%m-%d"

    # Column mapping
    date_col: str
    amount_col: str
    debit_credit_col: str
    debit_value: str = "D"

    def process_file(self, file_path: Path) -> tuple[list[Transaction], ImportResult]:
        if not file_path.exists():
            return [], ImportResult(
                success=False, message=f"File not found: {file_path}"
            )

        try:
            # 1. READ
            # Polars handles decimal conversion natively via decimal_comma argument
            df = pl.read_csv(
                file_path,
                separator=self.delimiter,
                decimal_comma=(self.decimal == ","),
                encoding=self.encoding,
            )

            # Check for required columns
            required_cols = {self.date_col, self.amount_col, self.debit_credit_col}
            if not required_cols.issubset(df.columns):
                missing = required_cols - set(df.columns)
                return [], ImportResult(
                    success=False,
                    message="CSV missing required columns.",
                    error=f"Missing: {missing}",
                )

            # 2. FILTER & TRANSFORM (Lazy API)
            q = (
                df.lazy()
                # Filter for Expenses (Debit)
                .filter(
                    pl.col(self.debit_credit_col).str.strip_chars().str.to_uppercase()
                    == self.debit_value
                )
                # Parse Dates
                .with_columns(
                    pl.col(self.date_col)
                    .str.strptime(pl.Date, format=self.date_fmt, strict=False)
                    .alias("parsed_date")
                )
                # Parse Amounts: Absolute value -> Cents -> Integer
                .with_columns(
                    (pl.col(self.amount_col).abs() * 100)
                    .round()
                    .cast(pl.Int64)
                    .alias("amount_cents")
                )
                # Drop rows where date parsing failed or amount is invalid
                .drop_nulls(subset=["parsed_date", "amount_cents"])
                .filter(pl.col("amount_cents") > 0)
                .select(["parsed_date", "amount_cents"])
            )

            # Execute Query
            result_df = q.collect()

            if result_df.height == 0:
                return [], ImportResult(
                    success=True,
                    count=0,
                    message=f"No valid expenses found in {file_path.name}.",
                )

            # 3. CONVERT TO MODELS
            transactions = [
                Transaction(entry_date=row["parsed_date"], amount=row["amount_cents"])
                for row in result_df.to_dicts()
            ]

            return transactions, ImportResult(
                success=True,
                count=len(transactions),
                message=f"Parsed {len(transactions)} transactions.",
            )

        except Exception as e:
            return [], ImportResult(
                success=False, message="Error parsing CSV", error=str(e)
            )


class LHVImporter(BaseBankImporter):
    delimiter: str = ","
    encoding: str = "utf-8"
    decimal: str = "."
    dayfirst: bool = False
    date_col: str = "Kuupäev"
    amount_col: str = "Summa"
    debit_credit_col: str = "Deebet/Kreedit (D/C)"
    debit_value: str = "D"


class SEBImporter(BaseBankImporter):
    delimiter: str = ";"
    encoding: str = "utf-8"
    decimal: str = ","
    dayfirst: bool = True
    date_col: str = "Kuupäev"
    amount_col: str = "Summa"
    debit_credit_col: str = "Deebet/Kreedit (D/C)"
    debit_value: str = "D"


class SwedbankImporter(BaseBankImporter):
    delimiter: str = ";"
    encoding: str = "utf-8"
    decimal: str = ","
    dayfirst: bool = True
    date_col: str = "Kuupäev"
    amount_col: str = "Summa"
    debit_credit_col: str = "Deebet/Kreedit"
    debit_value: str = "D"
