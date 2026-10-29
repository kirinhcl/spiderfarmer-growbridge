# Spider Farmer GrowBridge

[English](README.md) | 简体中文

通过本地蓝牙连接 Spider Farmer GGS 控制器，为 LLM 提供环境监测、历史查询、插座、灯和风机控制，以及定时水泵工具。

这是独立开发的早期版本，与 Spider Farmer 官方无关联。当前已经在 **macOS + AC5（广播名称 SF-GGS-PS5、固件 3.2、明文协议 v1）** 上验证协议读取、插座开关、调光和调速。Linux/树莓派后端和部署入口已提供；树莓派蓝牙实机验证尚未完成。加密 v2 固件会被识别并拒绝控制。

## 界面预览

以下截图来自通过本地蓝牙连接到 Mac 的真实 AC5，展示截图时的环境读数、采集历史和设备状态。

**桌面总览**：环境读数、历史曲线、设备控制和最近操作。

![GrowBridge 桌面控制台：真实 AC5 环境读数和采集历史曲线](docs/images/dashboard-overview.jpg)

<details>
<summary>展开查看设备控制与手机布局</summary>

**设备控制**：灯光亮度、风机速度、水泵定时运行和电源插座。

![GrowBridge 设备控制与电源插座，展示真实 AC5 设备状态](docs/images/dashboard-controls.jpg)

**手机布局**：窄屏上的相同控制功能。

<img src="docs/images/dashboard-mobile.jpg" alt="GrowBridge 手机设备控制界面，展示真实 AC5 设备状态" width="375">

</details>

## 工作方式

```text
LLM / Codex
   │ MCP stdio（本机或经 SSH）
   ▼
GrowBridge MCP 客户端
   │ 带认证的本机 HTTP
   ▼
GrowBridge 常驻服务 ─── SQLite 历史与操作记录
   │ 单一蓝牙连接
   ▼
Spider Farmer AC5 / GGS
```

MCP 进程不直接占用蓝牙。常驻服务集中执行命令、校验回读，并维护历史。默认 API 仅监听 `127.0.0.1:8766`；每次安装生成独立访问令牌，客户端从私有配置读取，不把令牌写进 MCP 配置。

当前版本支持按需控制、持续采集和本地网页控制台，不包含无人值守环境优化、自动灌溉计划、MQTT 或云端模型。

## 安装

需要 Python 3.11+。Mac 还需要 Xcode 命令行工具；Linux 需要 BlueZ 和系统 D-Bus。

```sh
git clone https://github.com/kirinhcl/spiderfarmer-growbridge.git
cd spiderfarmer-growbridge
python3 -m venv .venv
.venv/bin/python -m pip install -c constraints-tested.txt .
.venv/bin/growbridge scan
```

Mac 首次使用会编译并启动 `GrowBridge BLE` 原生辅助程序，请允许它使用蓝牙。扫描结果包含这台机器可用的设备地址。把扫描得到的地址填入下面命令：

```sh
.venv/bin/growbridge init --device YOUR_SCANNED_ADDRESS
.venv/bin/growbridge serve
```

另开一个终端查看状态：

```sh
.venv/bin/growbridge status
```

默认只读。确认接线后，在私有配置 `~/.config/spiderfarmer-growbridge/config.toml` 中设置 `controls_enabled = true` 并重启服务。首次初始化时，也可以显式传入 `init --device YOUR_SCANNED_ADDRESS --enable-controls`。

配置默认映射如下，其他接线必须先改配置：

| 设备 | 插座 | 控制范围 |
| --- | --- | --- |
| 灯 | 1 | 亮度 0–100%；0 为关闭 |
| 排风扇 | 2 | 速度 0–100%；0 为关闭 |
| 循环风扇 | 3 | 0–10 档；0 为关闭 |
| 水泵 | 4 | 有限时长脉冲；默认上限 5 秒、间隔 60 秒 |

调光和调速不会自动开启对应电源插座。先按接线开启电源，再调节设备。5 号不默认分配用途；没有对应配置的插座拒绝写入。

## 本地可视化控制台

保持常驻服务运行，在同一安装环境中执行：

```sh
.venv/bin/growbridge dashboard
```

浏览器中可查看温度、湿度、VPD、CO₂、PPFD、土壤温度和设备回读状态，调节灯和风机、开关电源插座，以及运行有限时长的水泵脉冲。历史曲线提供 1 小时、6 小时、24 小时和 7 天范围，可切换指标、查看记录点，也可将所选时间段的全部原始样本导出为 CSV。操作记录包含网页和 MCP 发起的动作。界面支持窄屏，默认英文，可切换简体中文。

启动命令生成 60 秒内有效、仅能使用一次的连接链接。浏览器取得有效期为 12 小时的 HttpOnly 会话 Cookie，长期 API 令牌不会发送给浏览器 JavaScript。点击“断开控制台”可撤销此会话；服务重启或会话到期后，重新运行启动命令即可。手动控制与 MCP 复用相同的参数校验和回读逻辑；数据过期或安装处于只读模式时，控制按钮不可用。

样本较多时，曲线按整个时间段选取真实样本，显示采集中断，不补造缺失读数。CSV 保留所选时间段的全部原始样本，时间戳使用 UTC；曲线按浏览器本地时区显示。缺失数值显示为横线，设备返回的零值仍显示为零。

界面资源全部由本机提供，无需前端构建或 CDN。服务仍只监听本机回环地址。在树莓派上使用时，先从 Mac 建立 SSH 端口转发：

```sh
ssh -L 8766:127.0.0.1:8766 YOUR_PI_HOST
```

再从另一个终端向树莓派请求临时连接链接：

```sh
ssh -T YOUR_PI_HOST /absolute/path/on/pi/spiderfarmer-growbridge/.venv/bin/growbridge dashboard --no-open
```

