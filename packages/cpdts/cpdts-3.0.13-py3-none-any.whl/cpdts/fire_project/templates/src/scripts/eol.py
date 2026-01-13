"""切换文件的行尾符 (LF <-> CRLF)"""

import sys
from pathlib import Path


def detect_eol(content: bytes) -> str:
    """检测文件当前的行尾符类型"""
    if b"\r\n" in content:
        return "CRLF"
    elif b"\n" in content:
        return "LF"
    return "NONE"


def convert_eol(file_path: Path, target: str | None = None) -> None:
    """转换文件行尾符
    
    Args:
        file_path: 文件路径
        target: 目标格式 (LF/CRLF)，为空则自动切换
    """
    content = file_path.read_bytes()
    current = detect_eol(content)
    
    if current == "NONE":
        print(f"文件无换行符: {file_path}")
        return
    
    # 自动切换或指定目标
    if target is None:
        target = "LF" if current == "CRLF" else "CRLF"
    
    if current == target:
        print(f"已是 {target}: {file_path}")
        return
    
    # 执行转换
    if target == "LF":
        new_content = content.replace(b"\r\n", b"\n")
    else:
        # 先统一为 LF，再转 CRLF
        new_content = content.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    
    file_path.write_bytes(new_content)
    print(f"{current} -> {target}: {file_path}")


def batch_convert(directory: Path, target: str, extensions: set[str]) -> None:
    """批量转换目录下的文件"""
    for file_path in directory.rglob("*"):
        # 跳过目录、隐藏文件夹、常见忽略目录
        if file_path.is_dir():
            continue
        if any(p in ("__pycache__", "node_modules", ".venv", "dist", ".git") 
               for p in file_path.parts):
            continue
        if file_path.suffix.lower() not in extensions:
            continue
        
        try:
            convert_eol(file_path, target)
        except Exception as e:
            print(f"错误 {file_path}: {e}")


# 常见文本文件扩展名
TEXT_EXTENSIONS = {
    ".py", ".txt", ".md", ".json", ".yaml", ".yml", ".toml",
    ".js", ".ts", ".html", ".css", ".xml", ".sh", ".bat", ".ps1",
    ".gitignore", ".env", ".cfg", ".ini", ".lock"
}


def main():
    if len(sys.argv) < 2:
        print("用法: python eol.py <file|dir> [LF|CRLF]")
        print("  不指定目标格式则自动切换（单文件）或转为 LF（目录）")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"路径不存在: {path}")
        sys.exit(1)
    
    target = sys.argv[2].upper() if len(sys.argv) > 2 else None
    if target and target not in ("LF", "CRLF"):
        print(f"无效的目标格式: {target}，应为 LF 或 CRLF")
        sys.exit(1)
    
    if path.is_dir():
        batch_convert(path, target or "LF", TEXT_EXTENSIONS)
    else:
        convert_eol(path, target)


if __name__ == "__main__":
    main()
