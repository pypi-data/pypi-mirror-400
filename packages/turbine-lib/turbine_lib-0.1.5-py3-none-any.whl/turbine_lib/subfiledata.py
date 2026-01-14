import yaml

from turbine_lib.binarydata import BinaryData


class SubfileData:

    def __init__(self, binary_data=None, text_data="", options=None):
        if binary_data is None:
            # Default constructor
            self.binary_data = BinaryData()
            self.text_data = ""
            self.options = yaml.safe_load("{}") if options is None else options
        else:
            # Constructor with parameters
            self.binary_data = binary_data
            self.text_data = text_data
            self.options = options if options is not None else yaml.safe_load("{}")

    def empty(self):
        return (len(self.binary_data) == 0 and 
                len(self.text_data) == 0 and 
                (self.options is None or self.options == yaml.safe_load("{}")))

    def __eq__(self, other):
        if not isinstance(other, SubfileData):
            return False
        return (self.binary_data == other.binary_data and 
                self.text_data == other.text_data)

    def __ne__(self, other):
        return not self.__eq__(other)