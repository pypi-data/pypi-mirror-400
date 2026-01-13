"""
安装后钩子：在项目根目录创建必要的目录结构
"""
import os
import sys
import shutil
from pathlib import Path


def find_project_root(start_path=None):
    """
    查找项目根目录（包含 setup.py 或 run.py 的目录）
    
    此函数会智能查找项目根目录，不受虚拟环境位置影响。
    它会从起始路径向上查找，直到找到包含 setup.py 或 run.py 的目录。
    
    Args:
        start_path: 起始查找路径，默认为当前工作目录
    
    Returns:
        Path: 项目根目录的绝对路径
    """
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path)
    
    current = start_path.resolve()
    
    # 检查当前目录是否是项目根目录
    if (current / 'setup.py').exists() or (current / 'run.py').exists():
        return current
    
    # 向上查找，最多查找 10 层（避免在虚拟环境中误判）
    for _ in range(10):
        if (current / 'setup.py').exists() or (current / 'run.py').exists():
            return current
        parent = current.parent
        if parent == current:  # 已到达文件系统根目录
            break
        current = parent
    
    # 如果找不到项目根目录标识文件，返回起始路径的绝对路径
    # 这适用于新项目初始化的情况
    return start_path.resolve()


def create_project_directories():
    """
    在项目根目录创建必要的目录结构
    使用运行命令时的当前工作目录作为项目根目录
    
    注意：
    - 此函数不会在项目根目录创建 README.md 文件
    - 此函数不会在 docs 目录创建 README.md 文件
    - 只会在子目录（model、config、translations、scheduler）中创建 README.md 说明文件
    """
    # 直接使用当前工作目录作为项目根目录
    current_dir = Path.cwd().resolve()
    
    print("\n" + "=" * 60)
    print("🚀 开始初始化 Fred Framework 项目")
    print("=" * 60)
    print(f"\n项目根目录: {current_dir}\n")
    
    # 明确不创建根目录和 docs 目录的 README.md 文件
    # 只会在子目录中创建 README.md 说明文件
    
    # 定义要创建的目录及其说明
    directories = {
        'model': {
            'description': '数据模型目录',
            'details': '''此目录用于存放数据模型文件。

功能说明：
- 存放数据模型相关的业务逻辑
- 存放模型验证和序列化相关代码
- 存放其他数据模型相关代码

使用示例：
```python
from model.model import YourModel
```
'''
        },
        'config': {
            'description': '配置文件目录',
            'details': '''此目录用于存放项目配置文件。

功能说明：
- 存放自定义配置类（继承自 fred_framework.config.Config）
- 存放环境相关的配置文件
- 存放敏感信息配置文件（建议加入 .gitignore）

使用示例：
在 config/Config.py 中定义：
```python
from fred_framework.config.Config import Config

class CustomConfig(Config):
    # 自定义配置项
    CUSTOM_SETTING = 'value'
```
'''
        },
        'translations': {
            'description': '国际化翻译文件目录',
            'details': '''此目录用于存放多语言翻译文件。

功能说明：
- 存放 Babel 翻译文件（.po, .mo）
- 支持多语言切换
- 配合 flask_babelplus 使用

使用示例：
```python
from flask_babelplus import gettext as _

_('Hello World')  # 根据当前语言返回翻译
```
'''
        },
        'scheduler': {
            'description': '定时任务目录',
            'details': '''此目录用于存放定时任务定义。

功能说明：
- 存放 APScheduler 定时任务函数
- 存放任务调度相关配置
- 存放任务执行逻辑

使用示例：
在 scheduler/tasks.py 中定义：
```python
from flask_apscheduler import APScheduler

def my_scheduled_task():
    # 任务逻辑
    pass

# 在配置中注册任务
# SCHEDULER_JOBS = [
#     {
#         'id': 'job1',
#         'func': 'scheduler.tasks:my_scheduled_task',
#         'trigger': 'interval',
#         'seconds': 60
#     }
# ]
```
'''
        }
    }
    
    created_dirs = []
    skipped_dirs = []
    
    print("📁 步骤 1/8: 创建项目目录结构")
    for dir_name, info in directories.items():
        dir_path = current_dir / dir_name
        
        # 检查目录是否已存在
        dir_exists = dir_path.exists() and dir_path.is_dir()
        
        # 创建目录（如果不存在）
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            if not dir_exists:
                created_dirs.append(dir_name)
                print(f"   ✓ 创建目录: {dir_name}/")
            else:
                skipped_dirs.append(dir_name)
                print(f"   ⊘ 目录已存在，跳过: {dir_name}/")
            
            # 创建 README.md 说明文件（如果不存在）
            readme_path = dir_path / 'README.md'
            if not readme_path.exists():
                readme_content = f'''# {dir_name.upper()} 目录

## {info['description']}

{info['details']}

---
*此目录由 fred_framework 自动创建*
'''
                readme_path.write_text(readme_content, encoding='utf-8')
                print(f"      ✓ 创建说明文件: {dir_name}/README.md")
            
            # 创建 __init__.py 文件（如果是 Python 包）
            if dir_name in ['model', 'config', 'scheduler']:
                init_path = dir_path / '__init__.py'
                if not init_path.exists():
                    init_path.write_text('# -*- coding: utf-8 -*-\n', encoding='utf-8')
                    print(f"      ✓ 创建包文件: {dir_name}/__init__.py")
            
        except Exception as e:
            print(f"   ⚠ 创建目录失败: {dir_name}/ ({e})")
    
    # 创建 docs 目录（用于存放所有文档）
    # 注意：不会在 docs 目录创建 README.md 文件
    docs_dir = current_dir / 'docs'
    try:
        if not docs_dir.exists():
            docs_dir.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ 创建目录: docs/")
        else:
            print(f"   ⊘ 目录已存在，跳过: docs/")
    except Exception as e:
        print(f"   ⚠ 创建目录失败: docs/ ({e})")
    
    # 复制 Config.py 到 config 目录
    print("\n📝 步骤 2/8: 创建配置文件")
    copy_config_file(current_dir)
    
    # 创建 run.py 文件
    print("\n🎯 步骤 3/8: 创建应用启动文件")
    create_run_file(current_dir)
    
    # 复制 demo 目录到项目根目录（已禁用，不再自动生成）
    # copy_demo_directory(current_dir)
    
    # 创建命令使用文档（放到 docs 目录）
    print("\n📚 步骤 4/8: 创建文档文件")
    create_commands_documentation(current_dir)
    copy_code_standards_file(current_dir)
    copy_frontend_documentation(current_dir)
    
    # 创建 requirements.txt 文件
    print("\n📦 步骤 5/8: 创建依赖文件")
    create_requirements_file(current_dir)
    
    # 创建 .gitignore 文件
    print("\n🔒 步骤 6/8: 创建 Git 配置文件")
    create_gitignore_file(current_dir)
    
    # 复制 frontend 目录到项目根目录
    print("\n🎨 步骤 7/8: 复制前端代码")
    copy_frontend_to_project_root(current_dir)
    
    # 复制 vscode 目录到项目根目录（重命名为 .vscode）
    print("\n⚙️  步骤 8/8: 复制开发工具配置")
    copy_vscode_to_project_root(current_dir)
    
    # 复制 sql 目录到项目根目录
    copy_sql_to_project_root(current_dir)
    
    print("\n" + "=" * 60)
    print("✅ 项目初始化完成！")
    print("=" * 60)
    
    return len(created_dirs) > 0


