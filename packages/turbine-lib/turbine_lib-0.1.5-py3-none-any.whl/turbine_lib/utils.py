def compare_files_byte_by_byte(file1_path, file2_path):
    """
    比较两个文件的每个字节是否完全相同

    Args:
        file1_path (str): 第一个文件路径
        file2_path (str): 第二个文件路径

    Returns:
        bool: 如果两个文件完全相同返回True，否则返回False
    """
    try:
        with open(file1_path, 'rb') as file1, open(file2_path, 'rb') as file2:
            # 按块读取文件进行比较，避免大文件占用过多内存
            while True:
                chunk1 = file1.read(8192)  # 每次读取8KB
                chunk2 = file2.read(8192)

                # 如果两个文件都到达末尾，则文件相同
                if not chunk1 and not chunk2:
                    return True

                # 如果其中一个文件结束而另一个没有，则文件不同
                if not chunk1 or not chunk2:
                    return False

                # 如果当前块不相同，则文件不同
                if chunk1 != chunk2:
                    return False

    except FileNotFoundError as e:
        print(f"文件未找到: {e}")
        return False
    except Exception as e:
        print(f"比较文件时出错: {e}")
        return False


def compare_files_detailed(file1_path, file2_path):
    """
    比较两个文件的每个字节，并提供详细的差异信息

    Args:
        file1_path (str): 第一个文件路径
        file2_path (str): 第二个文件路径

    Returns:
        dict: 包含比较结果和详细信息的字典
    """
    result = {
        'same': False,
        'size1': 0,
        'size2': 0,
        'first_diff_pos': -1,
        'error': None
    }

    try:
        with open(file1_path, 'rb') as file1, open(file2_path, 'rb') as file2:
            # 获取文件大小
            file1.seek(0, 2)  # 移动到文件末尾
            file2.seek(0, 2)
            result['size1'] = file1.tell()
            result['size2'] = file2.tell()

            # 重置文件指针
            file1.seek(0)
            file2.seek(0)

            # 如果文件大小不同，则肯定不相同
            if result['size1'] != result['size2']:
                return result

            position = 0
            while True:
                byte1 = file1.read(1)
                byte2 = file2.read(1)

                # 如果两个文件都到达末尾，则文件相同
                if not byte1 and not byte2:
                    result['same'] = True
                    break

                # 如果字节不同，记录位置并退出
                if byte1 != byte2:
                    result['first_diff_pos'] = position
                    break

                position += 1

    except FileNotFoundError as e:
        result['error'] = f"文件未找到: {e}"
    except Exception as e:
        result['error'] = f"比较文件时出错: {e}"

    return result

def compare_files(file_path1, file_path2):
    # 简单比较
    are_same = compare_files_byte_by_byte(file_path1, file_path2)
    print(f"文件是否相同: {are_same}")

    # 详细比较
    result = compare_files_detailed(file_path1, file_path2)
    if result['error']:
        print(f"错误: {result['error']}")
    elif result['same']:
        print("文件完全相同")
    else:
        if result['size1'] != result['size2']:
            print(f"文件大小不同: {result['size1']} vs {result['size2']}")
        else:
            print(f"文件大小相同但内容不同，第一个差异在位置: {result['first_diff_pos']}")
if __name__ == '__main__':
    # 简单比较
    compare_files(r'./font/standard/1107296298.fontbin', r'./font/output_17-11-2025-14-01/1107296298.fontbin')

