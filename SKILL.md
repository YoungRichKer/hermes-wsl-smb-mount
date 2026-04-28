# Hermes WSL SMB 共享文件夹挂载配置

> 让 Hermes Agent (WSL) 自动挂载电脑B的共享文件夹，用于视频素材交换。

---

## 适用场景

- 电脑A（WSL + Hermes Agent）需要访问电脑B上的视频素材
- 繁殖引擎产出视频自动存到共享文件夹
- 跨设备视频素材交换

---

## 前置条件

| 条件 | 说明 |
|:----|:------|
| 电脑B | Windows，有固定IP（局域网） |
| 电脑B操作 | 建共享文件夹 → 设置Everyone读/写权限 |
| WSL网络 | 能与电脑B互通 |

---

## 配置参数

所有参数集中在 SKILL.md 顶部，方便修改：

```yaml
# ── SMB 共享目录配置 ──────────────
SMB_SERVER_IP: "192.168.1.3"           # 电脑B的IP地址
SMB_SHARE_NAME: "agent-video-shared"   # 共享文件夹名称（不含路径）
SMB_MOUNT_POINT: "/mnt/video-shared"   # WSL挂载点
SMB_USERNAME: "86150"                  # 电脑B的Windows用户名
SMB_VERSION: "3.0"                     # SMB协议版本 (2.0 / 3.0)
```

> **注意**：SMB密码不会写在skill里，首次挂载时手动输入，或通过 `~/.smbcredentials` 文件管理。

---

## 配置步骤

### 步骤1：电脑B — 创建共享文件夹

1. 在电脑B上新建文件夹（如 `D:\video-shared\`）
2. 右键 → 属性 → **共享** → 共享
3. 添加 **Everyone**，权限设为 **读取/写入**
4. 确认共享名（本例为 `agent-video-shared`）
5. `ipconfig` 查看电脑B的 IPv4 地址

### 步骤2：WSL — 安装SMB客户端

```bash
sudo apt update
sudo apt install -y smbclient cifs-utils
```

### 步骤3：WSL — 测试连接

```bash
# 测试能否访问共享（会提示输入密码）
smbclient //<SERVER_IP>/<SHARE_NAME> -U <USERNAME>

# 示例：
smbclient //192.168.1.3/agent-video-shared -U 86150
```

输入Windows密码后，如果能进入 `smb: \>` 提示符，说明连接成功，输入 `exit` 退出。

### 步骤4：WSL — 创建挂载点 & 挂载

```bash
# 创建挂载目录
sudo mkdir -p /mnt/video-shared

# 临时挂载（测试用，重启后失效）
sudo mount -t cifs //<SERVER_IP>/<SHARE_NAME> /mnt/video-shared \
  -o username=<USERNAME>,vers=<SMB_VERSION>

# 示例：
sudo mount -t cifs //192.168.1.3/agent-video-shared /mnt/video-shared \
  -o username=86150,vers=3.0
```

### 步骤5：WSL — 配置自动挂载（fstab）

```bash
# 创建凭据文件（避免密码明文写在fstab里）
sudo nano ~/.smbcredentials
```

写入：
```
username=86150
password=你的Windows密码
domain=WORKGROUP
```

```bash
# 设置权限（仅自己可读）
chmod 600 ~/.smbcredentials

# 编辑fstab
sudo nano /etc/fstab
```

在末尾添加：
```
//<SERVER_IP>/<SHARE_NAME>  <MOUNT_POINT>  cifs  credentials=/home/kameko/.smbcredentials,uid=1000,gid=1000,vers=<SMB_VERSION>,x-systemd.automount,noauto  0  0
```

> **注意**：使用 `x-systemd.automount,noauto` 可以做到按需挂载——只在访问挂载点时自动连接，WSL启动时不会卡住。

### 步骤6：WSL — 验证挂载

```bash
# 查看挂载点内容
ls -la /mnt/video-shared/

# 测试写入
echo "test" | sudo tee /mnt/video-shared/test.txt

# 测试读取
cat /mnt/video-shared/test.txt

# 删除测试文件
sudo rm /mnt/video-shared/test.txt
```

### 步骤7：WSL — 触发自动挂载

```bash
# 方式1：重启WSL
wsl --shutdown
# 重新打开WSL终端

# 方式2：直接访问挂载点触发
ls /mnt/video-shared/
```

---

## 验证清单

- [ ] `ls /mnt/video-shared/` 能列出电脑B的文件
- [ ] `touch /mnt/video-shared/.test` 能创建文件
- [ ] WSL重启后自动挂载生效
- [ ] SMB密码不暴露（存在 `~/.smbcredentials` 中）

---

## 给其他 Agent 的调用方式

其他 Hermes Agent 想使用这个配置时，只需在对话中说：

> **"加载 SMB 挂载 skill"**

或者手动加载 skill 后执行以下命令验证：

```bash
# 检查挂载状态
ls -la /mnt/video-shared/

# 如果未挂载，手动触发
sudo mount /mnt/video-shared

# 查看当前挂载信息
mount | grep cifs
```

---

## 文件夹结构

挂载成功后，素材按以下规范存放：

```
/mnt/video-shared/
├── products/
│   └── SP001-产品名/
│       ├── raw/A~F/        ← 原始素材按A~F分类
│       ├── clips/A~F/      ← 裁切后的精华片段
│       └── outputs/        ← 繁殖引擎成品
├── ai_generated/
│   └── 待审核/               ← AI生成素材暂存
└── shared_docs/             ← 共享文档（产品资料等）
```

---

## 故障排查

| 问题 | 原因 | 解决 |
|:----|:----|:-----|
| `mount error(112): Host is down` | SMB版本不匹配 | 尝试 `vers=2.0` 或 `vers=1.0` |
| `mount error(13): Permission denied` | 用户名/密码错误 | 检查 `~/.smbcredentials` |
| WSL启动卡住 | fstab自动挂载超时 | 改用 `x-systemd.automount,noauto` |
| 文件权限问题 | uid/gid不匹配 | fstab中加 `uid=1000,gid=1000` |
| `mount error(5): Input/output error` | Windows防火墙拦截 | 电脑B防火墙开放SMB端口(445) |
