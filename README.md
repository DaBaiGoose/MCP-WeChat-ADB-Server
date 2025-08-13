# MCP WeChat ADB Server

一个基于 ADB 的微信自动化 MCP 服务器，为 AI 助手提供微信消息发送和截图功能，可以实现 AI 自动对多个联系人微信回复不同的个性化消息，满足商务生活需求。适配雷电模拟器（LDPlayer 9），通过 MCP 协议暴露工具接口。MCP入口文件是 main.py

## 🚀 功能特性

- **微信消息发送**：通过自然语言指令发送微信消息
- **智能截图**：自动截图并保存到本地
- **MCP 协议支持**：与 Cursor、Claude Desktop 等支持 MCP 的 AI 助手无缝集成
- **雷电模拟器适配**：专为 LDPlayer 9 优化，支持中文输入

## 🛠️ 可用工具

- `send_wechat_message(name, message)` - 发送微信消息
- `screen_save()` - 截图保存

### 环境要求

- Windows 10/11（已测试）
- Python >= 3.13
- 雷电模拟器 LDPlayer 9（已安装并登录微信）
- 已启用 ADB 调试（在模拟器 诊断信息 中可查看 ADB 端口）

### 完整安装配置流程

#### 第一步：安装雷电模拟器
1. 下载并安装雷电模拟器，测试使用的是 9.1.58(64) 官网最新版本，安装路径中不要有空格，并将路径填入 main.py 的 ldplayer_dir 变量中
2. 设置模拟器分辨率为 1600x900
3. 在模拟器中安装微信，模拟器里直接搜索安装的就行，测试用的是 Version 8.0.58
4. 登录微信账号并手动设置好权限
5. 打开微信试用一下，确保不会弹出风险提示，能正常运行（一般微信都没问题）
6. **查看 ADB 端口**：在命令行中执行以下命令查看可用的设备端口：
   ```powershell
   D:\Program\leidian\LDPlayer9\adb.exe devices
   ```
   查看结果示例：
   ```
   List of devices attached
   127.0.0.1:5555  device
   emulator-5554   device
   ```
   选择第一个端口（如 `127.0.0.1:5555`）填入 main.py 的 `DEVICE` 变量

#### 第二步：创建 Python 环境
可以使用 conda 或者 uv 创建环境，推荐使用 Python 3.13：

```powershell
# 使用 conda
conda create -n mcp-wechat python=3.13
conda activate mcp-wechat

# 或使用 uv
uv venv
uv pip install "mcp[cli]"
```

只需要安装 `pip install "mcp[cli]"` 库即可。

#### 第三步：配置和运行
1. 将模拟器目录位置填入 `main.py` 的 `ldplayer_dir` 变量
2. 将第一步查看到的 ADB 设备端口填入 `main.py` 的 `DEVICE` 变量（如 `"127.0.0.1:5555"`）
3. 默认启用 SSE 模式运行，用当前环境下的 Python 运行 `main.py`：
   ```powershell
   python main.py
   ```
运行后会启动 MCP SSE 服务并注册以下工具：

- `send_wechat_message(name: str, message: str) -> str`
  - 功能：给指定联系人发送消息
  - 依赖：微信已登录、ADB 输入法已激活

- `screen_save() -> str`
  - 功能：在模拟器上截图并保存到 `screens/` 目录
    
#### 第四步：配置 Cursor MCP
1. 在 Cursor 中设置：Tools and Integrations → Add Custom MCP
2. 在 `mcp.json` 文件中写入：
   ```json
   {
     "mcpServers": {
       "plus": {
         "url": "http://127.0.0.1:8000/sse"
       }
     }
   }
   ```
3. 开启这个 MCP Tools，显示小绿点以后即可正常在Cursor的 Agent 对话框里对话了

### 重要注意事项

