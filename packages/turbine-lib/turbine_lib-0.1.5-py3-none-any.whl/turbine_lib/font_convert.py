import datetime
import os
import struct


# bmfont


class SourceCharInfo:
    def __init__(self, id, x, y, width, height, xoffset, yoffset, xadvance, page, channel):
        self.Id = id
        self.X = x
        self.Y = y
        self.Width = width
        self.Height = height
        self.XOffset = xoffset
        self.YOffset = yoffset
        self.XAdvance = xadvance
        self.Page = page
        self.Channel = channel
        # 计算rightBearingX = XAdvance - XOffset - Width
        self.RightBearingX = xadvance - xoffset - width


class Padding:
    def __init__(self, up, right, down, left):
        self.Left = left
        self.Right = right
        self.Up = up
        self.Down = down


class Spacing:
    def __init__(self, horizontal, vertical):
        self.Horizontal = horizontal
        self.Vertical = vertical


class SourceFontInfo:
    def __init__(self, filename):
        self.Filename = filename
        self.IsValid = False

        # 初始化所有属性
        self.FontName = ""
        self.FontSize = 0
        self.Bold = False
        self.Italic = False
        self.FixedHeight = False
        self.Charset = 0
        self.Unicode = False
        self.StretchH = 0
        self.Smooth = False
        self.Antialiasing = 0
        self.Padding = None
        self.Spacing = None
        self.Outline = 0
        self.LineHeight = 0
        self.Base = 0
        self.ScaleW = 0
        self.ScaleH = 0
        self.Pages = 0
        self.AlphaChannel = 0
        self.RedChannel = 0
        self.GreenChannel = 0
        self.BlueChannel = 0
        self.DdsFilename = ""
        self.CharsCount = 0
        self.Chars = []
        self.DdsWidth = 0
        self.DdsHeight = 0

        if filename:
            self.IsValid = self._read(filename)
            # pass

    @property
    def Filename(self):
        return self._filename

    @Filename.setter
    def Filename(self, value):
        self._filename = value
        # if value:
        #     self.IsValid = self._read(value)

    def _read(self, filename):
        try:
            with open(filename, 'rb') as f:
                data = f.read()

            # file identifier: BMF3
            if data[0] != 66 or data[1] != 77 or data[2] != 70 or data[3] != 3:
                return False

            # 使用内存视图来模拟BinaryReader
            offset = 0

            # file identifier
            offset += 4

            # block type 1: info
            # read type identifier and size
            offset += 1  # 跳过类型标识符
            block1_size = struct.unpack_from('<I', data, offset)[0]
            offset += 4

            # read content
            self.FontSize = struct.unpack_from('<h', data, offset)[0]
            offset += 2

            bit_field_byte = struct.unpack_from('B', data, offset)[0]
            offset += 1

            # 解析bit field
            self.Smooth = bool(bit_field_byte & 1)
            self.Unicode = bool(bit_field_byte & 2)
            self.Italic = bool(bit_field_byte & 4)
            self.Bold = bool(bit_field_byte & 8)
            self.FixedHeight = bool(bit_field_byte & 16)

            self.Charset = struct.unpack_from('B', data, offset)[0]
            offset += 1
            self.StretchH = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            self.Antialiasing = struct.unpack_from('B', data, offset)[0]
            offset += 1

            # Padding
            padding_up = struct.unpack_from('B', data, offset)[0]
            offset += 1
            padding_right = struct.unpack_from('B', data, offset)[0]
            offset += 1
            padding_down = struct.unpack_from('B', data, offset)[0]
            offset += 1
            padding_left = struct.unpack_from('B', data, offset)[0]
            offset += 1
            self.Padding = Padding(padding_up, padding_right, padding_down, padding_left)

            # Spacing
            spacing_horizontal = struct.unpack_from('B', data, offset)[0]
            offset += 1
            spacing_vertical = struct.unpack_from('B', data, offset)[0]
            offset += 1
            self.Spacing = Spacing(spacing_horizontal, spacing_vertical)

            self.Outline = struct.unpack_from('B', data, offset)[0]
            offset += 1

            # FontName
            font_name_bytes = data[offset:offset + (block1_size - 14)]
            # self.FontName = font_name_bytes.decode('utf-8').rstrip('\x00')  # 移除可能的空字符
            offset += (block1_size - 14)

            # block type 2: common
            # read type identifier and size
            offset += 1  # 跳过类型标识符
            block2_size = struct.unpack_from('<I', data, offset)[0]
            offset += 4

            # read content
            self.LineHeight = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            self.Base = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            self.ScaleW = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            self.ScaleH = struct.unpack_from('<H', data, offset)[0]
            offset += 2
            self.Pages = struct.unpack_from('<H', data, offset)[0]
            offset += 2

            # skip bit field
            offset += 1

            self.AlphaChannel = struct.unpack_from('B', data, offset)[0]
            offset += 1
            self.RedChannel = struct.unpack_from('B', data, offset)[0]
            offset += 1
            self.GreenChannel = struct.unpack_from('B', data, offset)[0]
            offset += 1
            self.BlueChannel = struct.unpack_from('B', data, offset)[0]
            offset += 1

            # block type 3: pages
            # read type identifier and size
            offset += 1  # 跳过类型标识符
            block3_size = struct.unpack_from('<I', data, offset)[0]
            offset += 4

            # read content
            # assume we have no more than 1 page here
            dds_filename_bytes = data[offset:offset + block3_size - 1]  # 去掉结尾的null字符
            self.DdsFilename = dds_filename_bytes.decode('utf-8')
            offset += block3_size

            # block type 4: chars
            # read type identifier and size
            offset += 1  # 跳过类型标识符
            block4_size = struct.unpack_from('<I', data, offset)[0]
            offset += 4

            # read content
            self.CharsCount = block4_size // 20
            self.Chars = []
            for i in range(self.CharsCount):
                id = struct.unpack_from('<I', data, offset)[0]
                offset += 4
                x = struct.unpack_from('<H', data, offset)[0]
                offset += 2
                y = struct.unpack_from('<H', data, offset)[0]
                offset += 2
                width = struct.unpack_from('<H', data, offset)[0]
                offset += 2
                height = struct.unpack_from('<H', data, offset)[0]
                offset += 2
                xoffset = struct.unpack_from('<h', data, offset)[0]
                offset += 2
                yoffset = struct.unpack_from('<h', data, offset)[0]
                offset += 2
                xadvance = struct.unpack_from('<h', data, offset)[0]
                offset += 2
                page = struct.unpack_from('B', data, offset)[0]
                offset += 1
                channel = struct.unpack_from('B', data, offset)[0]
                offset += 1

                char_info = SourceCharInfo(id, x, y, width, height, xoffset, yoffset, xadvance, page, channel)
                self.Chars.append(char_info)

            # skip block 5 (如果存在)

            return True
        except Exception as e:
            raise Exception(f"Error reading font file: {e}")


