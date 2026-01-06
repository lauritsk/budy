from sqlmodel import Session, select

from budy.schemas import Category, CategoryRule


def create_category(*, session: Session, name: str, color: str = "white") -> Category:
    """Creates a new category."""
    category = Category(name=name, color=color)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def get_categories(*, session: Session) -> list[Category]:
    """Returns all categories."""
    return list(session.exec(select(Category)).all())


def delete_category(*, session: Session, category_id: int) -> bool:
    """Deletes a category by ID."""
    category = session.get(Category, category_id)
    if not category:
        return False
    session.delete(category)
    session.commit()
    return True


# --- Rules ---


def create_rule(*, session: Session, pattern: str, category_id: int) -> CategoryRule:
    """Creates a new auto-categorization rule."""
    rule = CategoryRule(pattern=pattern.lower(), category_id=category_id)
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return rule


def get_rules(*, session: Session) -> list[tuple[CategoryRule, Category]]:
    """Returns all rules with their associated category."""
    stmt = select(CategoryRule, Category).join(Category)
    return list(session.exec(stmt).all())


def delete_rule(*, session: Session, rule_id: int) -> bool:
    """Deletes a rule by ID."""
    rule = session.get(CategoryRule, rule_id)
    if not rule:
        return False
    session.delete(rule)
    session.commit()
    return True
