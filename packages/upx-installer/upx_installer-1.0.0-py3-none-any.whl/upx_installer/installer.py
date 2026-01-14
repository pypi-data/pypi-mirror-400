"""
UPX安装器核心模块
提供安装、卸载和验证功能
"""

import os
import sys
import platform
import shutil
import hashlib
import json
from pathlib import Path

# 尝试导入pkg_resources，如果不可用则使用备用方法
try:
    import pkg_resources
    PKG_RESOURCES_AVAILABLE = True
except ImportError:
    PKG_RESOURCES_AVAILABLE = False

# 安装记录文件位置（用户目录）
INSTALL_RECORD_PATH = Path.home() / '.upx_installer_record.json'
# UPX目标路径
WINDOWS_TARGET_PATH = Path('C:/Windows/upx.exe')
# 备份目录
BACKUP_DIR = Path.home() / '.upx_installer_backup'

def get_upx_source_path():
    """获取包内UPX可执行文件的路径"""
    if PKG_RESOURCES_AVAILABLE:
        try:
            return pkg_resources.resource_filename('upx_installer', 'data/upx.exe')
        except:
            pass
    
    # 备用方法：尝试从包目录查找
    package_dir = Path(__file__).parent
    data_file = package_dir / 'data' / 'upx.exe'
    if data_file.exists():
        return str(data_file)
    
    # 如果都找不到，返回None
    return None

def calculate_file_hash(file_path):
    """计算文件的MD5哈希值"""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
        return file_hash.hexdigest()
    except Exception:
        return None