def copy_demo_directory(project_root):
    """
    将 src/demo 目录复制到项目根目录，支持无限级目录递归复制
    
    功能特点：
    - 支持无限级目录结构
    - 如果目标目录已存在，会合并复制（只复制不存在的文件/目录）
    - 保留目标目录中已存在的文件
    """
    try:
        # 获取当前文件所在的目录
        current_file_path = Path(__file__)
        # 构建源 demo 目录路径
        source_demo_path = current_file_path.parent / 'demo'
        # 目标路径为项目根目录下的 demo 目录
        target_demo_path = project_root / 'demo'
        
        # 检查源目录是否存在
        if not source_demo_path.exists() or not source_demo_path.is_dir():
            return
        
        # 如果目标目录不存在，直接复制整个目录树
        if not target_demo_path.exists():
            shutil.copytree(source_demo_path, target_demo_path)
            return
        
        # 目标目录已存在，进行递归合并复制
        copied_count = _copy_directory_recursive(source_demo_path, target_demo_path)
            
    except Exception as e:
        pass


def _copy_directory_recursive(source_path, target_path):
    """
    递归复制目录，支持无限级目录结构
    
    参数:
        source_path: 源目录路径
        target_path: 目标目录路径
    
    返回:
        int: 复制的文件/目录数量
    """
    copied_count = 0
    
    # 确保目标目录存在
    if not target_path.exists():
        target_path.mkdir(parents=True, exist_ok=True)
        copied_count += 1
    
    # 遍历源目录中的所有项目
    for item in source_path.iterdir():
        source_item = source_path / item.name
        target_item = target_path / item.name
        
        try:
            if source_item.is_file():
                # 如果是文件，且目标文件不存在，则复制
                if not target_item.exists():
                    shutil.copy2(source_item, target_item)
                    copied_count += 1
                # 如果目标文件已存在，跳过（保留用户自定义的文件）
            
            elif source_item.is_dir():
                # 如果是目录，递归复制
                if not target_item.exists():
                    # 目标目录不存在，直接复制整个目录树
                    # 使用 dirs_exist_ok=True 参数（Python 3.8+）以避免目标目录已存在的错误
                    try:
                        shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                        # 统计复制的文件数量（包括目录本身）
                        file_count = sum(1 for _ in target_item.rglob('*') if _.is_file())
                        dir_count = sum(1 for _ in target_item.rglob('*') if _.is_dir())
                        copied_count += file_count + dir_count if (file_count + dir_count) > 0 else 1
                    except Exception as copytree_error:
                        # 如果 copytree 失败，尝试使用递归方式
                        target_item.mkdir(parents=True, exist_ok=True)
                        sub_copied = _copy_directory_recursive(source_item, target_item)
                        copied_count += sub_copied if sub_copied > 0 else 1
                else:
                    # 目标目录已存在，递归合并
                    sub_copied = _copy_directory_recursive(source_item, target_item)
                    copied_count += sub_copied
        
        except Exception as e:
            # 单个文件/目录复制失败不影响整体流程
            continue
    
    return copied_count


