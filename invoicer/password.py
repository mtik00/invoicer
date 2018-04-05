from argon2 import (
    PasswordHasher, DEFAULT_HASH_LENGTH, DEFAULT_MEMORY_COST,
    DEFAULT_PARALLELISM, DEFAULT_RANDOM_SALT_LENGTH, DEFAULT_TIME_COST
)


class Hasher(object):
    def __init__(self):
        self._hasher = PasswordHasher()

    def set(
        self, time_cost=DEFAULT_TIME_COST, memory_cost=DEFAULT_MEMORY_COST,
        parallelism=DEFAULT_PARALLELISM, hash_len=DEFAULT_HASH_LENGTH,
        salt_len=DEFAULT_RANDOM_SALT_LENGTH
    ):
        self._hasher = PasswordHasher(
            time_cost=time_cost, memory_cost=memory_cost, parallelism=parallelism,
            hash_len=hash_len, salt_len=salt_len)

    def hash(self, password):
        return self._hasher.hash(password)

    def verify(self, hashed_password, password):
        return self._hasher.verify(hashed_password, password)


password_hasher = Hasher()


def hash_password(password=''):
    return password_hasher.hash(password)


def verify_password(hashed_password, password):
    return password_hasher.verify(hashed_password, password)
