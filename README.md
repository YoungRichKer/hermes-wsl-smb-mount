# Hermes WSL SMB 共享文件夹挂载配置

## 📁 文件说明

```
hermes-wsl-smb-mount/
├── SKILL.md              ← 技能文档（主文件，含完整配置步骤）
├── mount_smb.py          ← 可执行脚本（挂载/检查/测试）
├── hermes-skill.json     ← Hermes技能定义元数据
└── LICENSE
```

## 🚀 快速使用

其他 Hermes Agent 可以通过加载此 skill 后执行：

```bash
# 挂载共享文件夹
python3 mount_smb.py

# 检查挂载状态
python3 mount_smb.py --check

# 卸载
python3 mount_smb.py --unmount

# 读写测试
python3 mount_smb.py --test
```

## 🔧 配置参数

编辑 `hermes-skill.json` 或 `mount_smb.py` 顶部的参数：

| 参数 | 默认值 | 说明 |
|:----|:------|:-----|
| SMB_SERVER_IP | 192.168.1.3 | 电脑B的IP |
| SMB_SHARE_NAME | agent-video-shared | 共享文件夹名 |
| SMB_MOUNT_POINT | /mnt/video-shared | 挂载点 |
| SMB_USERNAME | 86150 | Windows用户名 |
| SMB_VERSION | 3.0 | SMB协议版本 |

## 📦 依赖

- smbclient (`sudo apt install smbclient`)
- cifs-utils (`sudo apt install cifs-utils`)