def copy_config_file(project_root):
    """
    将 fred_framework.config.Config 复制到项目根目录的 config 目录中
    如果文件已存在，只更新 PROJECT_ROOT 配置，不覆盖其他内容
    """
    config_dir = project_root / 'config'
    target_config_file = config_dir / 'Config.py'
    
    # 如果目标文件已存在，只更新 PROJECT_ROOT，不覆盖文件
    file_exists = target_config_file.exists()
    
    if file_exists:
        print("   ⊘ 配置文件已存在，跳过: config/Config.py")
        return
    
    # 如果文件不存在，需要从源文件复制
    if not file_exists:
        # 尝试从多个可能的路径找到源 Config.py 文件
        source_paths = [
            # 方式1: 从已安装的包中查找
            Path(__file__).parent.parent / 'config' / 'Config.py',
            # 方式2: 从当前文件位置推断（开发模式）
            Path(__file__).parent.parent.parent.parent / 'src' / 'fred_framework' / 'config' / 'Config.py',
            # 方式3: 尝试导入模块获取路径
        ]
        
        # 方式3: 通过导入模块获取路径
        try:
            import fred_framework.config.Config as config_module
            if hasattr(config_module, '__file__'):
                source_paths.insert(0, Path(config_module.__file__))
        except Exception:
            pass
        
        source_config_file = None
        for path in source_paths:
            if path.exists() and path.is_file():
                source_config_file = path
                break
        
        if source_config_file is None:
            return
        
        # 确保 config 目录存在
        if not config_dir.exists():
            try:
                config_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return
        
        # 复制文件
        try:
            shutil.copy2(source_config_file, target_config_file)
            print("   ✓ 复制配置文件: config/Config.py")
        except Exception as e:
            print(f"   ⚠ 复制配置文件失败: {e}")
            return
    
    # 确保 config 目录存在
    if not config_dir.exists():
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"   ⚠ 创建 config 目录失败: {e}")
            return
    
    # 读取文件内容并设置项目根目录（无论文件是新创建还是已存在）
    try:
        content = target_config_file.read_text(encoding='utf-8')
        
        # 在文件开头添加说明注释（如果不存在且文件是新创建的）
        if not file_exists and not content.startswith('# -*- coding: utf-8 -*-'):
            header = '''# -*- coding: utf-8 -*-
"""
配置文件 - 从 fred_framework.config.Config 复制而来
你可以在此文件中自定义配置项，继承或覆盖默认配置
"""
'''
            content = header + content
        
        # 获取项目根目录的绝对路径
        project_root_path = project_root.resolve()
        
        # 设置 PROJECT_ROOT 配置
        import re
        
        # 获取项目根目录的字符串表示
        project_root_str = str(project_root_path)
        
        # 直接替换 PROJECT_ROOT = "" 中引号内的路径值
        # 匹配模式：PROJECT_ROOT = r"路径" 或 PROJECT_ROOT = "路径"
        pattern = r'(PROJECT_ROOT\s*=\s*r?["\'])([^"\']*)(["\'])'
        replacement = f'\\1{project_root_str}\\3'
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # 写回文件
        target_config_file.write_text(content, encoding='utf-8')
        print("      ✓ 已更新 PROJECT_ROOT 配置")
    except Exception as e:
        print(f"   ⚠ 更新配置文件失败: {e}")


def create_run_file(project_root):
    """
    在项目根目录创建 run.py 文件
    """
    run_file_path = project_root / 'run.py'
    
    # 如果文件已存在，跳过（保留用户自定义的 run.py）
    if run_file_path.exists():
        print("   ⊘ 启动文件已存在，跳过: run.py")
        return
    
    # run.py 文件内容（只包含指定行的内容）
    run_file_content = '''from fred_framework import create_app
# 创建应用
app = create_app()

if __name__ == '__main__':
    app.run()
'''
    
    try:
        run_file_path.write_text(run_file_content, encoding='utf-8')
        print("   ✓ 创建启动文件: run.py")
    except Exception as e:
        print(f"   ⚠ 创建启动文件失败: {e}")


def create_requirements_file(project_root):
    """
    在项目根目录创建 requirements.txt 文件
    """
    requirements_file_path = project_root / 'requirements.txt'
    
    # 如果文件已存在，跳过（保留用户自定义的依赖）
    if requirements_file_path.exists():
        print("   ⊘ 依赖文件已存在，跳过: requirements.txt")
        return
    
    # requirements.txt 文件内容
    requirements_content = 'fred_framework\n'
    
    try:
        requirements_file_path.write_text(requirements_content, encoding='utf-8')
        print("   ✓ 创建依赖文件: requirements.txt")
    except Exception as e:
        print(f"   ⚠ 创建依赖文件失败: {e}")


def create_gitignore_file(project_root):
    """
    在项目根目录创建 .gitignore 文件
    """
    gitignore_file_path = project_root / '.gitignore'
    
    # 如果文件已存在，跳过（保留用户自定义的 .gitignore）
    if gitignore_file_path.exists():
        print("   ⊘ Git 配置文件已存在，跳过: .gitignore")
        return
    
    # .gitignore 文件内容
    gitignore_content = '''__pycache__
.idea
venv
logs
dist
dist-ssr
*.spec
.DS_Store
coverage
*.local

# Python build artifacts
*.egg-info
build/
*.egg

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules

/cypress/videos/
/cypress/screenshots/

# Editor directories and files
!.vscode/extensions.json
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
*.tsbuildinfo
.venv
.ipynb_checkpoints
config/Config.py
docker-compose.override.yml
model/*
'''
    
    try:
        gitignore_file_path.write_text(gitignore_content, encoding='utf-8')
    except Exception as e:
        pass


