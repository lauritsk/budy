import csv
from typer.testing import CliRunner
from sqlmodel import Session, SQLModel, select
from budy import app
from budy.database import engine
from budy.schemas import Category, Transaction

runner = CliRunner()


def reset_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def test_auto_categorization(tmp_path):
    reset_db()

    # 1. Setup Category and Rule
    result = runner.invoke(app, ["categories", "add", "Entertainment"])
    assert result.exit_code == 0

    with Session(engine) as session:
        cat = session.exec(
            select(Category).where(Category.name == "Entertainment")
        ).one()
        cat_id = cat.id

    # "Netflix" rule
    result = runner.invoke(
        app, ["categories", "rules", "add", "Netflix", "-c", str(cat_id)]
    )
    assert result.exit_code == 0

    # 2. Create CSV (LHV format as per config)
    csv_file = tmp_path / "statement.csv"
    header = [
        "Kuupäev",
        "Saaja/maksja nimi",
        "Selgitus",
        "Summa",
        "Deebet/Kreedit (D/C)",
    ]
    data = [
        ["2023-01-01", "Netflix Services", "Monthly Sub", "15.00", "D"],
        ["2023-01-02", "Unknown Store", "Food", "50.00", "D"],
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

    # 3. Import
    result = runner.invoke(
        app, ["transactions", "import", "--bank", "lhv", "--file", str(csv_file)]
    )
    assert result.exit_code == 0

    # 4. Verify Categorization
    with Session(engine) as session:
        # Netflix txn
        txn1 = session.exec(select(Transaction).where(Transaction.amount == 1500)).one()
        assert txn1.category_id == cat_id

        # Unknown txn
        txn2 = session.exec(select(Transaction).where(Transaction.amount == 5000)).one()
        assert txn2.category_id is None


def test_rule_management():
    reset_db()
    # Add category
    runner.invoke(app, ["categories", "add", "TestCat"])
    with Session(engine) as session:
        cat = session.exec(select(Category)).one()

    # Add rule
    result = runner.invoke(
        app, ["categories", "rules", "add", "testpattern", "-c", str(cat.id)]
    )
    assert result.exit_code == 0
    assert "Added rule" in result.stdout

    # List rules
    result = runner.invoke(app, ["categories", "rules", "list"])
    assert result.exit_code == 0
    assert "testpattern" in result.stdout
    assert "TestCat" in result.stdout

    # Get Rule ID (from list output or DB)
    # We'll just fetch from DB
    from budy.schemas import CategoryRule

    with Session(engine) as session:
        rule = session.exec(select(CategoryRule)).one()
        rule_id = rule.id

    # Delete rule
    result = runner.invoke(
        app, ["categories", "rules", "delete", str(rule_id), "--force"]
    )
    assert result.exit_code == 0
    assert "Deleted rule" in result.stdout

    with Session(engine) as session:
        rules = session.exec(select(CategoryRule)).all()
        assert len(rules) == 0
