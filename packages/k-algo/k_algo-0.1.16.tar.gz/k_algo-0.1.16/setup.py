import os
import pathlib
import shutil
from setuptools import setup, Extension, Command, find_packages
from setuptools.command.build_py import build_py as _build_py
from Cython.Build import cythonize

# extensions = [
#     Extension("algo.func01.func01", ["algo/func01/func01.py"]),
#     Extension("algo.func02.func02", ["algo/func02/func02.py"]),
# ]

class build_py_filter_modules(_build_py):
    # 要排除的純 Python 模組（完全限定名稱）
    # EXCLUDE_FQMODS = {
    #     "algo.func01.func01",   # 只排除這個 .py；其他仍會被打包
    #     "algo.func02.func02",
    # }
    EXCLUDE_FQMODS = set()  # 先留空，稍後以程式動態注入

    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        filtered = []
        for pkg, mod, filepath in modules:
            fqname = f"{pkg}.{mod}" if pkg else mod
            if fqname in self.EXCLUDE_FQMODS:
                # 跳過這個純 .py（讓同名 .so 取而代之）
                self.announce(f"Skipping pure module {fqname} ({filepath})", level=2)
                print(f"Skipping pure module {fqname} ({filepath})")
                continue
            filtered.append((pkg, mod, filepath))
        return filtered
    
    # ★ 新增這段：過濾掉被當作 package data 的 .c/.cpp
    def find_data_files(self, package, src_dir):
        files = super().find_data_files(package, src_dir)
        filtered = [f for f in files if not f.lower().endswith((".c", ".cpp"))]
        for f in set(files) - set(filtered):
            self.announce(f"Skipping data file {package}: {f}", level=2)
        return filtered

# === 自訂 Clean Command ===
class CleanCommand(Command):
    """Custom clean command to remove build artifacts and generated files."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        base = pathlib.Path(__file__).parent
        algo_dir = base / "algo"

        # 檔案 pattern
        patterns = ["**/*.c", "**/*.so", "**/*.pyd"]
        for pattern in patterns:
            for path in algo_dir.glob(pattern):
                try:
                    if "fastsum.c" not in str(path.resolve()) :
                        path.unlink()
                    print(f"Removed file {path}")
                except Exception as e:
                    print(f"Failed to remove {path}: {e}")

        # 目錄清理
        dirs = ["build", "dist", "dist_stripped", "wheel_work", "wheelhouse"] + [d.name for d in base.glob("*.egg-info")]
        for d in dirs:
            dpath = base / d
            if dpath.exists():
                try:
                    shutil.rmtree(dpath)
                    print(f"Removed directory {dpath}")
                except Exception as e:
                    print(f"Failed to remove directory {dpath}: {e}")

# 遍歷專案的子資料夾，找到所有 .py 文件
def find_py_files():
    py_files = []
    packages = find_packages(where="."),  # 自動包含所有子套件
    for package in packages[0]:
        package_path = package.replace(".", os.sep)
        if os.path.isdir(package_path):  # 確認 package_path 是一個目錄
            # for root, dirs, files in os.walk(package_path):
            #     for file in files:
            for file in os.listdir(package_path):  # 僅掃描當層
                if file.endswith(".py") and file != "setup.py" and file != "__init__.py" and file != "_version.py" and file != "__main__.py":
                    # 取得完整路徑並添加到 py_files
                    py_files.append(os.path.join(package_path, file))
    return py_files

# 將找到的 .py 文件轉換為 Extension 模組
def make_extensions(py_files):
    extensions = []
    for py_file in py_files:
        # 將檔案名轉換為對應的模組名 (用於 Extension 名稱)
        module_name = py_file.replace(os.path.sep, ".")[:-3]  # 去掉 ".py"
        extensions.append(
            Extension(
                name=module_name,  # 输出的 .pyd 文件名
                sources=[py_file],
                # extra_compile_args=["-O2"],  # 优化编译
                # extra_link_args=["-static-libgcc", "-static-libstdc++", "-static"], # 使用Windows編譯，請開啟這段
                # # extra_link_args=["-shared"],  # 使用linux編譯，請開啟這段
                # language="c"
            )
        )
    return extensions

# 獲取所有 .py 文件並轉換為 Extensions
py_files = find_py_files()
extensions = make_extensions(py_files)

# ★ 用 extensions 自動產生要排除的純 .py 模組清單
exclude_fqmods = {ext.name for ext in extensions}
# 將它塞進 build_py_filter_modules 的類別屬性，取代手動列舉
build_py_filter_modules.EXCLUDE_FQMODS = exclude_fqmods


# 可依平台調整編譯參數（可留空）
extra_compile_args = []
extra_link_args = []
import os
if os.name == "posix":
    extra_compile_args = ["-O3", "-fno-wrapv"]
elif os.name == "nt":
    extra_compile_args = ["/O2"]

extensions.append(
    Extension(
        name="algo.cext.fastsum",                # 匹配最末段模組名 "fastsum"
        sources=["algo/cext/fastsum.c"],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
)

print("== compiled extensions ==")
for n in sorted(exclude_fqmods):
    print("  -", n)
print("==========================")

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={"language_level": 3, "boundscheck": False, "wraparound": False},
    ),
    cmdclass={
        "build_py": build_py_filter_modules,   # ← 註冊
        "clean": CleanCommand,
    },
)