def copy_code_standards_file(project_root):
    """
    将代码规范文档复制到项目根目录的 docs 目录
    """
    # 确保 docs 目录存在
    docs_dir = project_root / 'docs'
    try:
        docs_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        pass
    
    target_file = docs_dir / '代码规范.md'
    
    # 如果文件已存在，跳过（保留用户自定义的文档）
    if target_file.exists():
        print("   ⊘ 文档已存在，跳过: docs/代码规范.md")
        return
    
    # 尝试从多个可能的路径找到源文件
    source_paths = []
    
    # 方式1: 从当前文件位置推断（开发模式）
    current_file_path = Path(__file__)
    # 开发模式：src/fred_framework/install_hook.py -> src/fred_framework/代码规范.md
    dev_standards_path = current_file_path.parent / '代码规范.md'
    if dev_standards_path.exists():
        source_paths.append(dev_standards_path)
    
    # 方式2: 通过导入模块获取路径（已安装的包）
    try:
        import fred_framework
        if hasattr(fred_framework, '__file__'):
            package_dir = Path(fred_framework.__file__).parent
            standards_path = package_dir / '代码规范.md'
            if standards_path.exists():
                source_paths.insert(0, standards_path)
    except Exception:
        pass
    
    # 方式3: 尝试使用 pkg_resources 查找（如果可用）
    try:
        import pkg_resources
        try:
            dist = pkg_resources.get_distribution('fred_framework')
            if dist.location:
                pkg_standards = Path(dist.location) / 'fred_framework' / '代码规范.md'
                if pkg_standards.exists():
                    source_paths.insert(0, pkg_standards)
        except Exception:
            pass
    except ImportError:
        pass
    
    # 方式4: 尝试使用 importlib.metadata 查找（Python 3.8+）
    try:
        from importlib.metadata import files, PackageNotFoundError
        try:
            package_files = files('fred_framework')
            for file in package_files:
                if file.name == '代码规范.md':
                    standards_path = Path(file.locate())
                    if standards_path.exists():
                        source_paths.insert(0, standards_path)
                        break
        except (PackageNotFoundError, Exception):
            pass
    except ImportError:
        pass
    
    source_file = None
    for path in source_paths:
        if path.exists() and path.is_file():
            source_file = path
            break
    
    if source_file is None:
        print("   ⚠ 未找到代码规范文档源文件")
        return
    
    # 复制文件
    try:
        shutil.copy2(source_file, target_file)
        print("   ✓ 复制文档: docs/代码规范.md")
    except Exception as e:
        print(f"   ⚠ 复制文档失败: {e}")


def copy_frontend_to_project_root(project_root):
    """
    将 demo/frontend 目录复制到项目根目录（如果不存在）
    确保复制所有文件，包括隐藏文件（以点开头的文件）
    
    Args:
        project_root: 项目根目录路径
    """
    try:
        # 获取当前文件所在的目录
        current_file_path = Path(__file__)
        # 构建源 demo/frontend 目录路径
        source_frontend_path = current_file_path.parent / 'demo' / 'frontend'
        
        # 检查源目录是否存在
        if not source_frontend_path.exists() or not source_frontend_path.is_dir():
            print("   ⚠ 源前端目录不存在，跳过复制")
            return
        
        # 目标 frontend 目录路径（项目根目录）
        target_frontend_path = project_root / 'frontend'
        
        # 如果目标目录已存在，跳过（不覆盖）
        if target_frontend_path.exists():
            print("   ⊘ 前端目录已存在，跳过: frontend/")
            return
        
        # 需要重命名为带点开头的文件名列表（源文件名 -> 目标文件名）
        # 保留此映射以支持向后兼容（如果源文件没有 demo_ 前缀）
        DOT_FILES_MAP = {
            'editorconfig': '.editorconfig',
            'eslintignore': '.eslintignore',
            'eslintrc.cjs': '.eslintrc.cjs',
            'gitignore': '.gitignore',
            'prettierignore': '.prettierignore',
            'prettierrc.cjs': '.prettierrc.cjs',
            'stylelintignore': '.stylelintignore',
            'stylelintrc.cjs': '.stylelintrc.cjs',
            'env': '.env',
            'env.development': '.env.development',
            'env.production': '.env.production'
        }
        
        def copy_all_files_with_dot_handling(src_path: Path, dst_path: Path):
            """
            复制所有文件，包括需要重命名为隐藏文件的文件
            策略：
            1. 如果文件名以 demo_ 开头，将 demo_ 替换为 . 后复制
            2. 否则，检查是否在 DOT_FILES_MAP 中，如果是则重命名为带点版本
            3. 递归处理所有目录，包括 src 目录
            """
            src_str = str(src_path)
            dst_str = str(dst_path)
            
            # 确保目标目录存在
            os.makedirs(dst_str, exist_ok=True)
            
            # 使用 os.listdir 获取所有文件和目录
            try:
                items = os.listdir(src_str)
            except OSError:
                items = []
            
            # 存储需要重命名的文件：源文件名 -> 目标文件名（带点）
            rename_files = {}
            
            for item in items:
                src_item = os.path.join(src_str, item)
                
                # 检查文件名是否以 demo_ 开头
                if item.startswith('demo_'):
                    # 将 demo_ 替换为 .
                    target_item_name = item.replace('demo_', '.', 1)  # 只替换第一个匹配
                    dst_item = os.path.join(dst_str, target_item_name)
                else:
                    dst_item = os.path.join(dst_str, item)
                
                if os.path.isdir(src_item):
                    # 递归复制目录（目录名也可能需要处理）
                    if item.startswith('demo_'):
                        # 目录名也以 demo_ 开头，需要替换
                        target_dir_name = item.replace('demo_', '.', 1)
                        target_dir_path = Path(dst_str) / target_dir_name
                    else:
                        target_dir_path = Path(dst_item)
                    copy_all_files_with_dot_handling(Path(src_item), target_dir_path)
                else:
                    # 复制文件，保留元数据
                    # 如果文件名以 demo_ 开头，直接使用替换后的名称复制
                    shutil.copy2(src_item, dst_item)
                    
                    # 如果文件名不是以 demo_ 开头，检查是否需要重命名为带点版本（向后兼容）
                    if not item.startswith('demo_') and item in DOT_FILES_MAP:
                        rename_files[item] = DOT_FILES_MAP[item]
            
            # 复制完成后，重命名需要带点的文件（仅处理非 demo_ 开头的文件）
            for source_name, target_name in rename_files.items():
                source_path = dst_path / source_name
                target_path = dst_path / target_name
                if source_path.exists() and not target_path.exists():
                    try:
                        source_path.rename(target_path)
                    except Exception:
                        pass
        
        # 执行复制
        try:
            copy_all_files_with_dot_handling(source_frontend_path, target_frontend_path)
        except Exception as e:
            # 如果自定义复制失败，尝试使用 shutil.copytree
            try:
                shutil.copytree(
                    source_frontend_path, 
                    target_frontend_path, 
                    dirs_exist_ok=True
                )
            except Exception as e2:
                pass
        
    except Exception as e:
        pass


