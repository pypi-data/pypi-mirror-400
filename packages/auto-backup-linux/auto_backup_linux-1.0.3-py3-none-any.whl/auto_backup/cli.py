# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import platform
import getpass
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from .config import BackupConfig
from .manager import BackupManager


def is_server():
    """检查是否在服务器环境中运行"""
    return not platform.system().lower() == 'windows'


def backup_server(backup_manager, source, target):
    """备份服务器"""
    backup_dir = backup_manager.backup_linux_files(source, target)
    if backup_dir:
        backup_path = backup_manager.zip_backup_folder(
            backup_dir, 
            str(target) + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        if backup_path:
            if backup_manager.upload_backup(backup_path):
                logging.critical("☑️ 服务器备份完成")
            else:
                logging.error("❌ 服务器备份失败")


def backup_and_upload_logs(backup_manager):
    log_file = backup_manager.config.LOG_FILE
    
    try:
        if not os.path.exists(log_file):
            if backup_manager.config.DEBUG_MODE:
                logging.debug(f"备份日志文件不存在，跳过: {log_file}")
            return

        # 刷新日志缓冲区，确保所有日志都已写入文件
        for handler in logging.getLogger().handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
        
        # 等待一小段时间，确保文件系统同步
        time.sleep(0.5)

        file_size = os.path.getsize(log_file)
        if file_size == 0:
            if backup_manager.config.DEBUG_MODE:
                logging.debug(f"备份日志文件为空，跳过: {log_file}")
            return

        temp_dir = Path.home() / ".dev/Backup/temp_backup_logs"
        if not backup_manager._ensure_directory(str(temp_dir)):
            logging.error("❌ 无法创建临时日志目录")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_log_{timestamp}.txt"
        backup_path = temp_dir / backup_name

        try:
            # 读取并验证日志内容
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as src:
                log_content = src.read()
            
            if not log_content or not log_content.strip():
                logging.warning("⚠️ 日志内容为空，跳过上传")
                return
            
            # 写入备份文件
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(log_content)
            
            # 验证备份文件是否创建成功
            if not os.path.exists(str(backup_path)) or os.path.getsize(str(backup_path)) == 0:
                logging.error("❌ 备份日志文件创建失败或为空")
                return
            
            if backup_manager.config.DEBUG_MODE:
                logging.info(f"📄 已复制备份日志到临时目录 ({os.path.getsize(str(backup_path)) / 1024:.2f}KB)")
            
            # 上传日志文件
            logging.info(f"📤 开始上传备份日志文件 ({os.path.getsize(str(backup_path)) / 1024:.2f}KB)...")
            if backup_manager.upload_file(str(backup_path)):
                try:
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write(f"=== 📝 备份日志已于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 上传 ===\n")
                    logging.info("✅ 备份日志上传成功并已清空")
                except Exception as e:
                    logging.error(f"❌ 备份日志更新失败: {e}")
            else:
                logging.error("❌ 备份日志上传失败")

        except (OSError, IOError, PermissionError) as e:
            logging.error(f"❌ 复制或读取日志文件失败: {e}")
        except Exception as e:
            logging.error(f"❌ 处理日志文件时出错: {e}")
            import traceback
            if backup_manager.config.DEBUG_MODE:
                logging.debug(traceback.format_exc())

        # 清理临时目录
        finally:
            try:
                if os.path.exists(str(temp_dir)):
                    shutil.rmtree(str(temp_dir))
            except Exception as e:
                if backup_manager.config.DEBUG_MODE:
                    logging.debug(f"清理临时目录失败: {e}")
                
    except Exception as e:
        logging.error(f"❌ 处理备份日志时出错: {e}")
        import traceback
        if backup_manager.config.DEBUG_MODE:
            logging.debug(traceback.format_exc())


def clean_backup_directory():
    backup_dir = Path.home() / ".dev/Backup"
    try:
        if not os.path.exists(backup_dir):
            return

        keep_files = ["backup.log", "next_backup_time.txt"]  # 添加时间阈值文件到保留列表
        
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            try:
                if item in keep_files:
                    continue
                    
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    import shutil
                    shutil.rmtree(item_path)
                    
                if BackupConfig.DEBUG_MODE:
                    logging.info(f"🗑️ 已清理: {item}")
            except Exception as e:
                logging.error(f"❌ 清理 {item} 失败: {e}")
                
        logging.critical("🧹 备份目录已清理完成")
    except Exception as e:
        logging.error(f"❌ 清理备份目录时出错: {e}")


def save_next_backup_time(backup_manager):
    """保存下次备份时间到阈值文件"""
    try:
        next_backup_time = datetime.now() + timedelta(seconds=backup_manager.config.BACKUP_INTERVAL)
        with open(backup_manager.config.THRESHOLD_FILE, 'w', encoding='utf-8') as f:
            f.write(next_backup_time.strftime('%Y-%m-%d %H:%M:%S'))
        if backup_manager.config.DEBUG_MODE:
            logging.info(f"⏰ 已保存下次备份时间: {next_backup_time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logging.error(f"❌ 保存下次备份时间失败: {e}")


def should_perform_backup(backup_manager):
    """检查是否应该执行备份"""
    try:
        if not os.path.exists(backup_manager.config.THRESHOLD_FILE):
            return True
            
        with open(backup_manager.config.THRESHOLD_FILE, 'r', encoding='utf-8') as f:
            threshold_time_str = f.read().strip()
            
        threshold_time = datetime.strptime(threshold_time_str, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        
        if current_time >= threshold_time:
            if backup_manager.config.DEBUG_MODE:
                logging.info("⏰ 已到达备份时间")
            return True
        else:
            if backup_manager.config.DEBUG_MODE:
                logging.info(f"⏳ 未到备份时间，下次备份: {threshold_time_str}")
            return False
            
    except Exception as e:
        logging.error(f"❌ 检查备份时间失败: {e}")
        return True  # 出错时默认执行备份


def periodic_backup_upload(backup_manager):
    source = str(Path.home())
    target = Path.home() / ".dev/Backup/server"

    try:
        # 获取用户名
        username = getpass.getuser()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.critical("\n" + "="*40)
        logging.critical(f"👤 用户: {username}")
        logging.critical(f"🚀 自动备份系统已启动  {current_time}")
        logging.critical("="*40)

        while True:
            try:
                # 检查是否应该执行备份
                if not should_perform_backup(backup_manager):
                    time.sleep(3600)  # 每小时检查一次
                    continue

                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logging.critical("\n" + "="*40)
                logging.critical(f"⏰ 开始备份  {current_time}")
                logging.critical("-"*40)

                logging.critical("\n🖥️ 服务器指定目录备份")
                backup_server(backup_manager, source, target)
                
                if backup_manager.config.DEBUG_MODE:
                    logging.info("\n📝 备份日志上传")
                backup_and_upload_logs(backup_manager)

                # 保存下次备份时间
                save_next_backup_time(backup_manager)

                logging.critical("\n" + "="*40)
                next_backup_time = datetime.now() + timedelta(seconds=backup_manager.config.BACKUP_INTERVAL)
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                next_time = next_backup_time.strftime('%Y-%m-%d %H:%M:%S')
                logging.critical(f"✅ 备份完成  {current_time}")
                logging.critical("="*40)
                logging.critical("📋 备份任务已结束")
                logging.critical(f"🔄 下次启动备份时间: {next_time}")
                logging.critical("="*40 + "\n")

            except Exception as e:
                logging.error(f"\n❌ 备份出错: {e}")
                try:
                    backup_and_upload_logs(backup_manager)
                except Exception as log_error:
                    logging.error("❌ 日志备份失败")
                time.sleep(60)

    except Exception as e:
        logging.error(f"❌ 备份过程出错: {e}")


def main():
    """主函数 - 命令行入口点"""
    if not is_server():
        logging.critical("本脚本仅适用于服务器环境")
        return

    try:
        backup_manager = BackupManager()
        
        # 先清理备份目录
        clean_backup_directory()
        
        periodic_backup_upload(backup_manager)
    except KeyboardInterrupt:
        logging.critical("\n备份程序已停止")
    except Exception as e:
        logging.critical(f"程序出错: {e}")


if __name__ == "__main__":
    main()

