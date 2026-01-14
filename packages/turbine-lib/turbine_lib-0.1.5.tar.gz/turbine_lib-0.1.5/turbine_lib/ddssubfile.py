from turbine_lib.subfile import Subfile, FILE_TYPE
from turbine_lib.binarydata import BinaryData
from turbine_lib.subfiledata import SubfileData


class DDSSubfile(Subfile):
    """Implementation of Subfile for DDS type files"""

    @staticmethod
    def build_for_export(file_data):
        if file_data.empty() or len(file_data) < 256:
            return SubfileData()

        dds_data = BinaryData(bytearray(len(file_data) - 24 + 128))
        for i in range(128):
            dds_data[i] = 0

        # Copy data from offset 24 in file_data to offset 128 in dds_data
        for i in range(len(file_data) - 24):
            dds_data[128 + i] = file_data[24 + i]

        if len(file_data) >= 20 and file_data[16] == 0x44 and file_data[17] == 0x58 and file_data[18] == 0x54:  # dxt

            if 0x31 == file_data[19]:  # dxt1
                dds_data[0] = 0x44  # D
                dds_data[1] = 0x44  # D
                dds_data[2] = 0x53  # S
                dds_data[3] = 0x20  # ''

                dds_data[4] = 0x7C

                dds_data[8] = 0x7
                dds_data[9] = 0x10

                # width, height
                dds_data[12] = file_data[12]
                dds_data[13] = file_data[13]
                dds_data[14] = file_data[14]
                dds_data[15] = file_data[15]

                dds_data[16] = file_data[8]
                dds_data[17] = file_data[9]
                dds_data[18] = file_data[10]
                dds_data[19] = file_data[11]

                dds_data[76] = 0x20
                dds_data[80] = 0x4

                dds_data[84] = 0x44  # 'D'
                dds_data[85] = 0x58  # 'X'
                dds_data[86] = 0x54  # 'T'
                dds_data[87] = 0x31  # '1'
            elif file_data[19] == 0x33:  ## dxt3
                dds_data[0] = 0x44  # D
                dds_data[1] = 0x44  # D
                dds_data[2] = 0x53  # S
                dds_data[3] = 0x20  # ''

                dds_data[4] = 0x7C

                dds_data[8] = 0x7
                dds_data[9] = 0x10

                # width, height
                dds_data[12] = file_data[12]
                dds_data[13] = file_data[13]
                dds_data[14] = file_data[14]
                dds_data[15] = file_data[15]

                dds_data[16] = file_data[8]
                dds_data[17] = file_data[9]
                dds_data[18] = file_data[10]
                dds_data[19] = file_data[11]

                dds_data[22] = 0x1

                dds_data[76] = 0x20
                dds_data[80] = 0x4

                dds_data[84] = 0x44  # 'D'
                dds_data[85] = 0x58  # 'X'
                dds_data[86] = 0x54  # 'T'
                dds_data[87] = 0x33  # '3'

                dds_data[108] = 0x8
                dds_data[109] = 0x10
                dds_data[110] = 0x40

            elif file_data[19] == 0x35:  # dxt5
                dds_data[0] = 0x44  # ‘D’
                dds_data[1] = 0x44  # ’D‘
                dds_data[2] = 0x53  # ‘S’
                dds_data[3] = 0x20  # ‘’

                dds_data[4] = 0x7C

                dds_data[8] = 0x7
                dds_data[9] = 0x10
                dds_data[10] = 0x8

                # width, height
                dds_data[12] = file_data[12]
                dds_data[13] = file_data[13]
                dds_data[14] = file_data[14]
                dds_data[15] = file_data[15]

                dds_data[16] = file_data[8]
                dds_data[17] = file_data[9]
                dds_data[18] = file_data[10]
                dds_data[19] = file_data[11]

                dds_data[22] = 0x1
                dds_data[28] = 0x1

                dds_data[76] = 0x20
                dds_data[80] = 0x4

                dds_data[84] = 0x44  # 'D'
                dds_data[85] = 0x58  # ‘X’
                dds_data[86] = 0x54  # ‘T’
                dds_data[87] = 0x35  # ‘5’

                # dds_data[88] = 0x20
                dds_data[88] = 0x20
                dds_data[94] = 0xFF
                dds_data[97] = 0xFF
                dds_data[100] = 0xFF
                dds_data[107] = 0xFF
                dds_data[113] = 0x10
        else:
            dds_data[0] = 0x44  # D
            dds_data[1] = 0x44  # D
            dds_data[2] = 0x53  # S
            dds_data[3] = 0x20  # ''

            dds_data[4] = 0x7C

            dds_data[8] = 0x7
            dds_data[9] = 0x10

            # width, height
            dds_data[12] = file_data[12]
            dds_data[13] = file_data[13]
            dds_data[14] = file_data[14]
            dds_data[15] = file_data[15]
            dds_data[16] = file_data[8]
            dds_data[17] = file_data[9]
            dds_data[18] = file_data[10]
            dds_data[19] = file_data[11]

            dds_data[76] = 0x20
            dds_data[80] = 0x40
            # dds_data[88] = 0x18
            dds_data[88] = 0x08
            dds_data[94] = 0xFF
            dds_data[97] = 0xFF
            dds_data[100] = 0xFF

        # compression = file_data.to_number(4, 0x10)
        #
        # if compression == 20:  # 14 00 00 00 - 888 (R8G8B8)
        #     dds_data[0x4C] = 0x20  # ?
        #     dds_data[0x50] = 0x40  # compressed or not
        #
        #     dds_data[0x58] = 0x18  # bytes per pixel
        #     dds_data[0x5E] = 0xFF
        #     dds_data[0x61] = 0xFF
        #     dds_data[0x64] = 0xFF
        # elif compression == 21:  # 15 00 00 00 - 8888 (R8G8B8A8)
        #     dds_data[0x4C] = 0x20  # ?
        #     dds_data[0x50] = 0x40  # compressed or not
        #
        #     dds_data[0x58] = 0x20  # bytes per pixel
        #     dds_data[0x5E] = 0xFF
        #     dds_data[0x61] = 0xFF
        #     dds_data[0x64] = 0xFF
        #     dds_data[0x6B] = 0xFF
        # elif compression == 28:  # 1C 00 00 00 - 332 (?)
        #     dds_data[0x4C] = 0x20  # ?
        #     dds_data[0x50] = 0x40  # compressed or not
        #
        #     dds_data[0x58] = 0x08  # bytes per pixel
        #     dds_data[0x5E] = 0xFF
        #     dds_data[0x61] = 0xFF
        #     dds_data[0x64] = 0xFF
        # elif compression == 827611204:  # 44 58 54 31 - DXT1
        #     dds_data[76] = 32
        #     dds_data[80] = 4
        #
        #     dds_data[84] = 68
        #     dds_data[85] = 88
        #     dds_data[86] = 84
        #     dds_data[87] = 49
        # elif compression == 861165636:  # 44 58 54 33 - DXT3
        #     dds_data[22] = 1
        #     dds_data[76] = 32
        #     dds_data[80] = 4
        #
        #     dds_data[84] = 68
        #     dds_data[85] = 88
        #     dds_data[86] = 84
        #     dds_data[87] = 51
        #
        #     dds_data[108] = 8
        #     dds_data[109] = 16
        #     dds_data[110] = 64
        # elif compression == 894720068:  # 44 58 54 35 - DXT5
        #     dds_data[10] = 8
        #     dds_data[22] = 1
        #     dds_data[28] = 1
        #     dds_data[76] = 32
        #     dds_data[80] = 4
        #
        #     dds_data[84] = 68
        #     dds_data[85] = 88
        #     dds_data[86] = 84
        #     dds_data[87] = 53
        #
        #     dds_data[88] = 32
        #     dds_data[94] = 255
        #     dds_data[97] = 255
        #     dds_data[100] = 255
        #     dds_data[107] = 255
        #     dds_data[109] = 16
        # else:
        #     print("Unknown header format.")
        #     return SubfileData()

        result = SubfileData()
        result.binary_data = dds_data
        result.options = {"ext": ".dds"}
        return result

    @staticmethod
    def build_for_import(old_data, data):
        file_size = BinaryData.from_number(4, len(data.binary_data) - 128)
        import_header = BinaryData(bytearray(20))
        for i in range(20):
            import_header[i] = 0
        #     file_id
        # import_header[0]= 0x0C
        # import_header[1]= 0x3B
        # import_header[2]= 0x00
        # import_header[3]= 0x41

        old_data_arr = old_data.data()
        import_header[0] = old_data_arr[0]
        import_header[1] = old_data_arr[1]
        import_header[2] = old_data_arr[2]
        import_header[3] = old_data_arr[3]

        # import_header[4]= 0x0F
        import_header[4] = old_data_arr[4]
        import_header[5] = old_data_arr[5]
        import_header[6] = old_data_arr[6]
        import_header[7] = old_data_arr[7]

        # width height
        # import_header[8]= 0x00
        # import_header[9]= 0x01
        # import_header[10]= 0x00
        # import_header[11]= 0x00
        # import_header[12]= 0x44
        # import_header[13]= 0x01
        # import_header[14]= 0x00
        # import_header[15]= 0x00

        import_header[8] = data.binary_data[16]
        import_header[9] = data.binary_data[17]
        import_header[10] = data.binary_data[18]
        import_header[11] = data.binary_data[19]
        import_header[12] = data.binary_data[12]
        import_header[13] = data.binary_data[13]
        import_header[14] = data.binary_data[14]
        import_header[15] = data.binary_data[15]

        # import_header[16]= 0x1C
        import_header[16] = old_data_arr[16]
        import_header[17] = old_data_arr[17]
        import_header[18] = old_data_arr[18]
        import_header[19] = old_data_arr[19]

        # print("new_header:")
        # DDSSubfile.print_hex_bytes(import_header.data())

        # print("old_header:")
        # DDSSubfile.print_hex_bytes(old_data.data())

        # return old_data.cut_data(0, 20) + file_size + data.binary_data.cut_data(128)
        return import_header.cut_data(0, 20) + file_size + data.binary_data.cut_data(128)

    @staticmethod
    def print_hex_bytes(data, count=20):
        """
        打印bytearray前count字节的十六进制表示

        Args:
            data: bytearray 或 bytes 对象
            count: 要打印的字节数，默认为20
        """
        # 获取前count个字节
        bytes_to_print = data[:count]

        # 方法3：使用f-string (Python 3.6+)
        print("十六进制(f-string):", ' '.join(f'{b:02X}' for b in bytes_to_print))
