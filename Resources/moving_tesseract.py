import shutil
import os
from pyuac import main_requires_admin



app_folder = os.path.abspath(".\\")
original_location = fr"{app_folder}" + "\\tesseract_path\\Tesseract-OCR"

prog_file_location = "C:\\Program Files\\"
prog_file_file = r"C:\\Program Files\\Tesseract-OCR"


@main_requires_admin
def move(src, dst):
    shutil.move(src, dst)


def check_tesseract_folder(path):
    if os.path.exists(path):
        print("Folder already in program files")

    else:
        move(original_location, prog_file_location)
        print("Folder moved!")


def check_env_vars(path):
    if path in os.getenv("PATH").split(";"):
        print("Folder Already in path")

    else:
        os.system(fr'cmd /c "setx PATH "{path};%PATH%"')



check_tesseract_folder(prog_file_file)
check_env_vars(prog_file_file)


