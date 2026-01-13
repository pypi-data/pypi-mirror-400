"""
Generic Utilities

Utility functions for generic operations.
Copied from vortex/common/utils/generic_utils.py to make repository self-contained.
"""

import random


def generate_transaction_id():
    transaction_id = "" + "".join(
        [random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVXYZ') for i in range(16)])
    return transaction_id

