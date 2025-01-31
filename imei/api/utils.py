def imei_valid(imei):
    if not imei.isdigit() or len(imei) != 15:
        return False
    imei = imei[::-1]
    checksum = 0

    for i in range(15):
        digit = ord(imei[i]) - ord("0")
        if i % 2 == 1:
            digit += digit
        if digit >= 10:
            digit = digit % 10 + 1
        checksum += digit

    return checksum % 10 == 0
