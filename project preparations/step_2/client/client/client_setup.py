import sys
from sqlalchemy.sql import default_comparator
from cx_Freeze import setup
from cx_Freeze import Executable

build_exe_options = {
    "packages": ["common", "client", "logs", "unit_tests"],
}
setup(
    name="messenger_client_part",
    version="0.4.1",
    description="messenger_client_part",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable(
        'client.py',
        # base='Win32GUI',
        targetName='client.exe'
    )]
)