def copy_frontend_documentation(project_root):
    """
    将 demo/frontend/前端代码说明.md 复制到项目根目录的 docs 目录
    
    Args:
        project_root: 项目根目录路径
    """
    try:
        # 获取当前文件所在的目录
        current_file_path = Path(__file__)
        # 构建源文件路径
        source_file_path = current_file_path.parent / 'demo' / 'frontend' / '前端代码说明.md'
        
        # 检查源文件是否存在
        if not source_file_path.exists() or not source_file_path.is_file():
            return
        
        # 确保 docs 目录存在
        docs_dir = project_root / 'docs'
        try:
            docs_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return
        
        # 目标文件路径
        target_file_path = docs_dir / '前端代码说明.md'
        
        # 如果目标文件已存在，跳过（保留用户自定义的文档）
        if target_file_path.exists():
            print("   ⊘ 文档已存在，跳过: docs/前端代码说明.md")
            return
        
        # 复制文件
        try:
            shutil.copy2(source_file_path, target_file_path)
            print("   ✓ 复制文档: docs/前端代码说明.md")
        except Exception as e:
            print(f"   ⚠ 复制文档失败: {e}")
    except Exception:
        # 复制前端文档失败，静默处理，不报错
        pass


def copy_vscode_to_project_root(project_root):
    """
    将 demo/vscode 目录复制到项目根目录，并重命名为 .vscode（如果不存在）
    
    Args:
        project_root: 项目根目录路径
    """
    try:
        # 获取当前文件所在的目录
        current_file_path = Path(__file__)
        # 构建源 demo/vscode 目录路径
        source_vscode_path = current_file_path.parent / 'demo' / 'vscode'
        
        # 检查源目录是否存在
        if not source_vscode_path.exists() or not source_vscode_path.is_dir():
            print("   ⊘ VSCode 配置目录不存在，跳过")
            return
        
        # 目标 vscode 目录路径（先复制为 vscode，然后重命名为 .vscode）
        target_vscode_path = project_root / 'vscode'
        target_dot_vscode_path = project_root / '.vscode'
        
        # 如果目标 .vscode 目录已存在，跳过（不覆盖）
        if target_dot_vscode_path.exists():
            print("   ⊘ VSCode 配置目录已存在，跳过: .vscode/")
            return
        
        # 如果临时 vscode 目录已存在，先删除
        if target_vscode_path.exists():
            try:
                shutil.rmtree(target_vscode_path)
            except Exception:
                pass
        
        # 复制 vscode 目录
        try:
            shutil.copytree(source_vscode_path, target_vscode_path)
            
            # 复制成功后，重命名为 .vscode
            if target_vscode_path.exists():
                try:
                    target_vscode_path.rename(target_dot_vscode_path)
                    print("   ✓ 复制 VSCode 配置: .vscode/")
                except Exception as e:
                    # 重命名失败，静默处理，不报错
                    # 尝试删除临时目录
                    try:
                        shutil.rmtree(target_vscode_path)
                    except Exception:
                        pass
                    print(f"   ⚠ VSCode 配置复制失败（重命名失败）: {e}")
        except Exception as e:
            print(f"   ⚠ 复制 VSCode 配置失败: {e}")
    except Exception as e:
        print(f"   ⚠ 复制 VSCode 配置失败: {e}")


