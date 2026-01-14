import os
import json
import re
import argparse
import subprocess

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# 全局配置文件路径
config_file_path = "p4config.json"

server = Server("mcp_perforce")

# 解析命令行参数
def parse_arguments():
    parser = argparse.ArgumentParser(description='Perforce服务工具')
    parser.add_argument('--p4config', '-c', type=str, help='p4config.json配置文件的路径', default="p4config.json")
    return parser.parse_args()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="get-changelist-files-catalog",
            description="""
    Get the files catalog in a changelist
    
    获取变更列表中的文件目录，返回受影响的文件列表（已过滤二进制文件和配置的跳过扩展名）
    
    Args:
        changelist_id: Perforce 变更列表 ID (CL号)
    """,
            inputSchema={
                "type": "object",
                "properties": {"changelist_id": {"type": "integer", "description": "Perforce 变更列表 ID (CL号)"}},    
                "required": ["changelist_id"],
            },
        ),
        types.Tool(
            name="get-file-details",
            description="""
    Get the details of a file in a changelist
    
    获取变更列表中指定文件的详细差异信息
    
    根据 is_shelved 参数使用不同的 diff 策略:
    - Shelved (is_shelved=true): 使用 p4 diff2 file file@=<CL> 比较未提交的变更
    - Affected (is_shelved=false): 使用 p4 diff2 file#(rev-1) file#rev 比较已提交的变更
    
    Args:
        action: 文件操作类型 (add/edit/delete/integrate/branch)
        file_path: depot 文件路径
        revision: 文件版本号
        changelist_id: Perforce 变更列表 ID (CL号)
        is_shelved: 是否是 Shelved CL (未提交的 CL 为 true，已提交的 CL 为 false)
    """,
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "文件操作类型 (add/edit/delete/integrate/branch)"},
                    "file_path": {"type": "string", "description": "depot 文件路径"},
                    "revision": {"type": "integer", "description": "文件版本号"},
                    "changelist_id": {"type": "integer", "description": "Perforce 变更列表 ID (CL号)"},
                    "is_shelved": {"type": "boolean", "description": "是否是 Shelved CL (未提交的 CL 为 true，已提交的 CL 为 false)", "default": True}
                },
                "required": ["action", "file_path", "revision", "changelist_id", "is_shelved"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    处理工具执行请求。
    目前 cursor 只支持简单工具的调用 无法处理资源修改等其他功能
    """
    if name == "get-changelist-files-catalog":
        res = await get_changelist_files_catalog(arguments.get("changelist_id"))
        return [types.TextContent(type="text", text=res)]
    elif name == "get-file-details":
        res = await get_file_details(
            arguments.get("action"),
            arguments.get("file_path"),
            arguments.get("revision"),
            arguments.get("changelist_id"),
            arguments.get("is_shelved", True)
        )
        return [types.TextContent(type="text", text=res)]
    else:
        raise ValueError(f"Unknown tool: {name}")

# 获取变更列表文件目录
async def get_changelist_files_catalog(changelist_id: int) -> str:
    """
    获取变更列表中的文件目录
    
    自动检测 CL 类型:
    - Shelved files: 使用 p4 describe -s -S <CL号> 获取搁置的文件列表
    - Affected files: 使用 p4 describe -s <CL号> 获取已提交的文件列表
    
    Args:
        changelist_id: Perforce 变更列表 ID (CL号)
    """
    try:
        is_shelved = False
        describe_output = ""
        
        # 先尝试获取 Shelved files
        shelved_cmd = ["p4", "describe", "-s", "-S", str(changelist_id)]
        shelved_result = subprocess.run(
            shelved_cmd,
            capture_output=True,
            text=True,
            encoding=P4_ENCODING,
            errors='replace'
        )
        
        if shelved_result.returncode == 0 and "Shelved files" in shelved_result.stdout:
            # 是 Shelved CL
            is_shelved = True
            describe_output = shelved_result.stdout
        else:
            # 尝试获取 Affected files (已提交的 CL)
            affected_cmd = ["p4", "describe", "-s", str(changelist_id)]
            affected_result = subprocess.run(
                affected_cmd,
                capture_output=True,
                text=True,
                encoding=P4_ENCODING,
                errors='replace'
            )
            
            if affected_result.returncode != 0:
                return f"错误: p4 describe 命令执行失败\n{affected_result.stderr}"
            
            describe_output = affected_result.stdout
        
        # 解析文件列表 - 从 p4 describe 输出中提取文件路径
        # 输出格式类似:
        # ... //depot/path/file.go#1 edit
        # ... //depot/path/file2.go#2 add
        files = []
        lines = describe_output.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('... '):
                # 提取文件路径和操作类型
                # 格式: ... //depot/path/file.go#1 edit
                parts = line[4:].split('#')
                if len(parts) >= 2:
                    file_path = parts[0]
                    # 提取版本号和操作类型
                    rest = parts[1].split(' ')
                    revision = rest[0] if rest else ''
                    action = rest[1] if len(rest) > 1 else ''
                    files.append({
                        'path': file_path,
                        'revision': revision,
                        'action': action
                    })
        
        # 格式化输出
        skip_ext_str = ', '.join([f'*{ext}' for ext in SKIP_FILE_EXTENSIONS])
        cl_type = "Shelved (未提交)" if is_shelved else "Affected (已提交)"
        
        formatted_info = f"变更列表: {changelist_id}\n"
        formatted_info += f"CL 类型: {cl_type}\n"
        formatted_info += f"is_shelved: {is_shelved}\n"
        formatted_info += "=" * 60 + "\n\n"
        formatted_info += f"【CL描述信息】\n{describe_output}\n"
        formatted_info += "=" * 60 + "\n\n"
        
        if not files:
            formatted_info += "未找到变更文件\n"
            return formatted_info
        
        formatted_info += f"受影响的文件(已过滤二进制文件和 {skip_ext_str}):\n\n"
        
        # 添加文件列表
        for file_info in files:
            file_path = file_info['path']
            action = file_info['action']
            revision = file_info['revision']

            if should_skip_file(file_path):
                continue
            formatted_info += f"- {action} {file_path}#{revision}\n"
        
        return formatted_info
    
    except Exception as e:
        error_msg = f"获取变更列表文件目录时出错: {str(e)}"
        print(error_msg)
        return error_msg

# 获取每个文件的详细信息
async def get_file_details(action: str, file_path: str, revision: int, changelist_id: int, is_shelved: bool = True) -> str:
    """
    获取每个文件的详细信息
    
    使用 P4 原生命令获取文件差异，根据 is_shelved 参数使用不同策略:
    
    Shelved files (is_shelved=True, 未提交的 CL):
    - delete: 直接标记为已删除
    - add: 使用 p4 print -q file@=<CL> 获取完整内容
    - edit/integrate: 使用 p4 diff2 file file@=<CL> 获取差异
    
    Affected files (is_shelved=False, 已提交的 CL):
    - delete: 直接标记为已删除
    - add: 使用 p4 print -q file#rev 获取完整内容
    - edit/integrate: 使用 p4 diff2 file#(rev-1) file#rev 获取差异
    
    Args:
        action: 文件操作类型 (add/edit/delete/integrate/branch)
        file_path: depot 文件路径
        revision: 文件版本号
        changelist_id: Perforce 变更列表 ID (CL号)
        is_shelved: 是否是 Shelved CL (默认 True)
    """
    cl_type = "Shelved" if is_shelved else "Affected"
    formatted_info = f"---- {file_path}#{revision} ({action}) [{cl_type}] ----\n"
    
    # 跳过配置的文件扩展名
    if should_skip_file(file_path):
        formatted_info += "  [已跳过: 不需要审查的文件类型]\n\n"
        return formatted_info
    
    # 对于删除的文件，不获取差异
    if action == 'delete':
        formatted_info += "  [文件已删除]\n\n"
        return formatted_info
    
    # 对于新增的文件，使用 p4 print 获取文件内容
    if action == 'add':
        if is_shelved:
            # Shelved: p4 print -q file@=<CL>
            print_cmd = ["p4", "print", "-q", f"{file_path}@={changelist_id}"]
        else:
            # Affected: p4 print -q file#rev
            print_cmd = ["p4", "print", "-q", f"{file_path}#{revision}"]
        
        print_result = subprocess.run(
            print_cmd,
            capture_output=True,
            text=True,
            encoding=P4_ENCODING,
            errors='replace'
        )
        
        if print_result.returncode == 0:
            content = print_result.stdout
            # 检查是否是二进制文件
            if '\x00' in content or is_binary_content(content):
                formatted_info += "  [二进制文件]\n\n"
            else:
                lines = content.split('\n')
                formatted_info += f"  [新增文件，共 {len(lines)} 行]\n"
                # 显示文件内容（限制行数避免输出过长）
                max_lines = 500
                if len(lines) > max_lines:
                    formatted_info += f"  (仅显示前 {max_lines} 行)\n"
                    for line in lines[:max_lines]:
                        formatted_info += f"  + {line}\n"
                    formatted_info += f"  ... 省略 {len(lines) - max_lines} 行 ...\n"
                else:
                    for line in lines:
                        formatted_info += f"  + {line}\n"
        else:
            formatted_info += f"  [获取文件内容失败: {print_result.stderr}]\n"
        formatted_info += "\n"
        return formatted_info
    
    # 对于编辑的文件，使用 p4 diff2 获取差异
    if is_shelved:
        # Shelved: p4 diff2 file file@=<CL>
        diff2_cmd = ["p4", "diff2", file_path, f"{file_path}@={changelist_id}"]
    else:
        # Affected: p4 diff2 file#(rev-1) file#rev
        prev_revision = int(revision) - 1
        if prev_revision < 1:
            prev_revision = 1
        diff2_cmd = ["p4", "diff2", f"{file_path}#{prev_revision}", f"{file_path}#{revision}"]
    
    diff2_result = subprocess.run(
        diff2_cmd,
        capture_output=True,
        text=True,
        encoding=P4_ENCODING,
        errors='replace'
    )
    
    if diff2_result.returncode == 0 or diff2_result.stdout:
        diff_output = diff2_result.stdout
        if not diff_output.strip():
            formatted_info += "  [无差异]\n"
        elif '(binary)' in diff_output.lower() or 'binary' in diff_output.lower():
            formatted_info += "  [二进制文件]\n"
        else:
            # 解析并格式化差异输出
            formatted_info += format_diff2_output(diff_output)
    else:
        formatted_info += f"  [获取差异失败: {diff2_result.stderr}]\n"
    
    formatted_info += "\n"
    return formatted_info


def is_binary_content(content: str) -> bool:
    """检查内容是否为二进制"""
    # 检查是否包含大量非打印字符
    non_printable = sum(1 for c in content[:1000] if ord(c) < 32 and c not in '\n\r\t')
    return non_printable > len(content[:1000]) * 0.1


def should_skip_file(file_path: str) -> bool:
    """检查文件是否应该被跳过"""
    for ext in SKIP_FILE_EXTENSIONS:
        if file_path.endswith(ext):
            return True
    return False


def format_diff2_output(diff_output: str) -> str:
    """格式化 p4 diff2 的输出"""
    formatted = ""
    lines = diff_output.split('\n')
    
    for line in lines:
        if line.startswith('==== '):
            # 文件头信息
            formatted += f"  {line}\n"
        elif line.startswith('>'):
            # 新增的行
            formatted += f"  + {line[1:].strip()}\n"
        elif line.startswith('<'):
            # 删除的行
            formatted += f"  - {line[1:].strip()}\n"
        elif line.startswith('---'):
            # 分隔符
            formatted += f"  {line}\n"
        elif re.match(r'^\d+[acd]\d+', line):
            # 差异位置信息 (如: 10a11, 5c6, 8d9)
            formatted += f"  [{line}]\n"
        elif re.match(r'^\d+,\d+[acd]\d+', line):
            # 差异位置信息 (如: 10,12a15)
            formatted += f"  [{line}]\n"
        elif line.strip():
            formatted += f"  {line}\n"
    
    return formatted


# 跳过的文件扩展名列表（默认值）
SKIP_FILE_EXTENSIONS = ['.pb.go', '.cs']

# 全局 P4 编码配置
P4_ENCODING = 'utf-8'


def get_p4_encoding() -> str:
    """
    通过 p4 set 命令获取 P4CHARSET 配置，返回对应的 Python 编码
    
    P4CHARSET 到 Python 编码的映射:
    - cp936 -> gbk (简体中文)
    - utf8/utf-8 -> utf-8
    - eucjp -> euc-jp (日文)
    - shiftjis -> shift_jis (日文)
    - winansi -> cp1252 (Windows ANSI)
    - iso8859-1 -> iso-8859-1
    - auto/none/未设置 -> utf-8 (默认)
    
    Returns:
        Python 编码字符串
    """
    # P4CHARSET 到 Python 编码的映射
    charset_mapping = {
        'cp936': 'gbk',
        'utf8': 'utf-8',
        'utf-8': 'utf-8',
        'eucjp': 'euc-jp',
        'shiftjis': 'shift_jis',
        'winansi': 'cp1252',
        'iso8859-1': 'iso-8859-1',
        'auto': 'utf-8',
        'none': 'utf-8',
    }
    
    try:
        # 执行 p4 set 获取配置
        result = subprocess.run(
            ['p4', 'set'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            print(f"警告: p4 set 命令执行失败，使用默认编码 utf-8")
            return 'utf-8'
        
        # 解析 P4CHARSET=xxx
        # 输出格式: P4CHARSET=cp936 (set)
        output = result.stdout
        for line in output.split('\n'):
            if line.startswith('P4CHARSET='):
                # 提取编码值，格式: P4CHARSET=cp936 (set)
                charset_part = line.split('=')[1].strip()
                # 移除 (set) 或其他后缀
                charset = charset_part.split()[0].lower() if charset_part else ''
                
                if charset in charset_mapping:
                    encoding = charset_mapping[charset]
                    print(f"检测到 P4CHARSET={charset}，使用编码: {encoding}")
                    return encoding
                else:
                    print(f"未知的 P4CHARSET={charset}，使用默认编码 utf-8")
                    return 'utf-8'
        
        print("未找到 P4CHARSET 配置，使用默认编码 utf-8")
        return 'utf-8'
        
    except Exception as e:
        print(f"获取 P4 编码配置时出错: {e}，使用默认编码 utf-8")
        return 'utf-8'

# 从配置文件读取P4配置
def read_p4_config_file(config_path):
    """
    从配置文件读取配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    try:
        if not os.path.exists(config_path):
            print(f"配置文件不存在: {config_path}")
            return None
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return {
            'skip_file_extensions': config.get('skip_file_extensions')
        }
    except Exception as e:
        print(f"读取配置文件出错: {str(e)}")
        return None

# 初始化默认配置
def init_default_config():
    """初始化默认配置，包括跳过的文件扩展名和 P4 编码"""
    global SKIP_FILE_EXTENSIONS
    global P4_ENCODING
    global config_file_path
    
    # 初始化 P4 编码配置
    P4_ENCODING = get_p4_encoding()
    
    # 从配置文件读取跳过的文件扩展名
    if os.path.exists(config_file_path):
        file_config = read_p4_config_file(config_file_path)
        if file_config:
            # 读取跳过的文件扩展名配置
            skip_extensions = file_config.get('skip_file_extensions')
            if skip_extensions and isinstance(skip_extensions, list):
                SKIP_FILE_EXTENSIONS = skip_extensions
                print(f"已加载跳过文件扩展名配置: {SKIP_FILE_EXTENSIONS}")
    else:
        print(f"配置文件 {config_file_path} 不存在，使用默认配置")
        print(f"默认跳过的文件扩展名: {SKIP_FILE_EXTENSIONS}")


async def main():
    """MCP 服务器主入口"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置配置文件路径
    global config_file_path
    config_file_path = args.p4config
    print(f"使用配置文件: {config_file_path}")
    
    # 初始化默认配置
    init_default_config()

    # 运行 MCP 服务器
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )