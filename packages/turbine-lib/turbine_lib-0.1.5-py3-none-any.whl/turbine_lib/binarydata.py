class BinaryData:
    def __init__(self, data=None, size=None):
        if data is None and size is None:
            self.data_ = bytearray()
            self.size_ = 0
        elif isinstance(data, int):
            # Construct with size
            self.data_ = bytearray(data)
            self.size_ = data
        elif isinstance(data, bytes):
            # Construct with bytes data
            self.data_ = bytearray(data)
            self.size_ = len(data) if size is None else size
        elif isinstance(data, bytearray):
            self.data_ = data
            self.size_ = len(data) if size is None else size
        else:
            raise ValueError("Invalid arguments for BinaryData constructor")

    def __getitem__(self, pos):
        if pos >= self.size_:
            raise IndexError(f"Position {pos} is out of range in BinaryData with size {self.size_}")
        return self.data_[pos]

    def __setitem__(self, pos, value):
        if pos >= self.size_:
            raise IndexError(f"Position {pos} is out of range in BinaryData with size {self.size_}")
        self.data_[pos] = value

    def __add__(self, other):
        if not isinstance(other, BinaryData):
            raise TypeError("Can only add BinaryData to BinaryData")
        result_data = self.data_ + other.data_
        result = BinaryData(result_data)
        return result

    def __eq__(self, other):
        if not isinstance(other, BinaryData):
            return False
        return self.data_ == other.data_

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return self.size_

    def empty(self):
        return self.size_ == 0

    def append(self, other, offset=0):
        if offset + other.size_ > self.size_:
            raise ValueError("Data for appending has more bytes than BinaryData size!")
        self.data_[offset:offset + other.size_] = other.data_

    def to_number(self, t, pos):
        """Translates T bytes from data into number using UTF-16LE encoding"""
        if pos + t > self.size_:
            raise IndexError(
                f"Reading {t} bytes from {pos} offset with BinaryData size {self.size_} Reached end of BinaryData!")

        ans = 0
        for i in range(t - 1, -1, -1):
            ans = ((ans << 8) | self.data_[pos + i])
        return ans

    def to_number_raw(self, t, pos):
        """Translates T bytes from data into number in raw format"""
        if pos + t > self.size_:
            raise IndexError(
                f"Reading {t} bytes from {pos} offset with BinaryData size {self.size_} Reached end of BinaryData!")

        ans = 0
        for i in range(t):
            ans = ((ans << 8) | self.data_[pos + i])
        return ans

    @staticmethod
    def from_number(t, number):
        """Makes data from specified T bytes of number in Little Endian encoding"""
        if t <= 0:
            raise ValueError("Trying to make data from amount of bytes < 0")

        data = bytearray(t)
        for i in range(t):
            data[i] = (number >> (8 * i)) & 0xFF
        return BinaryData(data)

    @staticmethod
    def from_number_raw(t, number):
        """Makes data from specified T bytes of number in raw format"""
        if t <= 0:
            raise ValueError("Trying to make data from amount of bytes < 0")

        data = BinaryData.from_number(t, number)
        data.data_ = bytearray(reversed(data.data_))
        return data

    def size(self):
        return self.size_

    def data(self):
        return self.data_

    def write_to_file(self, filename):
        try:
            with open(filename, 'wb') as f:
                f.write(self.data_)
            return True
        except Exception as e:
            print(f"Error writing to file {filename}: {e}")
            return False

    def read_from_file(self, filename):
        try:
            with open(filename, 'rb') as f:
                file_data = f.read()
                self.data_ = bytearray(file_data)
                self.size_ = len(file_data)
        except Exception as e:
            print(f"Error reading from file {filename}: {e}")
            self.size_ = 0
            self.data_ = bytearray()

    def cut_data(self, first=0, last=None):
        if last is None:
            last = self.size()

        if last > self.size():
            raise IndexError("Unable to cut data - parameter last is out of range")

        new_data = self.data_[first:last]
        return BinaryData(new_data)