在 60 秒内于 Mac 浏览器打开返回的链接，并保持 SSH 转发运行。这不会将控制接口公开到互联网。

## 接入 Codex / MCP 客户端

保持常驻服务运行。在 MCP 客户端里添加一个 stdio 服务：

```toml
[mcp_servers.growbridge]
command = "/absolute/path/spiderfarmer-growbridge/.venv/bin/growbridge"
args = ["mcp"]
```

上面的 `/absolute/path` 是占位符，替换为你的实际安装路径。支持的工具：

| 工具 | 用途 |
| --- | --- |
| `get_health` | 蓝牙、数据新鲜度、协议、插座映射 |
| `get_status` | 环境、插座和设备状态 |
| `get_history` | 最近最多 168 小时的已有记录；默认返回最近 500 个样本 |
| `set_light` | 调整灯亮度 |
| `set_exhaust` | 调整排风扇速度 |
| `set_fan` | 调整风扇档位 |
| `set_outlet` | 开关电源插座；水泵插座直接开启被阻止 |
| `run_pump` | 有限时长运行水泵，并在返回前回读确认关闭 |

所有控制工具都要求 `request_id`（8–100 个字母、数字、下划线或连字符）。每个新动作使用新 ID；重试同一个动作复用 ID，避免重复执行。不同参数不能复用同一个 ID。失败操作需先查看状态，再决定是否创建新动作。

适合的请求示例：“查看当前环境并说明数据多久前更新”“将灯调到 25% 并确认回读”“用同一个请求 ID 重试刚才的查询结果不明的动作”。

## Mac 后台运行

在项目目录执行：

```sh
.venv/bin/python scripts/install_macos.py
```

安装器写入当前用户的 LaunchAgent 并启动服务，不修改设备设置。登录后自动启动；退出登录或电脑休眠时，Mac 无法承担持续采集。长期运行建议迁移到树莓派。日志位于私有数据目录。

停止并移除自动启动项：

```sh
.venv/bin/python scripts/install_macos.py --uninstall
```

## 树莓派部署

在 Raspberry Pi OS Lite 64 位上启用 SSH、连接网络，然后执行：

```sh
sudo apt update
sudo apt install -y python3-venv bluez dbus git
git clone https://github.com/kirinhcl/spiderfarmer-growbridge.git
cd spiderfarmer-growbridge
python3 -m venv .venv
.venv/bin/python -m pip install -c constraints-tested.txt .
.venv/bin/growbridge scan
.venv/bin/growbridge init --device YOUR_PI_SCANNED_ADDRESS
.venv/bin/growbridge serve
```

先完成读取测试，再显式启用控制。Mac 的设备 UUID 不用于 Linux；树莓派上重新扫描并保存自己的地址。

后台启动：

```sh
.venv/bin/python scripts/install_linux.py
systemctl --user status growbridge
```

如果要求退出 SSH 后持续运行并开机启动用户服务，还需由管理员对目标账户开启 linger：`sudo loginctl enable-linger "$USER"`。发行版的 BlueZ/D-Bus 权限策略可能需要为该账户授权，请按实际系统配置；程序不要求以 root 身份运行。

从 Mac 通过 SSH 使用树莓派的 MCP：

```toml
[mcp_servers.growbridge]
command = "ssh"
args = ["-T", "YOUR_PI_HOST", "/absolute/path/on/pi/spiderfarmer-growbridge/.venv/bin/growbridge", "mcp"]
```

先配置 SSH 密钥并确认主机身份。MCP 连接结束不会停止树莓派的常驻服务。服务继续只监听树莓派自己的回环地址，不需要公开 HTTP 端口。

## 数据与控制边界

- 默认保留 30 天传感器样本，可配置 `retention_days`；历史从安装启动后开始。
- 配置、SQLite 和日志存放在用户私有目录。仓库不包含实际地址、账户标识、原始蓝牙抓包或设备配置备份。
- 先读取目标模块完整配置，再修改目标字段；收到成功回复后仍须读取设备状态确认。
- 数据过期、蓝牙断线、协议不支持时拒绝普通控制；重连不会重放历史命令。
- 水泵计时由服务负责，客户端断开不会取消关闭动作。进行中的操作先写入数据库；中断后的水泵操作在重连时优先关闭，不重放开启动作。
- 如果关闭水泵无法确认，服务标记异常、阻止进一步普通控制，并尝试恢复连接后关闭。主机断电、进程被强制终止、蓝牙完全失效时，软件计时无法保证设备按时关闭；无人值守灌溉需要设备端计时或独立硬件保护。
- 本版本只验证了指定设备及协议；不要把某一台设备的成功当作所有固件和硬件的兼容保证。

## 开发验证

```sh
.venv/bin/python -m pip install -c constraints-tested.txt -e '.[dev]'
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/pytest -q
.venv/bin/python -m build
```

详细实测范围见 [VALIDATION.md](VALIDATION.md)。

自动测试使用合成设备，不连接蓝牙、不操作实物。测试覆盖分片与 CRC、版本拒绝、写入回读、参数限制、身份验证、重复请求、水泵超时及恢复。

参考：

- [OpenAI MCP 工具开发文档](https://developers.openai.com/plugins/build/mcp-server)
- [Bleak Linux 后端](https://bleak.readthedocs.io/en/latest/backends/linux.html)
- [原始 Wi-Fi/MQTT 桥接项目](https://github.com/iceboerg00/spiderfarmer-bridge)
- [GGS BLE 协议研究](https://github.com/cr0ssn0tice/Spider-Farmer-GGS-Controller-MQTT)

本项目的驱动和解码器独立实现，协议细节还通过本地设备数据进行了验证。MIT License。
