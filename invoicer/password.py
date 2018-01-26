from argon2 import PasswordHasher


password_hasher = PasswordHasher(time_cost=100)


def hash_password(password=''):
    return password_hasher.hash(password)


def verify_password(hashed_password, password):
    return password_hasher.verify(hashed_password, password)