def load_install_record():
    """加载安装记录"""
    if INSTALL_RECORD_PATH.exists():
        try:
            with open(INSTALL_RECORD_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_install_record(record):
    """保存安装记录"""
    try:
        with open(INSTALL_RECORD_PATH, 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2)
        return True
    except Exception:
        return False

def create_backup(file_path):
    """创建文件备份"""
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    backup_file = BACKUP_DIR / f"upx_backup_{Path(file_path).name}"
    try:
        if Path(file_path).exists():
            shutil.copy2(file_path, backup_file)
            return str(backup_file)
    except Exception:
        pass
    return None

def install_upx(force=False, backup=True):
    """
    安装UPX到系统
    
    Args:
        force: 是否强制安装（覆盖现有文件）
        backup: 是否创建备份
    """
    # 检查操作系统
    if platform.system() != 'Windows':
        print("UPX安装器仅支持Windows系统")
        return False
    
    # 获取源文件路径
    source_path = get_upx_source_path()
    if not source_path or not Path(source_path).exists():
        print("错误：在包中找不到UPX可执行文件")
        return False
    
    target_path = WINDOWS_TARGET_PATH
    
    # 检查目标文件是否已存在
    target_exists = target_path.exists()
    
    if target_exists and not force:
        print(f"UPX已存在于 {target_path}")
        print("使用 force=True 参数强制覆盖安装")
        return False
    
    # 如果需要备份
    backup_path = None
    if backup and target_exists:
        backup_path = create_backup(target_path)
        if backup_path:
            print(f"已创建备份: {backup_path}")
    
    try:
        # 复制文件
        shutil.copy2(source_path, target_path)
        
        # 计算哈希并保存记录
        source_hash = calculate_file_hash(source_path)
        record = load_install_record()
        record['installed'] = True
        record['install_path'] = str(target_path)
        record['source_hash'] = source_hash
        record['install_time'] = str(Path(source_path).stat().st_mtime)
        record['backup_path'] = backup_path
        
        save_install_record(record)
        
        print(f"UPX已成功安装到: {target_path}")
        if backup_path:
            print(f"原文件已备份到: {backup_path}")
        return True
        
    except PermissionError:
        print("错误：权限不足，无法写入C:\\Windows目录")
        print("请以管理员身份运行或手动复制文件")
        return False
    except Exception as e:
        print(f"安装失败: {e}")
        return False

def uninstall_upx(restore_backup=False):
    """
    卸载UPX
    
    Args:
        restore_backup: 是否从备份恢复原文件
    """
    if platform.system() != 'Windows':
        print("UPX安装器仅支持Windows系统")
        return False
    
    target_path = WINDOWS_TARGET_PATH
    record = load_install_record()
    
    # 检查是否由本包安装
    if not record.get('installed', False):
        print("未找到由本包安装的UPX记录")
        # 仍然尝试删除，但警告用户
        user_confirm = input("是否继续删除UPX文件？(y/n): ")
        if user_confirm.lower() != 'y':
            print("取消卸载")
            return False
    
    try:
        # 如果启用恢复备份且存在备份
        if restore_backup and 'backup_path' in record and record['backup_path']:
            backup_path = Path(record['backup_path'])
            if backup_path.exists():
                shutil.copy2(backup_path, target_path)
                print(f"已从备份恢复UPX: {backup_path}")
            else:
                print("警告：备份文件不存在，无法恢复")
        elif target_path.exists():
            # 删除文件
            target_path.unlink()
            print(f"已删除UPX文件: {target_path}")
        else:
            print("UPX文件不存在，无需删除")
        
        # 清理安装记录
        if INSTALL_RECORD_PATH.exists():
            INSTALL_RECORD_PATH.unlink()
            print("已清理安装记录")
        
        # 可选：清理备份目录
        if BACKUP_DIR.exists():
            try:
                shutil.rmtree(BACKUP_DIR)
                print(f"已清理备份目录: {BACKUP_DIR}")
            except Exception as e:
                print(f"警告：无法清理备份目录: {e}")
        
        return True
        
    except PermissionError:
        print("错误：权限不足，无法修改C:\\Windows目录中的文件")
        print("请以管理员身份运行")
        return False
    except Exception as e:
        print(f"卸载失败: {e}")
        return False

def verify_installation():
    """验证UPX安装"""
    if platform.system() != 'Windows':
        print("UPX安装器仅支持Windows系统")
        return False
    
    target_path = WINDOWS_TARGET_PATH
    record = load_install_record()
    
    if not target_path.exists():
        print("UPX未安装")
        return False
    
    # 检查文件哈希是否匹配记录
    current_hash = calculate_file_hash(target_path)
    recorded_hash = record.get('source_hash')
    
    if recorded_hash and current_hash == recorded_hash:
        print(f"UPX安装验证成功: {target_path}")
        print(f"文件哈希匹配: {current_hash}")
        return True
    else:
        print(f"UPX已安装但验证失败: {target_path}")
        if recorded_hash:
            print(f"记录哈希: {recorded_hash}")
        print(f"当前哈希: {current_hash}")
        return False

def check_upx_version():
    """检查UPX版本（需要UPX可执行文件支持）"""
    if platform.system() != 'Windows':
        return None
    
    target_path = WINDOWS_TARGET_PATH
    if not target_path.exists():
        return None
    
    try:
        import subprocess
        result = subprocess.run([str(target_path), '--version'], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    return None

if __name__ == "__main__":
    # 命令行接口
    import argparse
    
    parser = argparse.ArgumentParser(description="UPX安装器命令行工具")
    parser.add_argument('action', choices=['install', 'uninstall', 'verify', 'version'],
                       help="执行的操作")
    parser.add_argument('--force', action='store_true',
                       help="强制安装（覆盖现有文件）")
    parser.add_argument('--no-backup', action='store_true',
                       help="安装时不创建备份")
    parser.add_argument('--restore-backup', action='store_true',
                       help="卸载时从备份恢复")
    
    args = parser.parse_args()
    
    if args.action == 'install':
        success = install_upx(force=args.force, backup=not args.no_backup)
        sys.exit(0 if success else 1)
    elif args.action == 'uninstall':
        success = uninstall_upx(restore_backup=args.restore_backup)
        sys.exit(0 if success else 1)
    elif args.action == 'verify':
        success = verify_installation()
        sys.exit(0 if success else 1)
    elif args.action == 'version':
        version_info = check_upx_version()
        if version_info:
            print(f"UPX版本: {version_info}")
        else:
            print("无法获取UPX版本信息")
        sys.exit(0)
