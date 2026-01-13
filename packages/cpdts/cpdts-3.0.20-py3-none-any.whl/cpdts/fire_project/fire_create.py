
from pathlib import Path
from ..utils.genfile import create_file_with_path
import re
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter
from prompt_toolkit.validation import Validator, ValidationError


class ProjectNameValidator(Validator):
    """验证Python项目名称是否合法"""
    def validate(self, document):
        text = document.text.strip()
        if not text:
            raise ValidationError(
                message='项目名称不能为空',
                cursor_position=len(document.text)
            )
        # 检查是否符合Python包命名规范（PEP 8）：只能包含小写字母、数字和下划线，且不能以数字开头
        if not re.match(r'^[a-z_][a-z0-9_]*$', text):
            raise ValidationError(
                message='项目名称只能包含小写字母、数字和下划线，且不能以数字开头',
                cursor_position=len(document.text)
            )


class YesNoValidator(Validator):
    """验证输入是否为 yes/no 或 y/n"""
    def validate(self, document):
        text = document.text.lower().strip()
        if text not in ['yes', 'no', 'y', 'n']:
            raise ValidationError(
                message='请输入 yes/no 或 y/n',
                cursor_position=len(document.text)
            )


class PythonVersionValidator(Validator):
    """验证Python版本是否在支持的版本列表中"""
    def __init__(self, valid_versions):
        self.valid_versions = valid_versions
    
    def validate(self, document):
        text = document.text.strip()
        if not text:
            raise ValidationError(
                message='Python版本不能为空',
                cursor_position=len(document.text)
            )
        if text not in self.valid_versions:
            raise ValidationError(
                message=f'请选择有效的Python版本: {", ".join(self.valid_versions)}',
                cursor_position=len(document.text)
            )


def fire_create():
    """交互式创建 Python 项目
    
    引导用户输入项目名称、Python 版本，可选进行 PyPI 名称冲突检查，
    然后根据模板生成项目文件结构。
    """
    project_name = prompt(
        "请输入Python项目名称: ",
        validator=ProjectNameValidator(),
        validate_while_typing=False
    ).strip()
    
    # 检查  当前目录下 {project_name} 目录是否已经存在
    # 如果存在则 询问用户是否继续创建 
    project_path = Path.cwd() / project_name
    if project_path.exists():
        print(f"警告: 目录 '{project_name}' 已经存在")
        yes_no_completer = FuzzyCompleter(
            WordCompleter(['yes', 'no'], ignore_case=True)
        )
        continue_answer = prompt(
            "是否继续创建 (可能会覆盖现有文件) (yes/no): ",
            completer=yes_no_completer,
            validator=YesNoValidator(),
            validate_while_typing=False
        ).lower().strip()
        
        if continue_answer not in ['yes', 'y']:
            print("已取消创建项目")
            return

    # 使用 FuzzyCompleter 让用户选择 Python版本
    python_versions = ['3.8', '3.9', '3.10', '3.11', '3.12', '3.13', '3.14', '3.14t']
    python_version_completer = FuzzyCompleter(
        WordCompleter(python_versions, ignore_case=True)
    )
    python_version = prompt(
        "请选择Python版本 (支持模糊搜索TAB补全): ",
        completer=python_version_completer,
        validator=PythonVersionValidator(python_versions),
        validate_while_typing=False,
        default='3.13'
    ).strip()
    
    # 使用 prompt_toolkit 的 FuzzyCompleter 询问 yes/no
    yes_no_completer = FuzzyCompleter(
        WordCompleter(['yes', 'no'], ignore_case=True)
    )
    
    pypi_check_answer = prompt(
        "是否进行PYPI项目名称检查 (yes/no): ",
        completer=yes_no_completer,
        validator=YesNoValidator(),
        validate_while_typing=False
    ).lower().strip()
    
    pypi_name_check = pypi_check_answer in ['yes', 'y']
    # 如果用户同意检查项目名字冲突 则执行检查操作 直到通过为止 
    
    if pypi_name_check:
        try:
            while True: 
                if not check_pypi_package_name(project_name):
                    break 
                else:
                    print("包名已存在，请重新输入")
                    project_name = prompt(
                        "请输入项目名称: ",
                        validator=ProjectNameValidator(),
                        validate_while_typing=False
                    ).strip()
                    continue
        except :
            return
    
    creat_process(project_name,python_version)

def check_pypi_package_name(package_name: str) -> bool | None:
    """检查包名是否已存在于 PyPI
    
    Args:
        package_name: 要检查的包名
    
    Returns:
        True 表示包名已存在，False 表示可用，None 表示检查失败
    """
    import requests
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
        if response.status_code == 200:
            print("包名已存在，不可以使用")
            return True  # 包名已存在
        elif response.status_code == 404:
            print("包名不存在，可以正常使用")
            # print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            # 虽然能够检查到 包名是不是已经存在了 但是仍然无法判断这个包名能不能用 真的头痛

            return False  # 包名不存在，可以使用
        else:
            print(f"检查包名时出现异常状态码: {response.status_code}")
            return None  # 检查失败
    except requests.exceptions.RequestException as e:
        print(f"检查包名时网络请求失败: {e}")
        return None  # 检查失败



def get_template_dir_files(template_dir: str, target_dir: str) -> dict:
    """扫描模板目录，生成文件映射字典
    
    Args:
        template_dir: 模板目录相对路径 (相对于 fire_create.py 所在目录)
        target_dir: 目标目录相对路径 (相对于项目根目录)
    
    Returns:
        dict: 文件映射字典，key 为目标路径，value 为包含 template 的字典
    """
    current_dir = Path(__file__).parent
    template_path = current_dir / template_dir
    
    items = {}
    for file in template_path.glob("*.py"):
        target_file = f"{target_dir}/{file.name}"
        items[target_file] = {"template": f"{template_dir}/{file.name}"}
    
    return items


def creat_process(project_name: str, python_version: str):
    """根据模板创建项目文件结构
    
    Args:
        project_name: 项目名称
        python_version: Python 版本号
    """
    current_dir = Path(__file__).parent

    items = {
        ".vscode/settings.json":{
            "template": "templates/vscode/settings.json",
        },
        ".vscode/extensions.json":{
            "template": "templates/vscode/extensions.json",
        },
        ".vscode/launch.json":{
            "template": "templates/vscode/launch.json",
        },
        ".kiro/steering/main.md":{
            "template": "templates/kiro/main.md",
        },
        f"src/{project_name}/__init__.py":{
            "template": "templates/src/init.py",
        },
        f"src/{project_name}/__main__.py":{
            "template": "templates/src/__main__.py",
        },
        f"src/{project_name}/decorators/singleton.py":{
            "template": "templates/src/decorators/singleton.py",
        },
        "pyproject.toml":{
            "template": "templates/pyproject.toml.j2",
            "data": {
                "project_name": project_name,
                "python_version": python_version
            }
        },
        ".gitignore":{
            "template": "templates/.gitignore",
        },
        ".gitattributes":{
            "template": "templates/.gitattributes",
        },
        "README.md":{
            "template": "templates/README.md",
        }
    }

    # 批量添加 scripts 目录下的所有文件
    items.update(get_template_dir_files("templates/src/scripts", "src/scripts"))

    for item in items:
        template = items[item]["template"]
        data = items[item].get("data", {})
        create_file_with_path(f'{project_name}/{item}', f"{current_dir}/{template}", data)