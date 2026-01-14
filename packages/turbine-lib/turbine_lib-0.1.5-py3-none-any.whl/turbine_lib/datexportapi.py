import ctypes
import ctypes.util
import os
import platform
from ctypes import wintypes
from pathlib import Path


class DatExportApi:
    def __init__(self):
        # Load the datexport DLL

        # 校验系统和Python位数
        if os.name != "nt":
            raise RuntimeError("仅支持Windows系统")
        if platform.architecture()[0] != "32bit":
            raise RuntimeError("仅支持32位Python")

        # 加载32位DLL
        dll_path = Path(__file__).parent / "libs" / "datexport.dll"
        zlib_dll_path = Path(__file__).parent / "libs" / "zlib1T.dll"
        if not dll_path.exists():
            raise FileNotFoundError("缺失32位DLL文件")
        if not zlib_dll_path.exists():
            raise FileNotFoundError("缺失32位DLL文件")
        self.datexport_dll = ctypes.WinDLL(str(dll_path))
        self.zlib_dll = ctypes.WinDLL(str(zlib_dll_path))

        # Define function prototypes
        try:
            # OpenDatFileEx2
            self.open_dat_file_func = self.datexport_dll.OpenDatFileEx2
            self.open_dat_file_func.argtypes = [
                wintypes.INT,  # handle
                ctypes.c_char_p,  # filename
                wintypes.UINT,  # flags
                ctypes.POINTER(wintypes.INT),  # did_master_map
                ctypes.POINTER(wintypes.INT),  # block_size
                ctypes.POINTER(wintypes.INT),  # vnum_dat_file
                ctypes.POINTER(wintypes.INT),  # vnum_game_data
                ctypes.POINTER(wintypes.ULONG),  # dat_file_id
                ctypes.c_void_p,  # dat_id_stamp
                ctypes.c_void_p  # first_iter_guid
            ]
            self.open_dat_file_func.restype = wintypes.INT

            # GetNumSubfiles
            self.get_num_subfiles_func = self.datexport_dll.GetNumSubfiles
            self.get_num_subfiles_func.argtypes = [wintypes.INT]  # handle
            self.get_num_subfiles_func.restype = wintypes.INT

            # GetSubfileSizes
            self.get_subfile_sizes_func = self.datexport_dll.GetSubfileSizes
            self.get_subfile_sizes_func.argtypes = [
                wintypes.INT,  # handle
                ctypes.POINTER(wintypes.UINT),  # file_id list pointer
                ctypes.POINTER(wintypes.INT),  # size list pointer
                ctypes.POINTER(wintypes.INT),  # iteration list pointer
                wintypes.INT,  # offset
                wintypes.INT  # count
            ]
            self.get_subfile_sizes_func.restype = wintypes.INT

            # GetSubfileVersion
            self.get_subfile_version_func = self.datexport_dll.GetSubfileVersion
            self.get_subfile_version_func.argtypes = [
                wintypes.INT,  # handle
                wintypes.INT  # file_id
            ]
            self.get_subfile_version_func.restype = wintypes.INT

            # GetSubfileData
            self.get_subfile_data_func = self.datexport_dll.GetSubfileData
            self.get_subfile_data_func.argtypes = [
                wintypes.INT,  # handle
                wintypes.INT,  # file_id
                ctypes.c_void_p,  # buffer for storing data
                wintypes.INT,  # 0
                ctypes.POINTER(wintypes.INT)  # version
            ]
            self.get_subfile_data_func.restype = wintypes.INT

            # CloseDatFile
            self.close_dat_file_func = self.datexport_dll.CloseDatFile
            self.close_dat_file_func.argtypes = [wintypes.INT]  # handle
            self.close_dat_file_func.restype = wintypes.INT

            # PurgeSubfileData
            self.purge_subfile_data_func = self.datexport_dll.PurgeSubfileData
            self.purge_subfile_data_func.argtypes = [
                wintypes.INT,  # handle
                wintypes.INT  # file_id
            ]
            self.purge_subfile_data_func.restype = wintypes.INT

            # PutSubfileData
            self.put_subfile_data_func = self.datexport_dll.PutSubfileData
            self.put_subfile_data_func.argtypes = [
                wintypes.INT,  # handle
                wintypes.INT,  # file_id
                ctypes.c_void_p,  # buffer with subfile data
                wintypes.INT,  # offset
                wintypes.INT,  # size of data in bytes
                wintypes.INT,  # version
                wintypes.INT,  # iteration
                wintypes.BOOL  # compress
            ]
            self.put_subfile_data_func.restype = wintypes.INT

            # Flush
            self.flush_func = self.datexport_dll.Flush
            self.flush_func.argtypes = [wintypes.INT]  # handle
            self.flush_func.restype = wintypes.INT

            # GetSubfileCompressionFlag
            self.get_subfile_compression_flag_func = self.datexport_dll.GetSubfileCompressionFlag
            self.get_subfile_compression_flag_func.argtypes = [
                wintypes.INT,  # handle
                wintypes.INT  # file_id
            ]
            self.get_subfile_compression_flag_func.restype = wintypes.BYTE

            # uncompress
            self.uncompress_func = self.zlib_dll.uncompress
            self.uncompress_func.argtypes = [
                ctypes.POINTER(ctypes.c_ubyte),  # dest
                ctypes.POINTER(wintypes.INT),  # destLen
                ctypes.POINTER(ctypes.c_ubyte),  # source
                wintypes.INT  # sourceLen
            ]
            self.uncompress_func.restype = wintypes.INT

            # compress
            self.compress_func = self.zlib_dll.compress
            self.compress_func.argtypes = [
                ctypes.POINTER(ctypes.c_ubyte),  # dest：输出缓冲区指针
                ctypes.POINTER(wintypes.INT),  # destLen：输出缓冲区长度（指针，传入变量地址）
                ctypes.POINTER(ctypes.c_ubyte),  # source：输入缓冲区指针
                wintypes.INT  # sourceLen：输入数据长度
            ]
            self.compress_func.restype = wintypes.INT  # 返回值：错误码（int）

            # compress2
            self.compress2_func = self.zlib_dll.compress2
            self.compress2_func.argtypes = [
                ctypes.POINTER(ctypes.c_ubyte),  # dest：输出缓冲区指针
                ctypes.POINTER(wintypes.INT),  # destLen：输出缓冲区长度（指针，传入变量地址）
                ctypes.POINTER(ctypes.c_ubyte),  # source：输入缓冲区指针
                wintypes.INT,  # sourceLen：输入数据长度
                wintypes.INT  # level：压缩级别（0~9）
            ]
            self.compress_func.restype = wintypes.INT  # 返回值：错误码（int）

        except Exception as e:
            raise RuntimeError(f"Error while parsing runtime library function: {e}")

    def open_dat_file(self, handle, filename, flags):
        did_master_map = wintypes.INT()
        block_size = wintypes.INT()
        vnum_dat_file = wintypes.INT()
        vnum_game_data = wintypes.INT()
        dat_file_id = wintypes.ULONG()
        dat_id_stamp = ctypes.create_string_buffer(64)
        first_iter_guid = ctypes.create_string_buffer(64)

        result = self.open_dat_file_func(
            handle,
            filename.encode('utf-8'),
            flags,
            ctypes.byref(did_master_map),
            ctypes.byref(block_size),
            ctypes.byref(vnum_dat_file),
            ctypes.byref(vnum_game_data),
            ctypes.byref(dat_file_id),
            dat_id_stamp,
            first_iter_guid
        )

        return result

    def get_num_subfiles(self, handle):
        return self.get_num_subfiles_func(handle)

    def get_subfile_sizes(self, handle, file_ids, sizes, iterations, offset, count):
        # Convert Python lists to C arrays
        file_ids_array = (wintypes.UINT * len(file_ids))(*file_ids)
        sizes_array = (wintypes.INT * len(sizes))(*sizes)
        iterations_array = (wintypes.INT * len(iterations))(*iterations)

        self.get_subfile_sizes_func(
            handle,
            file_ids_array,
            sizes_array,
            iterations_array,
            offset,
            count
        )

        # Copy back the results
        for i in range(len(file_ids)):
            file_ids[i] = file_ids_array[i]
            sizes[i] = sizes_array[i]
            iterations[i] = iterations_array[i]

    def get_subfile_version(self, handle, file_id):
        return self.get_subfile_version_func(handle, file_id)

    def get_subfile_data(self, handle, file_id, target_buf, version):
        version_ref = wintypes.INT(version)
        buf_ptr = (ctypes.c_ubyte * len(target_buf)).from_buffer(target_buf)
        size = self.get_subfile_data_func(
            handle,
            file_id,
            buf_ptr,
            0,
            ctypes.byref(version_ref)
        )

        # 如果文件被压缩，则解压
        compression_flag = self.get_subfile_compression_flag(handle, file_id)
        if compression_flag:
            # Handle compressed data
            buffer = target_buf
            decompressed_length = (buffer[3] << 24) | (buffer[2] << 16) | (buffer[1] << 8) | buffer[0]
            compressed_length = size - 4

            dst = bytearray(decompressed_length)
            src = bytearray(compressed_length)

            for i in range(4, size):
                src[i - 4] = buffer[i]

            result = self.uncompress(dst, decompressed_length, src, compressed_length)
            if result != 0:
                raise RuntimeError(f"Decompression failed with error code: {result}")

            # 将解压后的数据复制回target_buf
            for i in range(decompressed_length):
                target_buf[i] = dst[i]
            size = decompressed_length

        return size, version_ref.value

    def close_dat_file(self, handle):
        return self.close_dat_file_func(handle)

    def purge_subfile_data(self, handle, file_id):
        return self.purge_subfile_data_func(handle, file_id)

    def put_subfile_data(self, handle, file_id, data, offset, size, version, iteration, compress=False):
        data_ptr = (ctypes.c_ubyte * len(data)).from_buffer(data)
        return self.put_subfile_data_func(
            handle,
            file_id,
            data_ptr,
            offset,
            size,
            version,
            iteration,
            compress
        )

    def flush(self, handle):
        return self.flush_func(handle)

    def get_subfile_compression_flag(self, handle, file_id):
        return self.get_subfile_compression_flag_func(handle, file_id)

    def uncompress(self, dest, dest_len, source, source_len):
        # Convert bytearray to proper ctypes arrays
        dest_array = (ctypes.c_ubyte * len(dest)).from_buffer(dest)
        source_array = (ctypes.c_ubyte * len(source)).from_buffer(source)

        # Create pointers for length parameters
        dest_len_ref = ctypes.byref(ctypes.c_int(dest_len))
        return self.uncompress_func(dest_array, dest_len_ref, source_array, source_len)

    def compress(self, dest, dest_len, source, source_len):
        # Convert bytearray to proper ctypes arrays
        dest_array = (ctypes.c_ubyte * len(dest)).from_buffer(dest)
        source_array = (ctypes.c_ubyte * len(source)).from_buffer(source)

        # Create pointers for length parameter
        dest_len_vlaue = ctypes.c_int(dest_len)
        dest_len_ref = ctypes.byref(dest_len_vlaue)
        result = self.compress_func(dest_array, dest_len_ref, source_array, source_len)
        if result != 0:
            raise RuntimeError(f"Error while compressing data: {result}")
        return dest_len_vlaue.value

    def compress2(self, dest, dest_len, source, source_len, level):
        # Convert bytearray to proper ctypes arrays
        dest_array = (ctypes.c_ubyte * len(dest)).from_buffer(dest)
        source_array = (ctypes.c_ubyte * len(source)).from_buffer(source)

        # Create pointers for length parameter
        dest_len_vlaue = ctypes.c_int(dest_len)
        dest_len_ref = ctypes.byref(dest_len_vlaue)
        result = self.compress2_func(dest_array, dest_len_ref, source_array, source_len, level)
        if result != 0:
            raise RuntimeError(f"Error while compressing data: {result}")
        return dest_len_vlaue.value

    def __del__(self):
        if hasattr(self, 'datexport_dll'):
            # Note: In Python, we don't typically free DLLs explicitly
            pass
