from turbine_lib.subfile import Subfile
from turbine_lib.subfiledata import SubfileData


class FONT:
    """Marker class for FONT file type"""
    pass


class SubfileFONT(Subfile):

    @staticmethod
    def build_for_export(file_data):
        """
        Build data for export from FONT file
        :param file_data: BinaryData with file data
        :return: SubfileData with processed data
        """
        result = SubfileData()
        result.binary_data = file_data
        result.options["ext"] = ".fontbin"
        return result

    @staticmethod
    def build_for_import(old_data, data):
        """
        Build data for import to FONT file
        :param old_data: BinaryData with old data
        :param data: SubfileData with new data
        :return: BinaryData with processed data
        """
        # return old_data.cut_data(0, 4) + data.binary_data.cut_data(4)
        return data.binary_data