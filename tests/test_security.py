from app.security import hash_password, verify_password


def test_hash_password_returns_argon2id_hash():
    password = "correct horse battery staple"

    password_hash = hash_password(password)

    assert isinstance(password_hash, str)
    assert password_hash != password
    assert password_hash.startswith("$argon2id$")


def test_hash_password_uses_random_salt():
    password = "same password"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash


def test_verify_password_accepts_correct_password():
    password = "valid password"
    password_hash = hash_password(password)

    assert verify_password(password, password_hash) is True


def test_verify_password_rejects_incorrect_password():
    password_hash = hash_password("valid password")

    assert verify_password("incorrect password", password_hash) is False


def test_verify_password_rejects_invalid_hash():
    assert verify_password("password", "not-an-argon2-hash") is False