- **ADBKeyboard.apk 文件**：目录下的 `ADBKeyboard.apk` 文件不能少，这个是雷电模拟器的 ADB 输入中文需要的插件
- **截图功能**：截图功能会将截图保存在 `screens` 文件夹下
- **ADB 端口查看**：使用 `{模拟器路径}\adb.exe devices` 命令查看可用的设备端口

### 目录结构

- `main.py`：MCP 服务入口，注册工具并运行 `FastMCP`（SSE 传输）。
- `wechat_example.py`：封装微信相关操作（进入对话、输入、发送等）。
- `adb_utils.py`：ADB 基础能力（连接、点击、输入法激活、截图、分辨率、Activity 检测等）。
- `ADBKeyboard.apk`：通过广播输入文本所需的输入法 APK（首次会自动安装并激活）。
- `screens/`：截图输出目录（自动创建）。

### 使用示例

配置好 MCP 后，您可以在 Cursor 的 Agent 中直接使用以下功能：

#### 发送微信消息
```
给 AAA 说我感冒了，写一个请假条发给他
```

#### 截图功能
```
帮我截图
```

#### 组合使用示例
```
给 AAA、 BBB 发信息说我今晚不回家，分别截图
```
[![演示视频]()](https://github.com/user-attachments/assets/0ec32420-ddcc-4d1e-9482-905de7c3cf8f)
https://github.com/user-attachments/assets/0ec32420-ddcc-4d1e-9482-905de7c3cf8f

#### 重要提醒：联系人名称
⚠️ **AAA、BBB 需要是微信中联系人或群聊的名字/备注中能搜索到的唯一名称，这样才能根据名字准确找到指定对方并进入对话**

- 可以使用微信**备注** 给需要的人和群聊特殊的备注，以便搜索

### 后续计划

🚀 本项目已实现将 adb 操作完美接入MCP，让AI可以自由操作模拟器，随着多模态大模型的发展进步，后续可以将截图输入给具有图像理解和定位能力的大模型（例如GLM-4.5V），让 AI Agent 通过 MCP 能完全自动化地边看边操作每一步，完成任何手机上的任务。

### 常见问题排查

路径分隔符在 Windows 下建议使用原始字符串或双反斜杠，例如：

```python
ldplayer_install_dir = r"D:\\Program\\leidian\\LDPlayer9"
```

首次运行会自动检查并安装/激活 `ADBKeyboard.apk`，若自动激活失败，可手动执行例如：

```powershell
"D:\Program\leidian\LDPlayer9\adb.exe" -s 127.0.0.1:5555 install -r ADBKeyboard.apk
"D:\Program\leidian\LDPlayer9\adb.exe" -s 127.0.0.1:5555 shell ime enable com.android.adbkeyboard/.AdbIME
"D:\Program\leidian\LDPlayer9\adb.exe" -s 127.0.0.1:5555 shell ime set com.android.adbkeyboard/.AdbIME
```

- 连接失败或超时：
  - 确认 `adb.exe` 路径是否正确，能否执行：
    ```powershell
    "D:\Program\leidian\LDPlayer9\adb.exe" devices  
    "D:\Program\leidian\LDPlayer9\adb.exe" connect 127.0.0.1:5555
    "D:\Program\leidian\LDPlayer9\adb.exe" -s 127.0.0.1:5555 shell screencap -p /sdcard/screen.png
    ```
  - 确认模拟器中 ADB 端口与 `ld_adb_address` 一致。
  - 确认模拟器中 ADB 端口与 `DEVICE` 变量一致。
  - 如果设备列表为空，请检查模拟器是否正常运行，ADB 调试是否已启用。


### 许可

本项目采用 [MIT 许可证](LICENSE)。

**注意事项：**
- 本项目仅用于学习和研究目的
- 使用本工具时请遵守相关法律法规和微信用户协议
- 请勿用于商业用途或恶意用途
- `pyproject.toml` 已通过打包排除规则避免将 `runtime/`、`screens/` 等内容发布到分发包



