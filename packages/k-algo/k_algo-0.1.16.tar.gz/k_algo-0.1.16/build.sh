python setup.py clean

# 0) 先建出原始 wheel
python -m build --wheel

# 1) 解包到暫存資料夾（會自動展開 dist/*.whl）
python -m wheel unpack dist/*.whl -d wheel_work

# 2) 刪掉 wheel 內容裡除了 __init__.py 以外的 .py
#    （這裡假設你的套件叫 algo）
# find wheel_work -type f -path "*/algo/*" -name "*.py" ! -name "__init__.py" -delete
find wheel_work -type f -path "*/algo/*" \
  \( -name "*.py" -o -name "*.c" \) \
  ! -name "__init__.py" ! \
  -delete

# 3) 重新打包（會自動重算 RECORD 雜湊與大小）
#    注意 pack 的參數要指向「解開後的那個子資料夾」
[ ! -d dist_stripped ] && mkdir -v dist_stripped
python -m wheel pack wheel_work/* -d dist_stripped

# # 4) 驗證新 wheel 內容（應該看不到 func01.py / func02.py）
# python - <<'PY'
# import zipfile, glob
# whl = sorted(glob.glob("dist_stripped/*.whl"))[-1]
# print("WHEEL:", whl)
# with zipfile.ZipFile(whl) as z:
#     for n in z.namelist():
#         if n.startswith("algo/"):
#             print(n)
# PY

# # 5) 安裝測試
# uv pip install --force-reinstall dist_stripped/*.whl
# python -c "import algo, sys; print(algo.__file__)"
