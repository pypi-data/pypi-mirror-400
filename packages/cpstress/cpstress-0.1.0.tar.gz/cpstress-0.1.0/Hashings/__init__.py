"""
Hashings module - provides cryptographically secure random number generation.
"""

from .secure_random import SecureRandom, get_secure_random

__all__ = ['SecureRandom', 'get_secure_random']
