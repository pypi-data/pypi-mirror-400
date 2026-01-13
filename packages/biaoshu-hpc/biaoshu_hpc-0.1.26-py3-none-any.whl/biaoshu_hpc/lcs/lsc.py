from . import telehpc

class LCS:
    __calculator = telehpc.LCSCalculator()

    @classmethod
    def calculate_general(cls, str1: str, str2: str):
        return cls.__calculator.calculate_general(str1, str2)

    @classmethod
    def calculate_dp(cls, str1: str, str2: str):
        return cls.__calculator.calculate_dp(str1, str2)