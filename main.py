import os
import pathlib
import zipfile

import cchardet as chardet
from colorama import init, deinit, Fore
from dynaconf import settings

settings.setenv("general")
path_vam = pathlib.Path(settings.VAM_ROOT)
path_add = path_vam.joinpath('AddonPackages')
targets = settings.TARGETS

settings.setenv("console_write")
do_console_write = settings.CONSOLE_WRITE
pre_lines = settings.PRE_LINES
post_lines = settings.POST_LINES

settings.setenv("file_write")
do_file_write = settings.FILE_WRITE
file_write_dir = settings.FILE_WRITE_DIR


def go_get(target_zip, target_file):
    with zipfile.ZipFile(target_zip) as myzip:
        with myzip.open(target_file) as myfile:
            file_bytes = myfile.read()
            file_encoding = chardet.detect(file_bytes)['encoding']
            if file_encoding is not None:
                file_text = file_bytes.decode(file_encoding)
                
                if do_file_write:
                    for target in targets:
                        if target in file_text:
                            target_file_for_path = target_file.split("\\")[-1]
                            with open(f'{file_write_dir}\\{target_file_for_path}', 'w') as f:
                                f.write(file_text)
                
                if do_console_write:
                    file_lines = file_text.split('\r\n')
                    file_length = len(file_lines)

                    for idx, text_line in enumerate(file_lines):
                        for target in targets:
                            if target in text_line:
                                init()

                                print()
                                header1 = f'{Fore.RESET}.VAR ABS PATH: {Fore.MAGENTA}{target_zip}{Fore.RESET}'
                                header2 = f'{Fore.RESET}.CS (IN .VAR): {Fore.MAGENTA}{target_file}{Fore.RESET}'
                                print(header1, '\n', header2, sep='')
                                print()

                                for i in range(pre_lines, 0, -1):
                                    print(f'{idx - i:<5}│ {file_lines[idx - i]}')

                                print(f'{Fore.LIGHTWHITE_EX}{idx:<5}│ {Fore.RED}{file_lines[idx]}{Fore.RESET}')

                                for i in range(1, post_lines, 1):
                                    if idx+i < file_length:
                                        print(f'{idx + i:<5}│ {file_lines[idx + i]}')

                                deinit()
                                input()


def run_fast_scandir(dir, ext):    # dir: str, ext: list

    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)

    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files


if __name__ == "__main__":
    # _ is a temp or throw away variable
    _, zip_files = run_fast_scandir(path_add.absolute(), ['.var'])

    for zip_file in zip_files:
        try:
            zip_contents = zipfile.ZipFile(zip_file).namelist()
            for file in zip_contents:
                if '.cs' in file:
                    go_get(target_zip=zip_file, target_file=file)

        except zipfile.BadZipFile:
            print(f'BROKEN ZIP: {zip_file}')