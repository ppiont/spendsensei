"""
Ingest Module - Data Loading and Validation

This module handles synthetic data generation and loading into the database.
"""

from spendsense.ingest.synthetic_generator import (
    generate_user,
    generate_accounts,
    generate_transactions,
    generate_dataset,
    save_dataset,
    load_data_from_json,
    main,
    main_async,
)

__all__ = [
    "generate_user",
    "generate_accounts",
    "generate_transactions",
    "generate_dataset",
    "save_dataset",
    "load_data_from_json",
    "main",
    "main_async",
]