def copy_sql_to_project_root(project_root):
    """
    将 demo/sql 目录复制到项目根目录（如果不存在）
    
    Args:
        project_root: 项目根目录路径
    """
    try:
        # 获取当前文件所在的目录
        current_file_path = Path(__file__)
        # 构建源 demo/sql 目录路径
        source_sql_path = current_file_path.parent / 'demo' / 'sql'
        
        # 检查源目录是否存在
        if not source_sql_path.exists() or not source_sql_path.is_dir():
            print("   ⊘ SQL 目录不存在，跳过")
            return
        
        # 目标 sql 目录路径（项目根目录）
        target_sql_path = project_root / 'sql'
        
        # 如果目标目录已存在，跳过（不覆盖）
        if target_sql_path.exists():
            print("   ⊘ SQL 目录已存在，跳过: sql/")
            return
        
        # 复制 sql 目录
        try:
            shutil.copytree(source_sql_path, target_sql_path)
            print("   ✓ 复制 SQL 文件: sql/")
        except Exception as e:
            print(f"   ⚠ 复制 SQL 文件失败: {e}")
    except Exception as e:
        print(f"   ⚠ 复制 SQL 文件失败: {e}")


def create_commands_documentation(project_root):
    """
    在项目根目录的 docs 目录创建命令使用文档
    """
    # 确保 docs 目录存在
    docs_dir = project_root / 'docs'
    try:
        docs_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        pass
    
    commands_doc_path = docs_dir / 'FRED_COMMANDS.md'
    
    # 如果文件已存在，跳过（保留用户自定义的文档）
    if commands_doc_path.exists():
        print("   ⊘ 文档已存在，跳过: docs/FRED_COMMANDS.md")
        return
    
    # 命令使用文档内容
    commands_doc_content = '''# Fred Framework 命令使用文档

本文档介绍 Fred Framework 提供的所有命令行工具及其使用方法。

## 可用命令

### 1. fred-init

初始化 Fred Framework 项目，创建必要的目录结构和配置文件。如果提供了模块名，会在初始化完成后自动创建该模块。

**用法：**
```bash
fred-init [MODULE_NAME] [--no-frontend]
```

**参数：**
- `MODULE_NAME` (可选): 模块名称（只能包含字母、数字和下划线）。如果提供，将在初始化完成后自动创建该模块（默认包含 frontend）
- `--no-frontend` (可选): 创建模块时不包含 frontend 目录（仅在提供模块名时有效，默认包含 frontend）

**说明：**
- 使用运行命令时的当前工作目录作为项目根目录
- 建议在项目根目录下运行此命令
- 如果提供了模块名，此命令会同时完成初始化和模块创建两步操作

**功能：**
- 创建项目目录结构：
  - `model/` - 数据模型目录
  - `config/` - 配置文件目录（包含 `Config.py`）
  - `translations/` - 国际化翻译文件目录
  - `scheduler/` - 定时任务目录
  - `docs/` - 文档目录（包含所有 markdown 文档）
- 创建 `run.py` 应用启动文件
- 复制 `demo/frontend` 目录到项目根目录（如果不存在）
- 在 `docs/` 目录中创建以下文档：
  - `FRED_COMMANDS.md` - 命令使用文档
  - `代码规范.md` - 代码规范文档
- 如果提供了模块名，自动创建该模块（默认包含 frontend，等同于执行 `fred-create MODULE_NAME --frontend`）

**示例：**
```bash
# 在项目根目录下运行（推荐）
cd /path/to/your/project

# 仅初始化项目
fred-init

# 初始化项目并创建名为 user 的模块（默认包含 frontend）
fred-init user

# 初始化项目并创建名为 user_management 的模块（支持下划线，默认包含 frontend）
fred-init user_management

# 初始化项目并创建不包含 frontend 的模块
fred-init user --no-frontend
```

**注意：**
- 如果目录或文件已存在，不会覆盖，保留现有内容
- 建议在项目根目录下运行此命令
- 如果模块已存在，创建模块的步骤会失败，但初始化步骤已完成

---

### 2. fred-create

创建新的业务模块，自动生成模块的目录结构和基础文件。

**用法：**
```bash
fred-create MODULE_NAME [--path PATH]
```

**参数：**
- `MODULE_NAME` (必需): 模块名称（只能包含字母、数字和下划线）
- `--path PATH` (可选): 指定项目根目录路径，默认为当前工作目录

**功能：**
自动创建以下目录结构和文件：
```
模块名/
├── __init__.py              # Blueprint 定义
├── controller/
│   ├── __init__.py          # 路由控制和用户验证
│   └── {ModuleName}Controller.py  # 控制器（包含 GET/POST/PUT/DELETE 方法）
├── service/
│   ├── __init__.py
│   └── {ModuleName}Service.py  # 服务层
├── model/
│   └── {ModuleName}Model.py    # 数据模型
├── schema/
│   ├── __init__.py
└──   └── {ModuleName}Schema.py   # Schema 定义

```

**示例：**
```bash
# 创建名为 user 的模块
fred-create user

# 创建名为 user_management 的模块（支持下划线）
fred-create user_management

# 在指定项目目录创建模块
fred-create mymodule --path /path/to/project
```

**说明：**
- 模块名称会自动转换为首字母大写的格式用于类名（如：`user` → `User`，`user_management` → `UserManagement`）
- 生成的模块会自动注册到框架中，可以直接使用
- 所有文件都按照 demo 模块的模板生成，包含必要的导入和基本结构
- 控制器默认包含 GET、POST、PUT、DELETE 四个方法，可根据需要修改

**注意事项：**
- 模块名只能包含字母、数字和下划线
- 如果模块已存在，命令会失败并提示错误
- 建议在项目根目录下运行此命令

---

## 快速开始

### 1. 初始化项目

```bash
# 安装框架后，首先初始化项目
fred-init

# 或者一步完成：初始化项目并创建第一个模块（默认包含 frontend）
fred-init user

# 如果不需要 frontend，可以使用 --no-frontend 参数
fred-init user --no-frontend
```

### 2. 创建业务模块（可选）

如果初始化时没有创建模块，可以后续使用 `fred-create` 命令创建：

```bash
# 创建新的业务模块
fred-create user
```

### 3. 启动应用

```bash
# 启动开发服务器
python run.py
```

---

## 常见问题

### Q: 命令找不到怎么办？

A: 确保已正确安装 Fred Framework：
```bash
pip install fred_framework
# 或开发模式安装
pip install -e .
```

### Q: 如何查看命令帮助？

A: 使用 `--help` 参数：
```bash
fred-init --help
fred-create --help
```

### Q: 模块创建后如何修改？

A: 可以直接编辑生成的文件，框架会自动加载修改后的代码。

### Q: 可以删除已创建的模块吗？

A: 可以，直接删除模块目录即可。但请注意：
- 如果模块中有数据库模型，需要处理数据迁移
- 如果模块已注册路由，需要确保没有其他代码依赖

---

## 更多信息

- 命令文档：查看 `docs/FRED_COMMANDS.md`
- 代码规范：查看 `docs/代码规范.md`
- 配置说明：查看 `config/Config.py`
- 示例代码：查看 `demo/` 目录

---

*本文档由 Fred Framework 自动生成*
'''
    
    try:
        commands_doc_path.write_text(commands_doc_content, encoding='utf-8')
        print("   ✓ 创建文档: docs/FRED_COMMANDS.md")
    except Exception as e:
        print(f"   ⚠ 创建文档失败: {e}")


