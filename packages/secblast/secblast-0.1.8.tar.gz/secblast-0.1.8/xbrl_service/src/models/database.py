from datetime import date
from typing import Any, Dict

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Date,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from ..config import get_settings


class Base(AsyncAttrs, DeclarativeBase):
    pass


class FinancialStatement(Base):
    """Stores parsed XBRL financial statement data."""

    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cik = Column(BigInteger, nullable=False, index=True)
    accession_number = Column(String(25), nullable=False)
    filing_date = Column(Date, nullable=False)
    form_type = Column(String(20), nullable=False)
    fiscal_year = Column(Integer)
    fiscal_period = Column(String(10))  # Q1, Q2, Q3, Q4, FY
    statement_type = Column(
        String(20), nullable=False
    )  # balance_sheet, income_statement, cash_flow
    period_end = Column(Date, nullable=False)
    currency = Column(String(3), default="USD")
    data = Column(JSONB, nullable=False)  # Structured financial data

    __table_args__ = (
        UniqueConstraint("accession_number", "statement_type", name="uq_statement"),
        Index("idx_financial_statements_cik", "cik"),
        Index("idx_financial_statements_filing_date", "filing_date"),
    )


class XBRLFilingData(Base):
    """Stores complete raw XBRL data for a filing including all facts and linkbases."""

    __tablename__ = "xbrl_filing_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cik = Column(BigInteger, nullable=False, index=True)
    accession_number = Column(String(25), nullable=False, unique=True)
    filing_date = Column(Date, nullable=False)
    form_type = Column(String(20), nullable=False)
    fiscal_year = Column(Integer)
    fiscal_period = Column(String(10))  # Q1, Q2, Q3, Q4, FY
    period_end = Column(Date, nullable=False)

    # Complete XBRL data as JSONB
    all_facts = Column(JSONB, nullable=False)  # All facts keyed by concept name
    presentation_trees = Column(JSONB, nullable=False)  # Hierarchical structure per statement role
    calculation_relationships = Column(JSONB)  # Calculation linkbase relationships
    labels = Column(JSONB)  # Human-readable labels for concepts

    __table_args__ = (
        Index("idx_xbrl_filing_data_cik", "cik"),
        Index("idx_xbrl_filing_data_filing_date", "filing_date"),
        Index("idx_xbrl_filing_data_cik_period", "cik", "period_end"),
    )


# Database engine and session
settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session():
    """Dependency for getting database sessions."""
    async with async_session() as session:
        yield session


async def create_tables():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
