from cx_Freeze import setup, Executable
import sys

sys.setrecursionlimit(5000)

build_exe_options = {
    "packages": ["os", "pyarrow", "numpy", "scipy", "lifelines", "matplotlib"],
    "includes": ["pyarrow._compute_docstrings", "numpy", "scipy.integrate", "lifelines.statistics", "lifelines.fitters", "matplotlib", "pandas.plotting._matplotlib"],
    "include_files": [
        ("data/population_data.xlsx", "data/population_data.xlsx"),
        ("data/preprocessed_male.xlsx", "data/preprocessed_male.xlsx"),
        ("data/preprocessed_female.xlsx", "data/preprocessed_female.xlsx"),
        ("data/preprocessed_general.xlsx", "data/preprocessed_general.xlsx"),
        ("ENinstruction.md", "ENinstruction.md"),
        ("PLinstruction.md", "PLinstruction.md"),
        ("images/icon.png", "images/icon.png")
    ],
    "excludes": ["tkinter"],
}

setup(
    name="pomoka",
    version="1.0",
    description="POMOKA",
    options={"build_exe": build_exe_options},
    executables=[Executable("pomoka.py", base="Win32GUI", icon="icon.ico")],
)
