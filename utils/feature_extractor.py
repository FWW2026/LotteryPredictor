from collections import Counter

ZODIACS = [
    "鼠","牛","虎","兔",
    "龙","蛇","马","羊",
    "猴","鸡","狗","猪"
]


def extract_last_numbers(records):

    result = []

    for item in records:

        try:

            nums = item["num"].split(",")

            result.append(
                int(nums[-1])
            )

        except:
            pass

    return result


def extract_last_zodiac(records):

    result = []

    for item in records:

        try:

            zodiacs = item["shengxiao"].split(",")

            result.append(
                zodiacs[-1]
            )

        except:
            pass

    return result