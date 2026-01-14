# UPX Installer

一个Python包，自动安装UPX可执行文件到Windows系统的C:\Windows目录。

## 功能特性

- **自动安装**: 安装Python包时自动将UPX复制到C:\Windows目录
- **卸载功能**: 提供完整的卸载功能，可恢复备份文件
- **验证机制**: 验证UPX安装的正确性
- **备份恢复**: 安装时自动备份现有UPX文件
- **跨平台**: 虽然主要针对Windows，但在其他系统上也可安全安装（不复制文件）

## 安装方法

### 从PyPI安装（推荐）

```bash
pip install upx-installer
```

安装完成后，UPX将自动安装到C:\Windows目录。

### 手动安装（开发模式）

```bash
# 克隆仓库
git clone https://github.com/example/upx-installer.git
cd upx-installer

# 安装开发版本
pip install -e .
```

## 使用方法

### 命令行工具

安装后，可以使用 `upx-installer` 命令行工具：

```bash
# 安装UPX（如果未自动安装）
upx-installer install

# 强制重新安装
upx-installer install --force

# 安装时不创建备份
upx-installer install --no-backup

# 卸载UPX
upx-installer uninstall

# 卸载并恢复备份
upx-installer uninstall --restore-backup

# 验证安装
upx-installer verify

# 检查UPX版本
upx-installer version
```

### Python API

```python
import upx_installer

# 安装UPX
upx_installer.install_upx()

# 强制安装
upx_installer.install_upx(force=True)

# 卸载UPX
upx_installer.uninstall_upx()

# 验证安装
upx_installer.verify_installation()
```

## 权限要求

在Windows系统上，写入C:\Windows目录需要管理员权限。如果遇到权限错误：

1. **以管理员身份运行命令提示符/PowerShell**
2. 或手动将UPX复制到C:\Windows目录

## 技术细节

### 文件位置

- **UPX源文件**: 包内的 `upx_installer/data/upx.exe`
- **安装目标**: `C:\Windows\upx.exe`
- **安装记录**: `%USERPROFILE%\.upx_installer_record.json`
- **备份文件**: `%USERPROFILE%\.upx_installer_backup\`

### 安装验证

安装时会计算UPX文件的MD5哈希值并保存到安装记录中。验证时比较当前文件的哈希值与记录值，确保文件未被修改。

## 开发指南

### 环境设置

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/
```

### 构建包

```bash
# 构建源码包和wheel
python setup.py sdist bdist_wheel

# 或使用build工具
python -m build
```

### 发布到PyPI

```bash
# 上传到PyPI
twine upload dist/*
```

## 常见问题

### Q: 安装时出现权限错误怎么办？
**A**: 请以管理员身份运行命令提示符或PowerShell，然后重新安装。

### Q: 非Windows系统可以使用吗？
**A**: 可以安装包，但不会复制UPX文件（因为目标路径是C:\Windows）。

### Q: 如何手动安装UPX？
**A**: 只需将UPX可执行文件复制到C:\Windows目录或系统PATH中的任何目录。

### Q: 这个包包含UPX的哪个版本？
**A**: 包含当前包版本的UPX可执行文件。使用 `upx-installer version` 查看具体版本。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交Issue和Pull Request！

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启Pull Request

## 免责声明

本软件按"原样"提供，不提供任何明示或暗示的担保。使用UPX请遵守其原始许可证。
