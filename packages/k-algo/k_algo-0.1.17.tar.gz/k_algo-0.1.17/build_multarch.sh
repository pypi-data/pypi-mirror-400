#!/usr/bin/env bash
set -euo pipefail

# # 若在 x86_64 主機上也要生 aarch64，先啟用 QEMU binfmt（只需跑一次）
# docker run --rm --privileged tonistiigi/binfmt --install arm64 >/dev/null

# # 若在 arm64 主機上也要生 x86_64，先啟用 QEMU binfmt（只需跑一次）
# docker run --rm --privileged tonistiigi/binfmt --install amd64 >/dev/null

# python -m pip install -U pip cibuildwheel

# 同時建兩種架構
export CIBW_ARCHS_LINUX="x86_64 aarch64"
# 只建 CPython 3.11
export CIBW_BUILD="cp311-*"

# 指定兩個架構對應的 manylinux 2.28 基底映像
export CIBW_MANYLINUX_X86_64_IMAGE="quay.io/pypa/manylinux_2_28_x86_64"
export CIBW_MANYLINUX_AARCH64_IMAGE="quay.io/pypa/manylinux_2_28_aarch64"

# 統一給編譯旗標
export CIBW_ENVIRONMENT='CFLAGS="-O3"'

# 跳過測試（跨架構時常用）
export CIBW_TEST_SKIP="*"

# 只保留所選平臺標籤（避免再加 manylinux2014/2_17）
export CIBW_REPAIR_WHEEL_COMMAND='auditwheel repair --only-plat -w {dest_dir} {wheel}'

# 開始建
cibuildwheel --platform linux

echo "==> wheels are in wheelhouse/"