# 目标字体
class DestCharInfo:
    def __init__(self, info):
        self.Id = int(info.Id) & 0xFFFF  # unsigned word
        self.X = int(info.X) & 0xFFFF  # unsigned word
        self.Y = int(info.Y) & 0xFFFF  # unsigned word
        self.Width = int(info.Width) & 0xFF  # unsigned byte
        self.Height = int(info.Height) & 0xFF  # unsigned byte
        self.XOffset = int(info.XOffset)  # signed byte
        # 确保XOffset在有符号字节范围内 [-128, 127]
        if self.XOffset > 127:
            self.XOffset -= 256
        elif self.XOffset < -128:
            self.XOffset += 256

        self.YOffset = int(info.YOffset)  # signed byte处理，但存储为unsigned byte
        # 确保YOffset在有符号字节范围内 [-128, 127]，但转换为unsigned byte [0, 255]
        if self.YOffset > 127:
            self.YOffset -= 256
        elif self.YOffset < -128:
            self.YOffset += 256
        # 转换为unsigned byte范围
        self.YOffset = self.YOffset & 0xFF

        # 计算rightBearingX
        self.RightBearingX = int(info.XAdvance - info.XOffset - info.Width)  # signed byte
        if self.RightBearingX > 127:
            self.RightBearingX -= 256
        elif self.RightBearingX < -128:
            self.RightBearingX += 256

        self.XAdvance = int(info.XAdvance)  # signed byte
        if self.XAdvance > 127:
            self.XAdvance -= 256
        elif self.XAdvance < -128:
            self.XAdvance += 256


