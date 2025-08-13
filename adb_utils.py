import subprocess
import time
import os
import base64
from datetime import datetime
# import urllib.parse
# import pyperclip
# --- 配置区域 ---
# 雷电模拟器 ADB 路径 (你已经确认这个路径是正确的)
ldplayer_install_dir = r"D:\Program\leidian\LDPlayer9"
adb_path = os.path.join(ldplayer_install_dir, "adb.exe")

# 雷电模拟器 ADB 连接地址 (根据你的 `adb devices` 输出确认是这个)
# D:\Program\leidian\LDPlayer9\adb.exe -s 127.0.0.1:5555 
ld_adb_address = "127.0.0.1:5555" # 这是关键部分

# 构建连接命令和基础 ADB 命令 D:\Program\leidian\LDPlayer9\adb.exe connect 127.0.0.1:5555 
start_command = f"{adb_path} connect {ld_adb_address}"
adb_command = adb_path # 执行具体命令时仍使用 adb.exe 的路径
# ----------------

# 其余部分 (如 sharefold, goalfold, Moniqi 类) 保持不变
sharefold = "/sdcard"
goalfold = "./screens"
os.makedirs(goalfold, exist_ok=True)

class Moniqi:
    def __init__(self, adb_path=adb_path, start_command=start_command, adb_command=adb_command, device_address=ld_adb_address):
        self.adb_path = adb_path
        self.adb_command = adb_command
        self.device_address = device_address # 保存设备地址
        print(f"尝试连接模拟器: {start_command}")
        stdout, stderr = self.run_adb_command(start_command)
        print(f"连接输出: {stdout.decode('utf-8').strip()}")
        self.width = 0              # 屏幕宽度
        self.height = 0             # 屏幕高度
        self.get_resolution()
        if stderr:
             print(f"连接错误: {stderr.decode('utf-8').strip()}")
        self.install_ADBKeyBoard()

    def run_adb_command(self, command, timeout=5):
        """
        执行 ADB 命令，默认 5 秒超时
        :param command: 字符串或列表均可（shell=True 时传字符串）
        :param timeout: 秒
        :return: (stdout_bytes, stderr_bytes)
        """
        try:
            process = subprocess.Popen(command, shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(timeout=timeout)
            return stdout, stderr
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()  # 回收僵尸进程
            print("ADB 命令执行超时，已强制结束")
            return b'', b'Timeout'
        except Exception as e:
            print(f"执行 ADB 命令 '{command}' 时出错: {e}")
        return b'', str(e).encode('utf-8')

    def get_screenshot(self):
        try:
            print("正在截图...")
            # 在命令中指定设备地址
            stdout_cap, stderr_cap = self.run_adb_command(f"{self.adb_command} -s {self.device_address} shell screencap -p {sharefold}/screen.png")
            if stderr_cap:
                print(f"截图命令错误: {stderr_cap.decode('utf-8').strip()}")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 构造新文件名（注意保留.png扩展名）
            new_filename = f"screen_{timestamp}.png"

            local_file_path = os.path.join(goalfold, new_filename)  # 使用新文件名

            # 在命令中指定设备地址
            stdout_pull, stderr_pull = self.run_adb_command(f"{self.adb_command} -s {self.device_address} pull {sharefold}/screen.png {local_file_path}")
            if stderr_pull:
                print(f"拉取截图错误: {stderr_pull.decode('utf-8').strip()}")
                return None
            else:
                print(f"截图已保存到: {local_file_path}")
                return local_file_path

        except Exception as e:
            print(f"截图失败：{str(e)}")
            return None

    def get_resolution(self):
        """获取模拟器分辨率并保存到类属性"""
        # 执行获取分辨率的ADB命令
        resolution_cmd = f"{self.adb_command} -s {self.device_address} shell wm size"
        print("正在获取模拟器分辨率...")
        stdout, stderr = self.run_adb_command(resolution_cmd)
        
        if stderr:
            print(f"获取分辨率错误: {stderr.decode('utf-8').strip()}")
            return False
        
        # 解析分辨率输出
        output = stdout.decode('utf-8').strip()
        if "Physical size:" in output:
            # 提取分辨率数值 (格式: Physical size: 1080x1920)
            res_str = output.split(":")[1].strip()
            self.width, self.height = map(int, res_str.split('x'))
        elif "Override size:" in output:
            # 处理修改后的分辨率
            res_str = output.split(":")[1].strip()
            self.width, self.height = map(int, res_str.split('x'))
        else:
            # 尝试备选方法
            alt_cmd = f"{self.adb_command} -s {self.device_address} shell dumpsys window displays"
            stdout, stderr = self.run_adb_command(alt_cmd)
            output = stdout.decode('utf-8').strip()
            
            # 在输出中查找分辨率
            for line in output.splitlines():
                if 'cur=' in line:
                    res_str = line.split('cur=')[1].split()[0]
                    self.width, self.height = map(int, res_str.split('x'))
                    break
            else:
                print("无法解析分辨率输出:", output)
                return False
        
        print(f"获取分辨率成功: {self.width}x{self.height}")
        return True
    
    def click(self, coordinates):
        # 在命令中指定设备地址
        click_command = f"{self.adb_command} -s {self.device_address} shell input tap {coordinates[0]} {coordinates[1]}"
        print(f"点击坐标: {coordinates[0]}, {coordinates[1]}")
        stdout, stderr = self.run_adb_command(click_command)
        if stderr:
             print(f"点击命令错误: {stderr.decode('utf-8').strip()}")
        time.sleep(0.5)

    def click_long(self, coordinates, duration_ms=1000):
        # 在命令中指定设备地址
        click_command = f"{self.adb_command} -s {self.device_address} shell input swipe {coordinates[0]} {coordinates[1]} {coordinates[0]} {coordinates[1]} {int(duration_ms)}"
        print(f"长按坐标: {coordinates[0]}, {coordinates[1]} 持续 {int(duration_ms)} 毫秒")
        stdout, stderr = self.run_adb_command(click_command)
        if stderr:
             print(f"长按命令错误: {stderr.decode('utf-8').strip()}")
        time.sleep(0.5)

    def install_apk(self, apk_path_on_pc):
        """
        在模拟器上安装 APK 文件。
        :param apk_path_on_pc: APK 文件在电脑上的完整路径 (例如: r'C:\path\to\app.apk')
        """
        # 1. 检查文件是否存在
        if not os.path.exists(apk_path_on_pc):
            print(f"找不到文件 '{apk_path_on_pc}'")
            return False

        # 2. 构建 ADB 安装命令
        # -r 参数表示如果应用已存在则替换
        install_command = f'{self.adb_command} -s {self.device_address} install -r "{apk_path_on_pc}"'
        
        print(f"正在安装: {apk_path_on_pc}")

        # 3. 执行命令
        stdout, stderr = self.run_adb_command(install_command)

        # 4. 检查结果 (简化判断)
        output_str = stdout.decode('utf-8', errors='replace').strip()
        error_str = stderr.decode('utf-8', errors='replace').strip()
        
        if output_str:
            print(f"  ADB 输出: {output_str}")
        if error_str:
            print(f"  ADB 错误: {error_str}")

        # 5. 判断成功与否 (非常基础的判断)
        if "Success" in output_str:
            print("安装成功。")
            return True
        else:
            print("安装可能失败，请检查输出。")
            return False
    
    def uninstall_app(self, package_name="com.android.adbkeyboard"):
        """
        在模拟器上卸载指定包名的应用。
        :param package_name: 要卸载的应用包名 (例如: 'com.tencent.mm' for WeChat)
        """
        # 1. 构建 ADB 卸载命令
        uninstall_command = f'{self.adb_command} -s {self.device_address} uninstall "{package_name}"'
        
        print(f"正在卸载应用: {package_name}")

        # 2. 执行命令
        stdout, stderr = self.run_adb_command(uninstall_command)

        # 3. 检查结果 (简化判断)
        output_str = stdout.decode('utf-8', errors='replace').strip()
        error_str = stderr.decode('utf-8', errors='replace').strip()
        
        if output_str:
            print(f"  ADB 输出: {output_str}")
        if error_str:
            print(f"  ADB 错误: {error_str}")

        # 4. 判断成功与否 (非常基础的判断)
        # adb uninstall 成功通常输出 "Success", 失败可能输出 "Failure" 或其他信息
        if "Success" in output_str:
            print(f"应用 '{package_name}' 卸载成功。")
            return True
        else:
            # 注意：如果应用本身不存在，命令也可能执行成功但输出 "Failure [DELETE_FAILED_INTERNAL_ERROR]"
            # 或者 "Failure [not installed for user 0]"
            print(f"应用 '{package_name}' 卸载可能失败或应用未安装，请检查输出。")
            return False

    def launch_app(self, package_name):
        """
        启动模拟器中已安装的应用。
        :param package_name: 应用的包名 (e.g., 'com.tencent.mm' for WeChat)
        """
        launch_command = f"{self.adb_command} -s {self.device_address} shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
        # 或者使用 am start 命令，有时更精确：
        # launch_command = f"{self.adb_command} -s {self.device_address} shell am start -n {package_name}/.{activity_name}"
        # 如果你知道具体的 Activity 名，可以使用 am start -n packageName/.ActivityName

        print(f"尝试启动应用: {package_name}")
        stdout, stderr = self.run_adb_command(launch_command)
        output_str = stdout.decode('utf-8').strip()
        error_str = stderr.decode('utf-8').strip()

        # 检查输出和错误
        if error_str:
            # 注意：monkey 命令即使成功也可能有 stderr 输出，需要具体判断
            # 一个简单的判断：如果 stderr 包含 'monkey aborted' 或 'Error'，则认为失败
            if 'monkey aborted' in error_str.lower() or 'error' in error_str.lower():
                 print(f"启动应用错误: {error_str}")
                 return False
        # 如果没有明显错误，或者 stderr 是类似 'Events injected: 1'，则认为成功
        print(f"启动命令输出: {output_str}")
        print(f"应用启动命令已发送。")
        time.sleep(0.5)
        return True # 假设命令发送成功即为启动（实际启动可能需要时间）

    def safe_launch_app(self, package_name, max_retry=2):
        """
        可靠启动应用：
        - 先尝试启动；
        - 若失败 → 强制关闭 → 回桌面 → 再次启动；
        - 最多重试 max_retry 次。
        :return: True 成功；False 依然失败
        """
        cur_pkg, _ = self.get_current_activity()
        if cur_pkg == package_name:
            return True

        attempt = 0
        while attempt <= max_retry:
            attempt += 1
            print(f"【第 {attempt} 次】尝试启动 {package_name}")

            # 1) 启动
            launch_command = f"{self.adb_command} -s {self.device_address} shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
            stdout, stderr = self.run_adb_command(launch_command)
            time.sleep(6)
            if not (stderr and b"Error" in stderr):
                # 无报错，再确认是否在前台
                cur_pkg, _ = self.get_current_activity()

                if cur_pkg == package_name:
                    print(f"{package_name} 成功启动并位于前台")
                    return True
                time.sleep(1)

            # 2) 失败处理：杀进程 + 回桌面
            print("启动未成功，准备清理重试…")
            self.force_stop_app(package_name)
            self.press_back_until_home()

        print("已重试多次仍无法启动，放弃")
        return False

    def force_stop_app(self, package_name):
        """
        强制关闭应用（相当于滑掉最近任务 + force-stop）
        """
        cmd = [self.adb_command, "-s", self.device_address,
            "shell", "am", "force-stop", package_name]
        stdout, stderr = self.run_adb_command(cmd)
        if stderr and b"Error" in stderr:
            print(f"关闭应用失败: {stderr.decode().strip()}")
            return False
        print(f"已强制关闭 {package_name}")
        return True

    def go_home(self):
        """
        把模拟器/真机一键回到主界面。
        :param max_back: 最多按几次 BACK
        :param delay: 每次检查间隔
        :return: True 表示已成功回到桌面
        """
        # 2. 直接发 HOME 键
        home_cmd = [self.adb_command, "-s", self.device_address,
                    "shell", "input", "keyevent", "KEYCODE_HOME"]
        self.run_adb_command(home_cmd)
        time.sleep(1)

        # 3. 确认是否已在桌面
        if self.is_on_home_screen():
            print("已一键回到主界面")
            return True
        
    def press_back(self):
        """
        模拟按下设备的返回键。
        """
        # Android 返回键的键码是 KEYCODE_BACK = 4
        back_command = f"{self.adb_command} -s {self.device_address} shell input keyevent 4"
        print("模拟按下返回键")
        stdout, stderr = self.run_adb_command(back_command)
        if stderr:
            print(f"返回键命令可能出错: {stderr.decode('utf-8').strip()}")
        # 可以添加短暂延迟，模拟按键间隔
        time.sleep(0.5)

    def install_ADBKeyBoard(self, apk_path="ADBKeyboard.apk"):
        """
        安装并激活 ADBKeyboard。
        首先检查是否已安装，如果未安装则进行安装。
        """
        package_name = "com.android.adbkeyboard"
        
        # 1. 检查 ADBKeyboard 是否已安装
        check_command = f"{self.adb_command} -s {self.device_address} shell pm list packages {package_name}"
        
        print(f"检查是否已安装 {package_name}...")
        try:
            # 使用 subprocess.check_output 以便更容易获取标准输出
            # 注意：这里直接调用 subprocess，而不是 self.run_adb_command，
            # 因为我们可能需要检查输出内容，而 self.run_adb_command 有固定的 sleep 和打印逻辑。
            # 如果 self.run_adb_command 没有返回 stdout/stderr，你需要调整。
            # 假设 self.run_adb_command 返回 (stdout, stderr)
            stdout, stderr = self.run_adb_command(check_command)
            
            # 解码输出 (假设 run_adb_command 返回的是字节)
            output_str = stdout.decode('utf-8').strip() if isinstance(stdout, bytes) else str(stdout).strip()
            error_str = stderr.decode('utf-8').strip() if isinstance(stderr, bytes) else str(stderr).strip()
            
            if error_str:
                print(f"  检查命令出错: {error_str}")
                # 可以选择抛出异常或继续尝试安装
                # raise Exception(f"检查应用失败: {error_str}")

            # 2. 判断是否已安装
            # 如果已安装，输出通常类似: package:com.android.adbkeyboard
            # 如果未安装，输出通常是空字符串
            if package_name in output_str:
                print(f"  {package_name} 已安装。")
                is_installed = True
            else:
                print(f"  {package_name} 未安装。")
                is_installed = False
                
        except subprocess.CalledProcessError as e:
            print(f"  执行检查命令时出错: {e}")
            is_installed = False # 假设出错则未安装，需要重新安装
        except Exception as e:
            print(f"  检查安装状态时发生未知错误: {e}")
            is_installed = False

        # 3. 如果未安装，则执行安装
        if not is_installed:
            print(f"开始安装 {package_name}...")
            install_success = self.install_apk(apk_path) # 假设 install_apk 返回 True/False
            if not install_success:
                print(f"安装 {package_name} 失败。")
                return False # 或抛出异常
            print(f"{package_name} 安装成功。")
        else:
            print("无需安装，跳过安装步骤。")

        # 4. 激活 ADB Keyboard (无论是否刚安装，都尝试激活以确保启用)
        print("正在激活 ADB Keyboard...")
        
        # 先启用 (enable) IME
        enable_command = f"{self.adb_command} -s {self.device_address} shell ime enable {package_name}/.AdbIME"
        stdout_e, stderr_e = self.run_adb_command(enable_command)
        # 可以检查 enable_command 的输出，但通常失败也不致命
        
        # 再设置 (set) 为默认 IME
        activate_command = f"{self.adb_command} -s {self.device_address} shell ime set {package_name}/.AdbIME"
        stdout_s, stderr_s = self.run_adb_command(activate_command)
        
        # 检查激活结果 (可选，但推荐)
        activate_output = stdout_s.decode('utf-8').strip() if isinstance(stdout_s, bytes) else str(stdout_s).strip()
        activate_error = stderr_s.decode('utf-8').strip() if isinstance(stderr_s, bytes) else str(stderr_s).strip()
        
        if activate_error:
            print(f"  激活命令出错: {activate_error}")
        # 成功时，ime set 命令通常没有 stdout 输出，或者输出 "Input method com.android.adbkeyboard/.AdbIME selected"
        # 失败时 stderr 会有信息，如 "Unknown input method com.android.adbkeyboard/.AdbIME"
        
        if "Unknown input method" in activate_error or "not found" in activate_error:
            print(f"  激活 {package_name} 失败，请检查包名和类名是否正确。")
            return False
        else:
            print(f"  {package_name} 激活命令已发送。请检查设备确认是否激活成功。")

        print("ADB Keyboard 安装并激活流程完成。")
        return True

    def input_text(self,text_to_paste,positon=None, chunk_size=50):
        if positon:
            self.click(positon)
        # activate_command = f"{self.adb_command} -s {self.device_address} shell ime set com.android.adbkeyboard/.AdbIME"
        # deactivate_command = f"{self.adb_command} -s {self.device_address} shell ime enable com.android.adbkeyboard/.AdbIME"

        # stdout, stderr = self.run_adb_command(deactivate_command)
        # stdout, stderr = self.run_adb_command(activate_command)
    
        # pyperclip.copy(message)
        # input_command = f"{self.adb_command} -s {self.device_address} shell input text {message}"

        # charsb64 = str(base64.b64encode(message.encode("utf-8")))[1:]
        # print(charsb64)
        # os.system("D:\\Program\\leidian\\LDPlayer9\\adb.exe -s 127.0.0.1:5555 shell am broadcast -a ADB_INPUT_B64 --es msg %s" %charsb64)

        clear_input = f"{self.adb_command} -s {self.device_address} shell am broadcast -a ADB_CLEAR_TEXT"
        stdout, stderr = self.run_adb_command(clear_input)
        time.sleep(0.2)

        if not text_to_paste:
            print("没有文本需要粘贴。")
            return
        # 1. 处理换行符 (\n)
        lines = text_to_paste.split('\n')

        for line_index, line in enumerate(lines):
            # 5. 处理制表符 (\t) - 在每一行内
            segments = line.split('\t')
            for segment_index, segment in enumerate(segments):
                
                # 6. 将段落进一步按 chunk_size 分块
                chunks = [segment[i:i + chunk_size] for i in range(0, len(segment), chunk_size)] if segment else ['']

                for chunk_index, chunk in enumerate(chunks):
                    if not chunk: # 跳过空块
                        continue

                    # 7. 对块进行 Base64 编码 
                    try:
                        text_bytes = chunk.encode('utf-8')
                        base64_bytes = base64.b64encode(text_bytes)
                        # Base64 字节串解码为 ASCII 字符串，用于命令行参数
                        base64_string = base64_bytes.decode('ascii') 
                    except Exception as e:
                        print(f"警告：对文本块进行 Base64 编码时出错 '{chunk}': {e}")
                        continue # 跳过这个块

                    # 8. 构建并执行 ADB 命令 
                    # 使用列表形式传递参数更安全，避免 shell 转义问题
                    input_command_list = [
                        self.adb_command,
                        "-s", self.device_address,
                        "shell", "am", "broadcast",
                        "-a", "ADB_INPUT_B64",
                        "--es", "msg", base64_string
                    ]
                    
                    print(f"【正在输入文本块】 (长度: {len(chunk)}): {chunk[:30]}{'...' if len(chunk) > 30 else ''}")
                    print(f"  Base64 Payload: {base64_string}") # 可选：打印 Base64 内容用于调试

                    # 9. 执行命令 (推荐使用 subprocess.run)
                    try:
                        # 使用列表形式，并捕获输出
                        result = subprocess.run(
                            input_command_list,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=False, # 以 bytes 处理输出
                            check=True, # 如果返回码非0，抛出 CalledProcessError
                            timeout=30 # 设置超时时间
                        )
                        stdout_str = result.stdout.decode('utf-8', errors='replace').strip()
                        stderr_str = result.stderr.decode('utf-8', errors='replace').strip()
                        
                        # 10. 检查命令执行结果
                        # 可以根据服务返回判断成功与否，例如检查 stdout 是否包含特定成功信息
                        # 这里只打印输出，不做严格判断
                        if stdout_str:
                            print(f"  ADB stdout: {stdout_str}")
                        if stderr_str:
                            # am broadcast 即使成功也可能有 stderr 输出
                            # 通常只在真正出错时才打印 (例如包含 Error, Exception 等)
                            if "Error" in stderr_str or "Exception" in stderr_str:
                                print(f"  ADB stderr (可能错误): {stderr_str}")
                            else:
                                print(f"  ADB stderr (信息/警告): {stderr_str}")

                    except subprocess.CalledProcessError as e:
                        print(f"  ADB 命令执行失败 (返回码 {e.returncode})")
                        if e.stdout:
                            print(f"  ADB stdout: {e.stdout.decode('utf-8', errors='replace')}")
                        if e.stderr:
                            print(f"  ADB stderr: {e.stderr.decode('utf-8', errors='replace')}")
                    except subprocess.TimeoutExpired:
                        print(f"  ADB 命令执行超时 (>{30}s)")
                    except Exception as e:
                        print(f"  执行 ADB 命令时发生未知错误: {e}")

                    # 11. 块间延迟，确保输入顺序和稳定性
                    time.sleep(0.2) # 可根据目标应用响应速度调整

                # 12. 段落间处理 (Tab 键)
                if segment_index < len(segments) - 1:
                    print("模拟按下 Tab 键")
                    tab_cmd = f"{self.adb_command} -s {self.device_address} shell input keyevent 61"
                    self.run_adb_command(tab_cmd)
                    time.sleep(0.2) # Tab 后短暂延迟

            # 13. 行间处理 (Enter 键)
            if line_index < len(lines) - 1:
                print("模拟按下 Enter 键 (换行)")
                self.press_enter() # 确保你的类中有这个方法
                time.sleep(0.3) # 换行后稍微长一点的延迟

        print("文本输入完成 (使用 Base64)。")
    
    def press_enter(self):
        """
        模拟按下设备的 Enter (回车) 键。
        """
        # Android Enter 键的键码是 KEYCODE_ENTER = 66
        enter_command = f"{self.adb_command} -s {self.device_address} shell input keyevent 66"
        print("按下 Enter 键")
        stdout, stderr = self.run_adb_command(enter_command)
        if stderr:
            print(f"Enter 键命令可能出错: {stderr.decode('utf-8').strip()}")
        # 可以添加短暂延迟，模拟按键间隔
        time.sleep(0.5)

    def get_current_activity(self):
        """
        获取当前前台 Activity 的包名和 Activity 名。
        返回格式: (package_name, activity_name) 或 (None, None) 如果失败。
        """
        # dumpsys window windows 命令输出当前窗口信息
        # grep -E 'mCurrentFocus|mFocusedApp' 用于过滤出焦点窗口信息
        # 在 Windows 上，grep 可能不可用，但 findstr 可以替代
        # awk '{print $NF}' 用于提取最后一列，在 Windows 上可以用 for /f 或其他方式处理
        # 更简单的方法是直接解析 dumpsys activity 的 mResumedActivity (较新版本) 或 mFocusedActivity (较旧版本)
        # 最通用的方法是 dumpsys window windows 并解析 mCurrentFocus
        
        # 使用 dumpsys window windows | findstr mCurrentFocus
        # 输出示例: mCurrentFocus=Window{cf0012a u0 com.android.launcher3/com.android.launcher3.Launcher}
        # 或者: mCurrentFocus=Window{... u0 com.tencent.mm/com.tencent.mm.ui.LauncherUI}
        
        dump_command = f"{self.adb_command} -s {self.device_address} shell dumpsys window windows"
        print("正在获取当前 Activity...")
        stdout, stderr = self.run_adb_command(dump_command)
        
        if stderr:
            print(f"获取 Activity 信息时出错: {stderr.decode('utf-8').strip()}")
            return None, None
            
        output_lines = stdout.decode('utf-8').strip().split('\n')
        # 查找包含 mCurrentFocus 的行
        for line in output_lines:
            if 'mCurrentFocus' in line and '=' in line:
                # 提取类似 com.android.launcher3/com.android.launcher3.Launcher 的部分
                # line 可能是: mCurrentFocus=Window{...} com.android.launcher3/com.android.launcher3.Launcher
                # 或者: mCurrentFocus=Window{... u0 com.android.launcher3/com.android.launcher3.Launcher}
                # 我们需要提取最后的包名/Activity名
                parts = line.split()
                for part in reversed(parts): # 从后往前找，更容易找到
                    if '/' in part and not part.startswith('Window{'):
                        try:
                            pkg_act = part.strip()
                            if pkg_act.endswith('}'): # 去掉可能的结尾大括号
                                pkg_act = pkg_act[:-1]
                            pkg, act = pkg_act.split('/', 1)
                            # act 可能是 .Launcher 或 com.android.launcher3.Launcher
                            # 如果是 .Launcher，通常前面会加上 pkg
                            if act.startswith('.'):
                                full_act = pkg + act
                            else:
                                full_act = act
                            print(f"当前 Activity: 包名={pkg}, Activity={full_act}")
                            return pkg, full_act
                        except ValueError:
                            # 如果分割失败，继续查找下一部分
                            continue
        print("未能解析出当前 Activity 信息。")
        self.get_resolution()
        # 尝试关闭弹出的错误
        self.click((int(self.width / 2),int(self.height / 2)))
        return None, None

    def is_on_home_screen(self, launcher_package="com.android.launcher3", launcher_activity_suffix=".Launcher"):
        """
        检查当前是否在主界面。
        注意：不同的模拟器或系统，Launcher 的包名和 Activity 名可能不同。
        你需要根据实际情况调整 launcher_package 和 launcher_activity_suffix。
        常见的组合：
        - 雷电模拟器/大多数原生Android: launcher_package="com.android.launcher3", launcher_activity_suffix=".Launcher"
        - 某些定制系统: launcher_package="com.miui.home", launcher_activity_suffix=".Launcher"
        - Google Pixel: launcher_package="com.google.android.apps.nexuslauncher", launcher_activity_suffix=".NexusLauncherActivity"
        
        :param launcher_package: 主界面应用的包名前缀
        :param launcher_activity_suffix: 主界面 Activity 名的后缀 (相对于包名)
        :return: True if on home screen, False otherwise
        """
        current_pkg, current_act = self.get_current_activity()
        if current_pkg is None or current_act is None:
            
            print("无法获取当前 Activity 信息，无法判断是否在主界面。")
            return False # 或者抛出异常，取决于你的需求

        # 检查包名是否匹配，并且 Activity 名是否以指定后缀结尾
        # 这种方式比较灵活，可以匹配 .Launcher 或完整的 com.android.launcher3.Launcher
        if current_pkg == launcher_package and current_act.endswith(launcher_activity_suffix):
             print(f"检测到已在主界面: {current_pkg}/{current_act}")
             return True
        else:
             print(f"当前不在主界面。当前 Activity: {current_pkg}/{current_act}")
             return False

    def press_back_until_home(self, max_attempts=10, delay_between_presses=0.5, launcher_package="com.android.launcher3", launcher_activity_suffix=".Launcher"):
        """
        循环按返回键，直到检测到主界面或达到最大尝试次数。
        :param max_attempts: 最大按返回键次数
        :param delay_between_presses: 每次按返回键之间的延迟（秒）
        :param launcher_package: 主界面应用的包名前缀
        :param launcher_activity_suffix: 主界面 Activity 名的后缀
        :return: True if successfully navigated to home, False otherwise
        """

        for attempt in range(max_attempts):
            print(f"尝试返回主界面 (第 {attempt + 1}/{max_attempts} 次)")
            if self.is_on_home_screen(launcher_package, launcher_activity_suffix):
                print("已处于主界面。")
                return True
            
            self.press_back()
            time.sleep(delay_between_presses) # 等待界面切换
        
        # 循环结束后再次检查
        if self.is_on_home_screen(launcher_package, launcher_activity_suffix):
             print("在最后一次检查后确认已处于主界面。")
             return True
        else:
             print(f"经过 {max_attempts} 次尝试后仍未返回主界面。")
             return False
        

if __name__ == "__main__":
    # 确保 ADB 路径正确
    if not os.path.exists(adb_path):
        print(f"错误：找不到 ADB 可执行文件 {adb_path}")
        exit(1)

    # 实例化时传入设备地址
    mnq = Moniqi()
    print(mnq.width," ",mnq.height)
    mnq.safe_launch_app("com.tencent.mm")
    mnq.go_home()

    # --- 示例用法 ---
    # 1. 截图
    # screenshot_path = mnq.get_screenshot()
    # success = mnq.launch_app("com.tencent.mm")
    # if success:
    #     print("启动微信命令已发送")
    # else:
    #     print("启动微信失败")

    # mnq.press_back_until_home()
    # mnq.paste_text()
    # mnq.click((145,1565))
    # mnq.input_text("""小八""")
    # mnq.click_long((616,1563),1000)
    # mnq.input_text("hello 1",(616,1563))
    # mnq.install_apk("ADBKeyboard.apk")
    # mnq.force_stop_app("com.tencent.mm")