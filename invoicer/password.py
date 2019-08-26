from argon2 import PasswordHasher


class Hasher(object):
    '''
    This object is used to create and verify password hashes.
    '''
    def __init__(self):
        self._hasher = PasswordHasher()

    def reset(self, *args, **kwargs):
        '''
        Reset the hasher arguments.
        '''
        self._hasher = PasswordHasher(*args, **kwargs)

    def hash(self, password):
        return self._hasher.hash(password)

    def verify(self, hashed_password, password):
        return self._hasher.verify(hashed_password, password)


password_hasher = Hasher()


def hash_password(password=''):
    return password_hasher.hash(password)


def verify_password(hashed_password, password):
    '''
    :raises: argon2.exceptions.VerifyMismatchError
    '''
    return password_hasher.verify(hashed_password, password)
