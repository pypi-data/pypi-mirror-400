#!/usr/bin/env bash
set -euo pipefail

# docker run --rm --privileged tonistiigi/binfmt --install arm64

python -m pip install -U pip "cibuildwheel"

export CIBW_ARCHS_LINUX=aarch64
export CIBW_BUILD="cp311-*"
export CIBW_MANYLINUX_AARCH64_IMAGE=quay.io/pypa/manylinux_2_28_aarch64
export CIBW_ENVIRONMENT='CFLAGS="-O3"'
# 可選：不在 QEMU 下跑測試
export CIBW_TEST_SKIP="*"

# 僅保留 manylinux_2_28 標籤（不加最低/legacy）
export CIBW_REPAIR_WHEEL_COMMAND='auditwheel repair --only-plat -w {dest_dir} {wheel}'

cibuildwheel --platform linux

echo "==> wheels are in wheelhouse/"
