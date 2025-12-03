from pathlib import Path

import polars as pl
from sqlmodel import SQLModel

from budy.models import Transaction


class BaseBankImporter(SQLModel):
    delimiter: str = ","
    encoding: str = "utf-8"
    decimal: str = "."
    date_col: str
    amount_col: str
    debit_credit_col: str
    debit_value: str = "D"

    def process_file(self, file_path: Path) -> list[Transaction]:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            df = pl.read_csv(
                file_path,
                separator=self.delimiter,
                decimal_comma=(self.decimal == ","),
                encoding=self.encoding,
            )

            required_cols = {self.date_col, self.amount_col, self.debit_credit_col}

            if not required_cols.issubset(df.columns):
                missing = required_cols - set(df.columns)
                raise ValueError(f"CSV missing required columns: {missing}")

            result = (
                df.lazy()
                .filter(
                    pl.col(self.debit_credit_col).str.strip_chars().str.to_uppercase()
                    == self.debit_value
                )
                .with_columns(
                    pl.col(self.date_col).str.strptime(pl.Date).alias("parsed_date")
                )
                .with_columns(
                    (pl.col(self.amount_col).abs() * 100)
                    .round()
                    .cast(pl.Int64)
                    .alias("amount_cents")
                )
                .drop_nulls(subset=["parsed_date", "amount_cents"])
                .filter(pl.col("amount_cents") > 0)
                .select(["parsed_date", "amount_cents"])
            ).collect()

            return [
                Transaction(entry_date=row["parsed_date"], amount=row["amount_cents"])
                for row in result.to_dicts()
            ]

        except Exception as e:
            raise RuntimeError(f"Error parsing CSV: {e}") from e
