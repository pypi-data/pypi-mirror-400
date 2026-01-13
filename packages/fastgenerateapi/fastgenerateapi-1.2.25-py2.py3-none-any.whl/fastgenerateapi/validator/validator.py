import re
from datetime import datetime, date
from typing import Optional


def phone_validate(phone: Optional[str]) -> bool:
    """
    手机号码校验
    :param phone:
    :return:
    """
    if not phone:
        return False
    phone_pattern = re.compile(r'^(?:(?:\+|00)86)?1[3-9]\d{9}$')

    return phone_pattern.fullmatch(phone) is not None


def id_card_validate(id_card: Optional[str]) -> bool:
    """
    身份证号码校验
    :param id_card:
    :return:
    """
    if not id_card or len(id_card) != 18:
        return False
    id_card = id_card.upper()
    if not id_card[:17].isdigit() or id_card[-1] not in '0123456789X':
        return False
    date_of_birth = date(
        year=int(id_card[6:10]),
        month=int(id_card[10:12]),
        day=int(id_card[12:14])
    )
    current_date = date.today()
    if date_of_birth > current_date or date_of_birth.year < 1900:
        return False

    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_code_map = {0: '1', 1: '0', 2: 'X', 3: '9', 4: '8', 5: '7', 6: '6', 7: '5', 8: '4', 9: '3', 10: '2'}

    total = sum(int(id_card[i]) * weights[i] for i in range(17))

    remainder = total % 11
    expected_check_code = check_code_map[remainder]
    return id_card[-1] == expected_check_code


def email_validate(email: Optional[str]) -> bool:
    """
    验证邮箱格式合法性（符合RFC 5322简化标准，覆盖99%+日常/开发场景）
    :param email: 待校验的邮箱字符串
    :return: 合法返回True，否则False
    """
    if not email:
        return False

    email_pattern = r'^[a-zA-Z0-9_%+-]+(?:\.[a-zA-Z0-9_%+-]+)*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    return re.fullmatch(email_pattern, email) is not None

