from turbine_lib import textutils

from turbine_lib.binarydata import BinaryData
from turbine_lib.subfile import Subfile
from turbine_lib.subfiledata import SubfileData


class TextFragment:
    """Represents a text fragment in a text subfile"""

    def __init__(self):
        self.fragment_id = 0
        self.text = ""
        self.args = ""

    def __lt__(self, other):
        return self.fragment_id < other.fragment_id


class TextSubfile(Subfile):
    """Implementation of Subfile for TEXT type files"""

    @staticmethod
    def build_for_export(file_data):
        result = SubfileData()
        offset = 9  # first 4 bytes - file_id, then 4 bytes - unknown, then 1 byte - unknown

        text_fragment_num = file_data.to_number(1, offset)
        if (text_fragment_num & 0x80) != 0:
            text_fragment_num = (((text_fragment_num ^ 0x80) << 8) | file_data[offset + 1])
            offset += 1
        offset += 1

        for i in range(text_fragment_num):
            fragment_id = file_data.to_number(8, offset)
            offset += 8

            # Making pieces
            pieces, offset = TextSubfile.make_pieces(file_data, offset)
            text = "["
            for j in range(len(pieces) - 1):
                text += pieces[j] + "<--DO_NOT_TOUCH!-->"
            if pieces:
                text += pieces[-1]
            text += "]"

            # Making argument references
            arg_refs, offset = TextSubfile.make_argument_references(file_data, offset)
            arguments = ""
            for j in range(len(arg_refs) - 1):
                arguments += textutils.to_utf16(arg_refs[j]) + "-"
            if arg_refs:
                arguments += textutils.to_utf16(arg_refs[-1])

            # Through argument strings are not used, we need to call this function to correctly move offset
            _result, offset = TextSubfile.make_argument_strings(file_data, offset)

            if len(result.text_data) > 0:
                result.text_data += "|||"

            result.text_data += textutils.to_utf16(fragment_id) + ":::"
            result.text_data += arguments + ":::"
            result.text_data += text

        result.options = {"ext": ".txt"}
        return result

    @staticmethod
    def build_for_import(old_data, data):
        new_file_data = BinaryData()
        offset = 9  # first 8 bytes - file_info. After them:
        # first 4 bytes - file_id, then 4 bytes - unknown, then 1 byte - unknown

        text_fragment_num = old_data.to_number(1, offset)
        if (text_fragment_num & 0x80) != 0:
            text_fragment_num = (((text_fragment_num ^ 0x80) << 8) | old_data[offset + 1])
            offset += 1
        offset += 1

        # Adding file info
        new_file_data = new_file_data + old_data.cut_data(0, offset)

        patch_fragments = TextSubfile.parse_patch_fragments(data)

        for i in range(text_fragment_num):
            fragment_id = old_data.to_number(8, offset)
            offset += 8

            new_file_data = new_file_data + BinaryData.from_number(8, fragment_id)

            id_comp = TextFragment()
            id_comp.fragment_id = fragment_id

            # Find matching fragment
            fragment_iterator = None
            for frag in patch_fragments:
                if frag.fragment_id == id_comp.fragment_id:
                    fragment_iterator = frag
                    break

            if fragment_iterator is None:
                # Retrieving old pieces
                result_data, offset = TextSubfile.get_piece_data(old_data, offset)
                new_file_data = new_file_data + result_data
                # Retrieving old references
                result_data, offset = TextSubfile.get_argument_reference_data(old_data, offset)
                new_file_data = new_file_data + result_data
                # Retrieving old ref_strings
                result_data, offset = TextSubfile.get_argument_strings_data(old_data, offset)
                new_file_data = new_file_data + result_data
            else:
                # Making and adding new pieces
                result_data, offset = TextSubfile.build_pieces(old_data, fragment_iterator, offset)
                new_file_data = new_file_data + result_data
                # Making and adding new references
                result_data, offset = TextSubfile.build_argument_references(old_data, fragment_iterator, offset)
                new_file_data = new_file_data + result_data
                # Making and adding new strings
                result_data, offset = TextSubfile.build_argument_strings(old_data, fragment_iterator, offset)
                new_file_data = new_file_data + result_data

        # Adding elapsed file data
        new_file_data = new_file_data + old_data.cut_data(offset)

        return new_file_data

    @staticmethod
    def parse_patch_fragments(data):
        result = []
        pointer = 0

        text_data = data.text_data
        while pointer < len(text_data):
            # Parsing fragment_id
            pointer1 = text_data.find(":::", pointer)
            if pointer1 == -1:
                break

            fragment_id = textutils.from_utf16(text_data[pointer:pointer1])
            pointer = pointer1 + 3

            fragment = TextFragment()
            fragment.fragment_id = fragment_id

            # Parsing arguments
            pointer1 = text_data.find(":::", pointer)
            if pointer1 == -1:
                break

            arguments = text_data[pointer:pointer1]
            pointer = pointer1 + 3

            if len(arguments) > 0:
                fragment.args = textutils.arguments_from_utf16(arguments)

            # Parsing text
            pointer1 = text_data.find("|||", pointer)
            if pointer1 == -1:
                pointer1 = len(text_data)

            fragment.text = text_data[pointer:pointer1]
            pointer = pointer1 + 3

            result.append(fragment)

        result.sort(key=lambda x: x.fragment_id)
        return result

    @staticmethod
    def make_pieces(data, offset):
        # This is a simplified implementation - would need to be expanded based on actual C++ code
        result = []

        num_pieces = data.to_number(4, offset)
        offset += 4

        for j in range(num_pieces):
            piece_size = data.to_number(1, offset)
            if (piece_size & 128) != 0:
                piece_size = (((piece_size ^ 128) << 8) | data[offset + 1])
                offset += 1
            offset += 1

            piece_data = data.cut_data(offset, offset + piece_size * 2)
            piece = ""

            for k in range(piece_size):
                c = (piece_data[2 * k + 1] << 8)  # First byte
                c |= piece_data[2 * k]  # Second byte
                piece += chr(c)

            result.append(piece)
            offset += piece_size * 2

        return result, offset

    @staticmethod
    def make_argument_references(data, offset):
        result = []

        num_references = data.to_number(4, offset)
        offset += 4

        for j in range(num_references):
            result.append(data.to_number(4, offset))
            offset += 4

        return result, offset

    @staticmethod
    def make_argument_strings(data, offset):
        result = []

        num_arg_strings = data.to_number(1, offset)
        offset += 1

        for j in range(num_arg_strings):
            num_args = data.to_number(4, offset)
            offset += 4

            result.append([])
            for k in range(num_args):
                string_size = data.to_number(1, offset)
                if (string_size & 0x80) != 0:
                    string_size = (((string_size ^ 0x80) << 8) | data[offset + 1])
                    offset += 1
                offset += 1

                result[j].append(data.cut_data(offset, offset + string_size * 2))
                offset += string_size * 2

        return result, offset

    @staticmethod
    def build_pieces(data, new_data, offset):
        # Moving offset pointer in data
        old_offset = offset
        num_pieces = data.to_number(4, offset)
        offset += 4

        for j in range(num_pieces):
            piece_size = data.to_number(1, offset)
            if (piece_size & 128) != 0:
                piece_size = (((piece_size ^ 128) << 8) | data[offset + 1])
                offset += 1
            offset += 1
            offset += piece_size * 2

        # Deleting '[' and ']' brackets
        text_data = new_data.text[1:-1] if len(new_data.text) > 2 else ""

        text_pieces = []

        DNT = "<--DO_NOT_TOUCH!-->"
        prev = 0
        next_pos = text_data.find(DNT, prev)

        while next_pos != -1:
            piece = " " if next_pos - prev == 0 else text_data[prev:next_pos]
            text_pieces.append(piece)
            prev = next_pos + len(DNT)
            next_pos = text_data.find(DNT, prev)

        text_pieces.append(text_data[prev:])

        # Building BinaryData from pieces
        result_data = BinaryData()
        result_data = result_data + BinaryData.from_number(4, len(text_pieces))

        for piece in text_pieces:
            piece_size = len(piece)
            if piece_size < 128:
                result_data = result_data + BinaryData.from_number(1, piece_size)
            else:
                result_data = result_data + BinaryData.from_number_raw(2, (piece_size | 32768))

            for j in range(piece_size):
                result_data = result_data + BinaryData.from_number(2, ord(piece[j]))

        return result_data, offset

    @staticmethod
    def build_argument_references(data, new_data, offset):
        # Moving offset pointer in data
        old_offset = offset
        num_references = data.to_number(4, offset)
        offset += 4
        offset += 4 * num_references

        # If there are no args - making 4 null-bytes and return;
        if not new_data.args:
            result = BinaryData.from_number(4, 0)
            return result, offset

        # Parsing arguments from list in options["args"]
        args_list = new_data.args
        argument_references = []

        prev = 0
        next_pos = args_list.find('-', prev)
        while next_pos != -1:
            argument = args_list[prev:next_pos]
            argument_references.append(int(argument))
            prev = next_pos + 1
            next_pos = args_list.find('-', prev)

        argument = args_list[prev:]
        argument_references.append(int(argument))

        result = BinaryData()
        result = result + BinaryData.from_number(4, len(argument_references))
        for arg_reference in argument_references:
            result = result + BinaryData.from_number(4, arg_reference)

        return result, offset

    @staticmethod
    def build_argument_strings(data, new_data, offset):
        # TODO: IMPLEMENT (never user)
        # Moving offset pointer in data
        old_offset = offset
        num_arg_strings = data.to_number(1, offset)
        offset += 1

        for j in range(num_arg_strings):
            num_args = data.to_number(4, offset)
            offset += 4

            for k in range(num_args):
                string_size = data.to_number(1, offset)
                if (string_size & 0x80) != 0:
                    string_size = (((string_size ^ 0x80) << 8) | data[offset + 1])
                    offset += 1
                offset += 1
                offset += string_size * 2

        return BinaryData.from_number(1, 0), offset

    @staticmethod
    def get_piece_data(data, offset):
        old_offset = offset

        num_pieces = data.to_number(4, offset)
        offset += 4

        for j in range(num_pieces):
            piece_size = data.to_number(1, offset)
            if (piece_size & 128) != 0:
                piece_size = (((piece_size ^ 128) << 8) | data[offset + 1])
                offset += 1
            offset += 1
            offset += piece_size * 2

        return data.cut_data(old_offset, offset), offset

    @staticmethod
    def get_argument_reference_data(data, offset):
        old_offset = offset
        num_references = data.to_number(4, offset)
        offset += 4
        offset += 4 * num_references
        return data.cut_data(old_offset, offset), offset

    @staticmethod
    def get_argument_strings_data(data, offset):
        old_offset = offset

        num_arg_strings = data.to_number(1, offset)
        offset += 1

        for j in range(num_arg_strings):
            num_args = data.to_number(4, offset)
            offset += 4

            for k in range(num_args):
                string_size = data.to_number(1, offset)
                if (string_size & 0x80) != 0:
                    string_size = (((string_size ^ 0x80) << 8) | data[offset + 1])
                    offset += 1
                offset += 1
                offset += string_size * 2

        return data.cut_data(old_offset, offset), offset
