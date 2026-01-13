import json
import os


def scan_dir_fast(path):
    file_infos = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file():
                info = entry.stat()
                file_infos.append({
                    "path": entry.path,
                    "size": info.st_size
                })
    return file_infos


def scan_dir(dir_name, result_file):
    # dir_name r"/share/fulltext/errors"
    # result_file "file_info_errors.txt"
    for root, dirs, files in os.walk(dir_name):
        print(root)
        lists = scan_dir_fast(root)
        with open(result_file, "a", encoding="utf-8") as file:
            for i in lists:
                if i:
                    file.write(json.dumps(i, ensure_ascii=False) + "\n")
