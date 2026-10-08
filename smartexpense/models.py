from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, func

db = SQLAlchemy()
DEFAULT_CATEGORIES = ('Food', 'Travel', 'Rent', 'Utilities', 'Shopping', 'Health', 'Education', 'Other')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary, nullable=False)

class LoginSession(db.Model):
    token = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String(80), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'name'),)

class Transaction(db.Model):
    """Shared contract for the teammate's SEB-F-005–010 implementation."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(7), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    txn_date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    payment_mode = db.Column(db.String(30))
    source = db.Column(db.String(100))
    note = db.Column(db.Text)
    __table_args__ = (
        db.CheckConstraint("type IN ('expense', 'income')"),
        db.CheckConstraint('amount > 0'),
        db.CheckConstraint("type != 'expense' OR (category_id IS NOT NULL AND payment_mode IS NOT NULL)"),
        db.CheckConstraint("type != 'income' OR source IS NOT NULL"),
        db.Index('ix_transaction_owner_date', 'user_id', 'txn_date'),
        db.Index('ix_transaction_owner_category', 'user_id', 'category_id'),
    )

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.String(7), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    limit = db.Column(db.Numeric(12, 2), nullable=False)
    __table_args__ = (db.CheckConstraint('"limit" > 0'),)

# NULL category identifies the monthly budget; coalesce prevents duplicate monthly rows.
Index('uq_budget_owner_month_scope', Budget.user_id, Budget.month, func.coalesce(Budget.category_id, 0), unique=True)
