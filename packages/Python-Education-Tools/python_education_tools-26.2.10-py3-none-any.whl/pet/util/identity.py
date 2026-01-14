from __future__ import annotations

from datetime import datetime


def id_card_to_age(id_card: str) -> int:
    """
    Convert PRC 18-digit ID card number to age.
    """
    if not isinstance(id_card, str):
        raise TypeError("id_card must be a string")
    if len(id_card) != 18:
        raise ValueError("身份证号码长度错误")

    birth_year = int(id_card[6:10])
    birth_month = int(id_card[10:12])
    birth_day = int(id_card[12:14])

    now = datetime.now()
    age = now.year - birth_year - ((now.month, now.day) < (birth_month, birth_day))
    return age
