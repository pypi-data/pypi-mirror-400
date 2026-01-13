from typing import Optional

import bcrypt

EXPECTED_SALT_LENGTH = 29
ENCODING = "utf-8"


def bcrypt_hash(plaintext: str, salt: Optional[bytes] = None) -> tuple[str, str]:
    if not salt:
        salt = bcrypt.gensalt()

    return (
        bcrypt.hashpw(plaintext.encode(ENCODING), salt).decode(ENCODING),
        salt.decode(ENCODING),
    )


def bcrypt_check_plaintext_equals_hash(
    plaintext: str, hashed_plaintext: str, salt: Optional[str] = None
) -> bool:
    if not salt:
        salt = hashed_plaintext[:EXPECTED_SALT_LENGTH]

    new_hashed_plaintext = bcrypt.hashpw(
        plaintext.encode(ENCODING), salt.encode(ENCODING)
    )
    return new_hashed_plaintext == hashed_plaintext.encode(ENCODING)
