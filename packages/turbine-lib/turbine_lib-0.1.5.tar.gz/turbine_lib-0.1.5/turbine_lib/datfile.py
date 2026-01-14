import logging

from turbine_lib.binarydata import BinaryData
from turbine_lib.database import Database
from turbine_lib.datexportapi import DatExportApi
from turbine_lib.ddssubfile import DDSSubfile
from turbine_lib.fontsubfile import SubfileFONT
from turbine_lib.subfile import string_from_file_type, file_type_from_file_contents, FILE_TYPE, Subfile
from turbine_lib.subfiledata import SubfileData
from turbine_lib.textsubfile import TextSubfile


class SubfileInfo:

    def __init__(self):
        self.file_id = -1
        self.size = -1
        self.iteration = -1

    def __lt__(self, other):
        return self.file_id < other.file_id


class DatFile:
    # Class variable - shared by all instances
    api_ = DatExportApi()

    def __init__(self, file_handle):
        self.file_handle_ = file_handle
        self.initialized_ = False
        self.files_info_ = {}  # Dictionary mapping file_id to SubfileInfo
        self.filename_ = ""
        self.export_data_buf_ = BinaryData(bytearray(64 * 1024 * 1024))  # 64 MB - max file size

    def __del__(self):
        self.deinit()

    def init(self, filename):
        if self.initialized_:
            self.deinit()

        if self.api_.open_dat_file(self.file_handle_, filename, 130) == self.file_handle_:
            self.initialized_ = True
            self.filename_ = filename
            self.load_all_files_info()
            return True

        return False

    def load_all_files_info(self):
        subfiles_num = self.api_.get_num_subfiles(self.file_handle_)
        file_ids = [0] * subfiles_num
        sizes = [0] * subfiles_num
        iterations = [0] * subfiles_num

        # Initialize lists with dummy values
        for i in range(subfiles_num):
            file_ids[i] = 0
            sizes[i] = 0
            iterations[i] = 0

        if subfiles_num > 0:
            self.api_.get_subfile_sizes(self.file_handle_, file_ids, sizes, iterations, 0, subfiles_num)

        for i in range(subfiles_num):
            file_info = SubfileInfo()
            file_info.file_id = file_ids[i]
            file_info.size = sizes[i]
            file_info.iteration = iterations[i]
            self.files_info_[file_info.file_id] = file_info

    def deinit(self):
        if self.initialized_:
            self.api_.close_dat_file(self.file_handle_)
            self.files_info_.clear()
            self.initialized_ = False

    def initialized(self):
        return self.initialized_

    def get_filename(self):
        return self.filename_

    def get_subfile_info(self, file_id):
        if file_id in self.files_info_:
            return self.files_info_[file_id]
        else:
            return SubfileInfo()

    def get_files_num_in_dat_file(self):
        return self.api_.get_num_subfiles(self.file_handle_)

    def patch_all_files_from_database(self, db,callback=None):
        patched_files_num = 0

        file = db.get_next_file()
        i = 0
        total_files = db.count_rows()
        logging.info("Patching all files from database...")

        while not file.empty():
            if i > 0 and total_files > 0 and i * 100 // total_files != (i - 1) * 100 // total_files:
                logging.info(f"Completed {i * 100 // total_files}%")
                if callback:
                    callback(i * 100 // total_files)
                # gl.progress_wnd.UpdateStageText(f"正在安装第{i}条翻译到dat文件...")
                # gl.progress_wnd.UpdatePercent(int(i * 100 / total_files))
            i += 1

            if not file.options or "fid" not in file.options:
                logging.info(f"Incorrect db entry - no file_id specified")
                file = db.get_next_file()
                continue

            self.patch_file(file)
            patched_files_num += 1
            file = db.get_next_file()

        return patched_files_num

    def patch_file(self, file_data=None, file_id=None, file_type=None, path_to_file=None, version=-1, iteration=-1):
        if file_data is not None:
            # Patch with SubfileData
            if not file_data.options or "fid" not in file_data.options:
                print("Trying to patch file, but file id is not specified, skipping!")
                return

            file_id_inner = int(file_data.options["fid"])

            if file_id_inner not in self.files_info_:
                print(f"Trying to patch file, not existing in files_info. File id = {file_id_inner}")
                return

            file_info = self.files_info_[file_id_inner]

            existing_file_version = 0  # will be evaluated with api_.GetSubfileData
            size, existing_file_version = self.api_.get_subfile_data(
                self.file_handle_, file_id_inner, self.export_data_buf_.data(), existing_file_version)

            if size <= 0:
                print(f"Trying to patch file, not existing in .dat file. File id = {file_id_inner}")
                return

            old_data = self.export_data_buf_.cut_data(0, size)

            # Check file size is reasonable
            if size > 64 * 1024 * 1024:  # Exceeds buffer size
                print(f"File size too large for buffer. File id = {file_id_inner}, Size = {size}")
                return

            # Build file for import
            try:
                file_binary = self.build_for_import(old_data, file_data)
            except Exception as e:
                print(f"Exception in build_for_import: {e} file_id {file_id_inner}")
                raise e
                return

            if version == -1:
                version = existing_file_version

            if iteration == -1:
                iteration = file_info.iteration

            # Convert BinaryData to bytearray for ctypes
            file_bytes = file_binary.data()
            self.api_.put_subfile_data(
                self.file_handle_, file_id_inner, file_bytes, 0, len(file_bytes), version, iteration, False)

        elif file_id is not None and file_type is not None and path_to_file is not None:
            # Patch with file path
            new_data = BinaryData(bytearray(64 * 1024 * 1024))

            try:
                with open(path_to_file, 'rb') as f:
                    file_content = f.read()
                    data_size = len(file_content)
                    new_data.data_[:data_size] = file_content
            except Exception as e:
                print(f"Error reading file {path_to_file}: {e}")
                return

            imported_subfile = SubfileData()
            imported_subfile.binary_data = new_data.cut_data(0, data_size)
            imported_subfile.options = {"ext": string_from_file_type(file_type), "fid": file_id}

            self.patch_file(imported_subfile, version=version, iteration=iteration)

    def get_existing_file_type(self, file_id):
        version = 0
        size, version = self.api_.get_subfile_data(
            self.file_handle_, file_id, self.export_data_buf_.data(), version)
        return file_type_from_file_contents(file_id, self.export_data_buf_)

    def perform_operation_on_all_subfiles(self, operation, callback=None):
        if not self.files_info_:
            self.load_all_files_info()

        print("Performing operation on all files...")
        i = 0
        for file_id, info in self.files_info_.items():
            if i > 0 and len(self.files_info_) > 0 and i * 100 // len(self.files_info_) != (i - 1) * 100 // len(
                    self.files_info_):
                logging.info(f"Completed {i * 100 // len(self.files_info_)}%")
                if (callback):
                    callback(i * 100 // len(self.files_info_))
            operation(info)
            i += 1

    def export_files_by_type(self, file_type, db_or_path, callback):
        num_files = 0

        if isinstance(db_or_path, Database):
            # Export to database
            def operation(info):
                nonlocal num_files
                file_type_existing = self.get_existing_file_type(info.file_id)
                if file_type_existing == file_type:
                    self.export_file_by_id(info.file_id, db_or_path)
                    num_files += 1

            self.perform_operation_on_all_subfiles(operation, callback)
            return num_files
        else:
            # Export to directory
            path_to_directory = db_or_path

            def operation(info):
                nonlocal num_files
                file_type_existing = self.get_existing_file_type(info.file_id)
                if file_type_existing == file_type:
                    target_path = f"{path_to_directory}/{info.file_id}"
                    self.export_file_by_id(info.file_id, target_path)
                    num_files += 1

            self.perform_operation_on_all_subfiles(operation)
            return num_files

    def export_file_by_id(self, file_id, target):
        if file_id <= 0:
            print("Invalid file ID!")
            return
        version = 0
        size, version = self.api_.get_subfile_data(
            self.file_handle_, file_id, self.export_data_buf_.data(), version)

        data = self.export_data_buf_.cut_data(0, size)
        file_result = self.build_for_export(file_id, data)

        if isinstance(target, Database):
            # Export to database
            target.push_file(file_result)
        else:
            # Export to file path
            ext = string_from_file_type(self.get_existing_file_type(file_id))
            target_file_path = f'{target}{ext}'
            # target_file_path = f'{target}.dds'
            try:
                with open(target_file_path, 'wb') as f:
                    if ext == ".txt":
                        f.write(file_result.text_data.encode("utf-8"))
                    else:
                        f.write(file_result.binary_data.data())
            except Exception as e:
                print(f"Error writing file {target_file_path}: {e}")

    def get_file_version(self, file_id):
        return self.api_.get_subfile_version(self.file_handle_, file_id)

    def get_file(self, file_id):
        version = 0
        size, version = self.api_.get_subfile_data(
            self.file_handle_, file_id, self.export_data_buf_.data(), version)
        data = self.export_data_buf_.cut_data(0, size)
        return self.build_for_export(file_id, data)

    def build_for_import(self, old_data, outer_data):
        if not outer_data.options or "ext" not in outer_data.options:
            print(f"No extension established for file with id {outer_data.options.get('fid', 'unknown')}")
            return BinaryData()

        # In Python, we'll directly call the appropriate subfile class
        ext = outer_data.options["ext"]
        if ext == ".txt":
            return TextSubfile.build_for_import(old_data, outer_data)
        elif ext == ".dds":
            for_import = DDSSubfile.build_for_import(old_data, outer_data)
            return for_import
        elif ext == ".fontbin":
            for_import = SubfileFONT.build_for_import(old_data, outer_data)
            return for_import
        elif ext == ".subfile":
            return outer_data.binary_data
        # Add other file types as needed
        else:
            # Default implementation for unknown types
            return old_data  # Just return the original data

    def compress(self, buffer):
        # Handle compression (reverse of decompression)
        decompressed_length = len(buffer)

        # Create buffer for compressed data (with 4 bytes extra for length header)
        compressed_buffer = bytearray(decompressed_length + 1000)  # Extra space for compression
        compressed_length = decompressed_length + 1000  # Using list to pass by reference

        # Compress the data
        compressed_length = self.api_.compress2(compressed_buffer, compressed_length, buffer.data(),
                                                decompressed_length, 9)

        # Create final buffer with length header
        final_buffer = bytearray(4 + compressed_length)

        # Write decompressed length as header (little endian)
        final_buffer[0] = decompressed_length & 0xFF
        final_buffer[1] = (decompressed_length >> 8) & 0xFF
        final_buffer[2] = (decompressed_length >> 16) & 0xFF
        final_buffer[3] = (decompressed_length >> 24) & 0xFF

        # Copy compressed data
        for i in range(compressed_length):
            final_buffer[4 + i] = compressed_buffer[i]

        # Update buffer
        return BinaryData(final_buffer)

    def build_for_export(self, file_id, inner_data):
        file_type = file_type_from_file_contents(file_id, inner_data)
        result = SubfileData()

        if file_type == FILE_TYPE.TEXT:
            result = TextSubfile.build_for_export(inner_data)
        elif file_type == FILE_TYPE.DDS:
            result = DDSSubfile.build_for_export(inner_data)
        elif file_type == FILE_TYPE.FONT:
            result = SubfileFONT.build_for_export(inner_data)
        # Add other file types as needed
        else:
            # Default implementation for unknown types
            result.binary_data = inner_data

        result.options["fid"] = file_id
        return result
