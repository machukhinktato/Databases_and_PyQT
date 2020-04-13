import sys
from cx_Freeze import setup
from cx_Freeze import Executable

build_exe_options = {
    "packages": ["common", "server", "logs", "unit_tests"],
}
setup(
    name="messenger_server_part",
    version="0.4.1",
    description="messenger_server_part",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable(
        'server.py',
        # base='Win32GUI',
        targetName='server.exe'
    )]
)
