#!/usr/bin/env python3
"""
Hermes Agent SMB 共享文件夹挂载工具
供其他Agent直接调用的入口

用法:
  python3 mount_smb.py                # 挂载（如已挂载则跳过）
  python3 mount_smb.py --check        # 检查挂载状态
  python3 mount_smb.py --unmount      # 卸载
  python3 mount_smb.py --test         # 测试读写
"""

import subprocess
import os
import sys

# ── 配置参数（与SKILL.md保持一致） ──────────────
SMB_SERVER_IP = "192.168.1.3"
SMB_SHARE_NAME = "agent-video-shared"
SMB_MOUNT_POINT = "/mnt/video-shared"
SMB_USERNAME = "86150"
SMB_VERSION = "3.0"
SMB_CREDENTIALS = os.path.expanduser("~/.smbcredentials")
# ──────────────────────────────────────────────


def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    if check and result.returncode != 0:
        return False, result.stderr.strip()
    return True, result.stdout.strip()


def is_mounted():
    ok, out = run(f"mount | grep '{SMB_MOUNT_POINT}'", check=False)
    return ok and SMB_MOUNT_POINT in out


def mount():
    if is_mounted():
        print(f"✅ 已挂载: {SMB_MOUNT_POINT}")
        return True

    print(f"🔗 正在挂载 //{SMB_SERVER_IP}/{SMB_SHARE_NAME} → {SMB_MOUNT_POINT} ...")

    # 确保挂载点存在
    os.makedirs(SMB_MOUNT_POINT, exist_ok=True)

    # 有凭据文件则用凭据，否则交互式
    if os.path.exists(SMB_CREDENTIALS):
        cmd = (f"sudo mount -t cifs //{SMB_SERVER_IP}/{SMB_SHARE_NAME} {SMB_MOUNT_POINT} "
               f"-o credentials={SMB_CREDENTIALS},uid=1000,gid=1000,vers={SMB_VERSION}")
    else:
        cmd = (f"sudo mount -t cifs //{SMB_SERVER_IP}/{SMB_SHARE_NAME} {SMB_MOUNT_POINT} "
               f"-o username={SMB_USERNAME},vers={SMB_VERSION}")

    ok, msg = run(cmd, check=False)
    if ok:
        print(f"✅ 挂载成功: {SMB_MOUNT_POINT}")
        return True
    else:
        print(f"❌ 挂载失败: {msg}")
        return False


def unmount():
    if not is_mounted():
        print(f"⚠️  未挂载: {SMB_MOUNT_POINT}")
        return True

    ok, msg = run(f"sudo umount {SMB_MOUNT_POINT}", check=False)
    if ok:
        print(f"✅ 已卸载: {SMB_MOUNT_POINT}")
        return True
    else:
        print(f"❌ 卸载失败: {msg}")
        return False


def test_rw():
    if not is_mounted():
        print("❌ 未挂载，无法测试")
        return False

    test_file = f"{SMB_MOUNT_POINT}/.hermes_test.txt"
    ok, msg = run(f"echo 'Hermes Agent SMB test: {os.urandom(8).hex()}' | sudo tee {test_file}", check=False)
    if not ok:
        print(f"❌ 写入测试失败: {msg}")
        return False

    ok, msg = run(f"cat {test_file}", check=False)
    if not ok:
        print(f"❌ 读取测试失败: {msg}")
        return False

    run(f"sudo rm -f {test_file}", check=False)
    print(f"✅ 读写测试通过")
    return True


def check():
    if is_mounted():
        ok, out = run(f"df -h {SMB_MOUNT_POINT} | tail -1")
        print(f"✅ 已挂载: {SMB_MOUNT_POINT}")
        print(f"   信息: {out}")
        ok2, out2 = run(f"ls {SMB_MOUNT_POINT}/", check=False)
        if ok2:
            items = out2.split('\n')[:10]
            print(f"   内容: {items}")
        return True
    else:
        print(f"❌ 未挂载: {SMB_MOUNT_POINT}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--check":
            sys.exit(0 if check() else 1)
        elif cmd == "--unmount":
            sys.exit(0 if unmount() else 1)
        elif cmd == "--test":
            sys.exit(0 if test_rw() else 1)
        else:
            print(f"未知参数: {cmd}")
            sys.exit(1)
    else:
        # 默认：挂载
        sys.exit(0 if mount() else 1)
