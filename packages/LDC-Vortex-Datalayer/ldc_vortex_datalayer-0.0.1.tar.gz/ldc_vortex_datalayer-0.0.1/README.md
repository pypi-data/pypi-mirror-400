# LDC Vortex Data Layer

A comprehensive data access layer for Vortex Django applications, providing database operations, Redis caching, entity mappers, and business flow operations.

## Features

| Module | Description |
|--------|-------------|
| **Base Layer** | Database connection management, query execution, transaction handling |
| **Entity Mappers** | Data mappers for loans, investments, wallets, accounts, lenders, etc. |
| **Flow Operations** | Business logic flows (redemption, repayment, portfolio, dashboard) |
| **Redis Integration** | Unified caching layer with type-safe get/set operations |
| **Cache Manager** | High-level caching patterns with fallback to database |
| **Constants** | Centralized constants for transaction types, statuses, filters |
| **Helpers** | Date utilities, generic utilities, master account caching |

## Installation

```bash
pip install LDC_Vortex-Datalayer
```

## Requirements

- Python 3.10+
- Django 5.2+
- PostgreSQL (with psycopg 3.x)
- Redis 5.0+

## Quick Start

### Django Settings Configuration

```python
# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vortex_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Redis Configuration
IOS_REDIS_CACHE = "redis://localhost:6379/0"
```

### Using Base Data Layer

```python
from repository.base_layer import BaseDataLayer

class UserRepository(BaseDataLayer):
    def __init__(self):
        super().__init__(db_alias="default")
    
    def get_user_by_id(self, user_id: int) -> dict:
        sql = "SELECT * FROM users WHERE id = %s"
        return self.execute_fetch_one(sql, params=[user_id])
    
    def get_active_users(self) -> list:
        sql = "SELECT * FROM users WHERE status = 'ACTIVE'"
        return self.execute_fetch_all(sql)
```

### Using Redis Utilities

```python
from repository import redis_utils

# Get with automatic type conversion
user = redis_utils.get("user:123", dict)      # Returns dict or None
count = redis_utils.get("counter", int)        # Returns int or None
name = redis_utils.get("name", str)            # Returns str or None
data = redis_utils.get("key")                  # Returns raw bytes (backward compatible)

# Set with automatic serialization
redis_utils.set("user:123", {"name": "John", "age": 30}, ttl=3600)
redis_utils.set("counter", 42, ttl=1800)

# Other operations
redis_utils.delete("user:123")
redis_utils.exists("user:123")
redis_utils.keys("user:*")
```

### Using Cache Manager

```python
from repository.cache_manager import CacheManager

# Get or set pattern with database fallback
result = CacheManager.get_or_set(
    cache_identifier="user_123",
    db_callback=lambda: fetch_user_from_db(123),
    cache_key_prefix="USER_DATA",
    ttl=1800,
    return_type=dict
)

# Invalidate cache
CacheManager.invalidate("user_123", cache_key_prefix="USER_DATA")
```

### Using Constants

```python
from repository.constants import TransactionStatus, LoanStatus, WalletTransactionType

if transaction.status == TransactionStatus.SUCCESS:
    print("Transaction completed")

if loan.status == LoanStatus.FUNDED:
    process_funded_loan(loan)
```

### Using Entity Mappers

```python
from repository.entity.loan import Loan
from repository.entity.wallet_transaction import WalletTransaction

# Loan operations
loan_repo = Loan()
loan_details = loan_repo.get_loan_by_id(loan_id)

# Wallet transactions
wallet_repo = WalletTransaction()
transactions = wallet_repo.get_transaction_list(lender_id, filters)
```

---

## Package Structure

```
repository/
├── base_layer.py          # Base database operations
├── redis_utils.py         # Redis connection and operations
├── cache_manager.py       # High-level caching patterns
├── constants.py           # Centralized constants
├── entity/                # Data mappers
│   ├── loan.py
│   ├── wallet_transaction.py
│   ├── lender.py
│   └── ...
├── flow/                  # Business logic flows
│   ├── redemption_processing.py
│   ├── repayment_consumption.py
│   ├── cp_dashboard_summary.py
│   └── ...
├── helper/                # Utility helpers
│   ├── date_utils.py
│   ├── generic_utils.py
│   └── master_account_helper.py
├── ddl/                   # Database DDL scripts
├── job_mappers/           # Job-specific mappers
└── stored_procedures/     # PostgreSQL stored procedures
```

---

## Deploying to PyPI

### Build and Upload

```bash
# Install build tools
pip install build twine

# Clean and build
rm -rf build/ dist/ *.egg-info/
python -m build

# Upload to PyPI
twine upload dist/*
```

### Version Management

Update version in `setup.py`:

```python
version = "0.0.2"
```

---

## License

Proprietary - LenDenClub Internal Use Only

## Author

**Sonu Sharma** - sonu.sharma@lendenclub.com

## Support

