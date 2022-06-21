class FloatBinHandler:

    def __init__(self, precision: int, max_value):
        """
        Handler functions to quickly and easily convert floats to bins with padding, useful when encoding genotypes
        since all the binary representation must be of the same length
        :param precision: number of decimals to be considered
        :param max_value: maximum value of the float numbers to be converted, needed for padding
        """
        self.precision = precision
        self.const = int("1" + "0" * precision)
        self.length = len(bin(int(max_value * self.const))) - 2

    def float2bin(self, f: float):
        """
        Coverts float to binary sting
        :param f: float to be converted
        :return: binary sting with buffer
        """
        b = bin(int(f * self.const))

        pb = "0b" + b[2:].zfill(self.length)
        return pb

    def bin2float(self, b: str):
        """
        Converts binary string to float
        :param b: Binary string
        :return: float conversion
        """
        return int(b, 2) / self.const
