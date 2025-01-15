from cx_Freeze import setup, Executable
import sys

# Zwiększ limit rekursji
sys.setrecursionlimit(5000)

# Opcje build_exe
build_exe_options = {
    "packages": ["os", "pyarrow", "numpy", "scipy", "lifelines", "matplotlib"],
    "includes": ["pyarrow._compute_docstrings", "numpy", "scipy.integrate", "lifelines.statistics", "lifelines.fitters", "matplotlib", "pandas.plotting._matplotlib"],  # Wymuś dołączenie
    "include_files": [
        ("data/magicdata.xlsx", "data/magicdata.xlsx"),
        ("data/dane_mezczyzni.xlsx", "data/dane_mezczyzni.xlsx"),
        ("data/dane_kobiety.xlsx", "data/dane_kobiety.xlsx"),
        ("data/dane_ogolne.xlsx", "data/dane_ogolne.xlsx"),
        ("ENinstruction.md", "ENinstruction.md"),
        ("PLinstruction.md", "PLinstruction.md"),
        ("images/icon.png", "images/icon.png")
    ],
    "excludes": ["tkinter"],  # Wyklucz nieużywane moduły
}

# Konfiguracja cx_Freeze
setup(
    name="pomoka",
    version="1.0",
    description="POMOKA",
    options={"build_exe": build_exe_options},
    executables=[Executable("pomoka.py", base=None)],
)
