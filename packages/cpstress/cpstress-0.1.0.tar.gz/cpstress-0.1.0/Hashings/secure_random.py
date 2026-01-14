"""
Cryptographically secure random number generator.
Uses secrets.SystemRandom() instead of Python's pseudo-random Random class.
This ensures unpredictability and cannot be easily determined.
"""

import secrets

class SecureRandom:
    """
    Wrapper around secrets.SystemRandom() to provide cryptographically secure randomness.
    This replaces Python's standard Random class which uses MT19937 (predictable).
    """
    
    def __init__(self):
        self._rng=secrets.SystemRandom()
    
    def randint(self, a, b):
        """Return a random integer N such that a <= N <= b."""
        return self._rng.randint(a, b)
    
    def uniform(self, a, b):
        """Return a random floating point number N such that a <= N <= b."""
        return self._rng.uniform(a, b)
    
    def choice(self, seq):
        """Return a random element from the non-empty sequence."""
        return self._rng.choice(seq)
    
    def choices(self, population, weights=None, k=1):
        """Return a k sized list of elements chosen from the population with replacement."""
        return self._rng.choices(population, weights=weights, k=k)
    
    def shuffle(self, x):
        """Shuffle list x in place."""
        return self._rng.shuffle(x)
    
    def random(self):
        """Return random float in [0.0, 1.0)."""
        return self._rng.random()


def get_secure_random():
    """Factory function to get a secure random instance."""
    return SecureRandom()
