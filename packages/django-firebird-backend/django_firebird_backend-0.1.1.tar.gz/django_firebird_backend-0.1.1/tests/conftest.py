"""
Pytest configuration and fixtures for django-firebird tests.
"""

from unittest.mock import MagicMock

# Configure Django settings before any tests run
import django.conf

import pytest

if not django.conf.settings.configured:
    django.conf.settings.configure(
        DEBUG=True,
        DATABASES={},
        USE_TZ=False,
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    )


@pytest.fixture
def mock_connection():
    """Create a mock database connection."""
    connection = MagicMock()
    connection.vendor = "firebird"
    connection.settings_dict = {
        "NAME": "/path/to/database.fdb",
        "USER": "SYSDBA",
        "PASSWORD": "masterkey",
        "HOST": "localhost",
        "PORT": "3050",
        "OPTIONS": {"charset": "UTF8"},
    }
    # Simulate Firebird 2.5
    connection.firebird_version = (2, 5)
    return connection


@pytest.fixture
def mock_cursor():
    """Create a mock database cursor."""
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    return cursor


@pytest.fixture
def mock_introspection_data():
    """
    Sample introspection data for testing.

    Represents a simple e-commerce schema:
    - COMPANY (no FKs) - root table
    - CUSTOMER (FK to COMPANY)
    - ORDER (FK to COMPANY, CUSTOMER)
    - PRODUCT (FK to COMPANY)
    - ORDER_ITEM (FK to ORDER, PRODUCT)
    """
    return {
        "tables": ["COMPANY", "CUSTOMER", "ORDER", "PRODUCT", "ORDER_ITEM"],
        "relations": {
            "COMPANY": {},
            "CUSTOMER": {"COMPANY_ID": ("COMPANY", "ID")},
            "ORDER": {
                "COMPANY_ID": ("COMPANY", "ID"),
                "CUSTOMER_ID": ("CUSTOMER", "ID"),
            },
            "PRODUCT": {
                "COMPANY_ID": ("COMPANY", "ID"),
            },
            "ORDER_ITEM": {
                "ORDER_ID": ("ORDER", "ID"),
                "PRODUCT_ID": ("PRODUCT", "ID"),
            },
        },
    }


@pytest.fixture
def mock_cyclic_data():
    """
    Sample data with circular dependencies.

    A -> B -> C -> A (cycle)
    D -> A (no cycle, but depends on cyclic table)
    """
    return {
        "tables": ["A", "B", "C", "D"],
        "relations": {
            "A": {"B_ID": ("B", "ID")},
            "B": {"C_ID": ("C", "ID")},
            "C": {"A_ID": ("A", "ID")},
            "D": {"A_ID": ("A", "ID")},
        },
    }


@pytest.fixture
def mock_complex_data():
    """
    Complex schema with multiple dependency levels.

           ┌─────┐
           │  A  │ (no deps)
           └──┬──┘
              │
        ┌─────┴─────┐
        ▼           ▼
    ┌─────┐     ┌─────┐
    │  B  │     │  C  │
    └──┬──┘     └──┬──┘
        │           │
        └─────┬─────┘
              ▼
          ┌─────┐
          │  D  │ (deps on B and C)
          └──┬──┘
              │
              ▼
          ┌─────┐
          │  E  │
          └─────┘
    """
    return {
        "tables": ["A", "B", "C", "D", "E"],
        "relations": {
            "A": {},
            "B": {"A_ID": ("A", "ID")},
            "C": {"A_ID": ("A", "ID")},
            "D": {
                "B_ID": ("B", "ID"),
                "C_ID": ("C", "ID"),
            },
            "E": {"D_ID": ("D", "ID")},
        },
    }


@pytest.fixture
def mock_self_referential_data():
    """
    Schema with self-referential FK.

    CATEGORY (parent_id -> CATEGORY)
    ITEM (category_id -> CATEGORY)
    """
    return {
        "tables": ["CATEGORY", "ITEM"],
        "relations": {
            "CATEGORY": {"PARENT_ID": ("CATEGORY", "ID")},
            "ITEM": {"CATEGORY_ID": ("CATEGORY", "ID")},
        },
    }