class DestFontInfo:
    def __init__(self, info):
        self.FontSize = abs(info.FontSize)
        self.Base = info.Base
        self.LineHeight = int(info.LineHeight) & 0xFFFF  # short
        # if self.LineHeight > 32767:
        #     self.LineHeight -= 65536
        self.Charset = int(info.Charset) & 0xFFFF  # short
        # if self.Charset > 32767:
        #     self.Charset -= 65536
        self.CharsCount = info.CharsCount
        self.Padding = int(info.Padding.Left) & 0xFF  # byte
        self.ScaleW = self.FontSize  # 新增：用于作为width
        self.ScaleH = self.FontSize  # 新增：用于作为height

        self.Chars = []
        for i in range(self.CharsCount):
            self.Chars.append(DestCharInfo(info.Chars[i]))

    def import_font(self, fontbin_filename):
        # 创建输出目录
        now = datetime.datetime.now()
        dir_name = f"output_{now.strftime('%Y-%m-%d')}"
        dir_path = os.path.join(os.getcwd(), dir_name)
        os.makedirs(dir_path, exist_ok=True)

        # 构建输出文件路径

        path = os.path.join(dir_path, fontbin_filename)
        # 写入处理后的数据
        with open(path, 'wb') as fs:
            # 写入头部数据 - 根据新格式调整
            fs.write(struct.pack('<I', 0))  # masterFileID
            fs.write(struct.pack('<I', self.FontSize))  # width
            fs.write(struct.pack('<I', self.FontSize))  # height
            fs.write(struct.pack('<I', self.CharsCount))  # CharsCount

            # 写入字符信息 - 根据新格式调整
            for i in range(self.CharsCount):
                char = self.Chars[i]
                fs.write(struct.pack('<B', char.Width))  # Chars[i].Width
                fs.write(struct.pack('<B', char.Height))  # Chars[i].Height
                fs.write(struct.pack('<b', char.XOffset))  # Chars[i].bearingX
                fs.write(struct.pack('<b', char.RightBearingX))  # Chars[i].rightBearingX
                fs.write(struct.pack('<B', char.YOffset))  # Chars[i].bearingY
                fs.write(struct.pack('<H', char.Id))  # Chars[i].id
                fs.write(struct.pack('<H', char.X))  # Chars[i].X
                fs.write(struct.pack('<H', char.Y))  # Chars[i].Y

            # 写入结尾数据
            fs.write(struct.pack('<I', 0))  # p
            fs.write(struct.pack('<I', 0))  # q
            fs.write(struct.pack('<I', 0))  # r
            fs.write(struct.pack('<I', 0))  # ddsId1
            fs.write(struct.pack('<I', 0))  # ddsId2
        return path


def fnt_to_fontbin(bmfont_file):
    """
    bmfont转换为fontbin
    """
    source_font = SourceFontInfo(bmfont_file)
    if not source_font.IsValid:
        print("Invalid source_font file!")
        raise ValueError("Invalid font file!")
    destFontInfo = DestFontInfo(source_font)
    output_fontbin = destFontInfo.import_font("template.fontbin")
    print(f'fontbin生成目录：{output_fontbin}')
    return output_fontbin


if __name__ == '__main__':
    font = SourceFontInfo(r'bmfont1.14a\output.fnt')
    destFontInfo = DestFontInfo(font)
    output_fontbin = destFontInfo.import_font('test.fontbin')
    print(f"生成字体成功：{output_fontbin}")
