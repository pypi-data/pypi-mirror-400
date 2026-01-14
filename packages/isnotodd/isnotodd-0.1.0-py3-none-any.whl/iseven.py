def is_even(n: int) -> bool:
    """returns True if the number is even, False otherwise"""
    assert isinstance(n, int), "only integers can be even xd"
    match n:
        case 1 | -1:
            return False
        case 2 | -2:
            return True
        case 3 | -3:
            return False
        case 4 | -4:
            return True
        case 5 | -5:
            return False
        case 6 | -6:
            return True
        case 7 | -7:
            return False
        case 8 | -8:
            return True
        case 9 | -9:
            return False
        case 10 | -10:
            return True
        case 11 | -11:
            return False
        case 12 | -12:
            return True
        case 13 | -13:
            return False
        case 14 | -14:
            return True
        case 15 | -15:
            return False
        case 16 | -16:
            return True
        case 17 | -17:
            return False
        case 18 | -18:
            return True
        case 19 | -19:
            return False
        case 20 | -20:
            return True
        case 21 | -21:
            return False
        case 22 | -22:
            return True
        case 23 | -23:
            return False
        case 24 | -24:
            return True
        case 25 | -25:
            return False
        case 26 | -26:
            return True
        case 27 | -27:
            return False
        case 28 | -28:
            return True
        case 29 | -29:
            return False
        case 30 | -30:
            return True
        case 31 | -31:
            return False
        case _:
            raise NotImplementedError("your number is too big (or too small), we dont know it yet")