def print_database_setup_instructions(project_root):
    """
    输出数据库配置提示信息
    
    Args:
        project_root: 项目根目录路径
    """
    sql_dir = project_root / 'sql'
    config_file = project_root / 'config' / 'Config.py'
    
    # 检查 sql 目录是否存在
    if sql_dir.exists() and sql_dir.is_dir():
        sql_files = list(sql_dir.glob('*.sql'))
        if sql_files:
            print("\n" + "=" * 60)
            print("📋 数据库配置提示")
            print("=" * 60)
            print("\n请按照以下步骤配置数据库：")
            print("\n1. 安装 MySQL 数据库")
            print("   如果尚未安装 MySQL，请先安装 MySQL 数据库服务器")
            print("   下载地址: https://dev.mysql.com/downloads/mysql/")
            
            print("\n2. 创建数据库")
            print("   使用 MySQL 客户端创建数据库，例如：")
            print("   CREATE DATABASE your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            
            print("\n3. 运行 SQL 文件")
            print(f"   SQL 文件位置: {sql_dir}")
            for sql_file in sql_files:
                print(f"   - {sql_file.name}")
            print("\n   执行方式（任选一种）：")
            print("   方式1: 使用 MySQL 命令行")
            print(f"          mysql -u root -p your_database_name < {sql_dir / sql_files[0].name}")
            print("   方式2: 使用 MySQL 客户端工具（如 Navicat、DBeaver 等）")
            print(f"         打开并执行 {sql_dir / sql_files[0].name} 文件")
            
            print("\n4. 修改配置文件")
            if config_file.exists():
                print(f"   编辑配置文件: {config_file}")
                print("   修改 SQLALCHEMY_DATABASE_URI 配置项，例如：")
                print("   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@127.0.0.1:3306/your_database_name'")
            else:
                print(f"   配置文件不存在: {config_file}")
            
            print("\n" + "=" * 60)
            print()


def install_frontend_dependencies(project_root):
    """
    检查并安装前端依赖
    1. 检查 frontend 目录是否存在
    2. 检查 Node.js 是否已安装
    3. 如果已安装，执行 pnpm install 命令
    
    Args:
        project_root: 项目根目录路径
    """
    frontend_dir = project_root / 'frontend'
    
    # 检查 frontend 目录是否存在
    if not frontend_dir.exists() or not frontend_dir.is_dir():
        return
    
    # 检查 package.json 是否存在
    package_json = frontend_dir / 'package.json'
    if not package_json.exists():
        return
    
    print("\n正在检查前端环境...")
    
    # 检查 Node.js 是否已安装
    import subprocess
    
    try:
        # 检查 node 命令是否可用
        result = subprocess.run(
            ['node', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            node_version = result.stdout.strip()
            print(f"✓ 检测到 Node.js: {node_version}")
        else:
            print("⚠ 警告: 未检测到 Node.js，跳过前端依赖安装")
            print("  请先安装 Node.js: https://nodejs.org/")
            return
    except FileNotFoundError:
        print("⚠ 警告: 未检测到 Node.js，跳过前端依赖安装")
        print("  请先安装 Node.js: https://nodejs.org/")
        return
    except subprocess.TimeoutExpired:
        print("⚠ 警告: Node.js 检查超时，跳过前端依赖安装")
        return
    except Exception as e:
        print(f"⚠ 警告: 检查 Node.js 时出错: {e}，跳过前端依赖安装")
        return
    
    # 检查 pnpm 是否已安装
    install_command = None
    package_manager = None
    
    try:
        result = subprocess.run(
            ['pnpm', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            pnpm_version = result.stdout.strip()
            print(f"✓ 检测到 pnpm: {pnpm_version}")
            install_command = ['pnpm', 'install']
            package_manager = 'pnpm'
        else:
            print("⚠ 警告: 未检测到 pnpm，尝试使用 npm 安装...")
            install_command = ['npm', 'install']
            package_manager = 'npm'
    except FileNotFoundError:
        print("⚠ 警告: 未检测到 pnpm，尝试使用 npm 安装...")
        install_command = ['npm', 'install']
        package_manager = 'npm'
    except subprocess.TimeoutExpired:
        print("⚠ 警告: pnpm 检查超时，尝试使用 npm 安装...")
        install_command = ['npm', 'install']
        package_manager = 'npm'
    except Exception as e:
        print(f"⚠ 警告: 检查 pnpm 时出错: {e}，尝试使用 npm 安装...")
        install_command = ['npm', 'install']
        package_manager = 'npm'
    
    # 如果仍然没有确定包管理器，使用 npm 作为后备
    if install_command is None or package_manager is None:
        install_command = ['npm', 'install']
        package_manager = 'npm'
    
    # 执行安装命令
    print(f"\n正在使用 {package_manager} 安装前端依赖...")
    print(f"工作目录: {frontend_dir}")
    
    try:
        # 切换到 frontend 目录并执行安装命令
        result = subprocess.run(
            install_command,
            cwd=str(frontend_dir),
            check=False,  # 不抛出异常，手动处理错误
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print(f"✓ 前端依赖安装成功")
        else:
            print(f"⚠ 警告: 前端依赖安装失败，退出码: {result.returncode}")
            print(f"  请手动进入 frontend 目录执行: {package_manager} install")
    except subprocess.TimeoutExpired:
        print("⚠ 警告: 前端依赖安装超时（超过5分钟）")
        print(f"  请手动进入 frontend 目录执行: {package_manager} install")
    except Exception as e:
        print(f"⚠ 警告: 执行前端依赖安装时出错: {e}")
        print(f"  请手动进入 frontend 目录执行: {package_manager} install")


def main():
    """
    命令行入口函数，用于初始化项目目录和文件
    使用运行命令时的当前工作目录作为项目根目录
    如果提供了模块名，会在初始化完成后自动创建该模块
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='初始化 fred_framework 项目目录和文件，并可选择创建第一个模块',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  fred-init                    # 在当前目录初始化项目
  fred-init user               # 初始化项目并创建名为 user 的模块（默认包含 frontend）
  fred-init user_management    # 初始化项目并创建名为 user_management 的模块（默认包含 frontend）
  fred-init user --no-frontend # 初始化项目并创建名为 user 的模块（不包含 frontend）
        '''
    )
    
    parser.add_argument(
        'module_name',
        type=str,
        nargs='?',
        default=None,
        help='可选：模块名称（只能包含字母、数字和下划线）。如果提供，将在初始化完成后自动创建该模块'
    )
    
    parser.add_argument(
        '--no-frontend',
        action='store_true',
        default=False,
        help='创建模块时不包含 frontend 目录（仅在提供模块名时有效，默认包含 frontend）'
    )
    
    args = parser.parse_args()
    
    # 执行初始化（使用当前工作目录作为项目根目录）
    try:
        create_project_directories()
        
        # 如果提供了模块名，在初始化完成后自动创建模块
        if args.module_name:
            print("\n" + "=" * 60)
            print("📦 创建业务模块")
            print("=" * 60 + "\n")
            from fred_framework.create_module import create_module_structure
            project_root = Path.cwd().resolve()
            
            # 预检查：验证模块名是否合法
            module_name = args.module_name.lower()
            if not module_name or not module_name.replace('_', '').isalnum():
                print(f"错误：模块名 '{args.module_name}' 不合法，只能包含字母、数字和下划线", file=sys.stderr)
                sys.exit(1)
            
            # 预检查：检查模块是否已存在
            module_dir = project_root / module_name
            if module_dir.exists():
                print(f"错误：模块 '{args.module_name}' 已存在", file=sys.stderr)
                sys.exit(1)
            
            # 默认包含 frontend，除非指定了 --no-frontend
            include_frontend = not args.no_frontend
            
            try:
                create_module_structure(module_name, project_root, include_frontend=include_frontend)
                print(f"\n✅ 模块 '{args.module_name}' 创建成功")
            except SystemExit:
                # create_module_structure 在出错时会调用 sys.exit(1)
                # 我们需要捕获这个异常并给出更友好的错误信息
                print(f"错误：创建模块 '{args.module_name}' 失败", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"错误：创建模块 '{args.module_name}' 失败: {e}", file=sys.stderr)
                sys.exit(1)
        
        # 初始化完成后，检查并安装前端依赖
        project_root = Path.cwd().resolve()
        
        print("\n" + "=" * 60)
        print("🌐 前端依赖安装")
        print("=" * 60)
        install_frontend_dependencies(project_root)
        
        # 输出数据库配置提示信息
        print_database_setup_instructions(project_root)
        
        # 输出默认管理账户信息
        print("\n" + "=" * 60)
        print("🔑 默认管理账户")
        print("=" * 60)
        print("\n请使用以下账户登录系统：")
        print("   用户名: admin")
        print("   密码:   Fic@2025")
        print("\n⚠️  重要提示: 请在首次登录后立即修改默认密码！")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"错误：初始化失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

