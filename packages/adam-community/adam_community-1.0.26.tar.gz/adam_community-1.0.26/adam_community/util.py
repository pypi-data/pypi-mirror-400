import time
import urllib.request
import urllib.error
import json
import subprocess
import sys
import os
import select
import logging
import ssl
from functools import wraps
from subprocess import run, CalledProcessError
import time

logger = logging.getLogger(__name__)

ADAM_API_HOST = os.getenv('ADAM_API_HOST', 'https://sidereus-ai.com')
ADAM_API_TOKEN = os.getenv('ADAM_API_TOKEN')
ADAM_TASK_ID = os.getenv('ADAM_TASK_ID')
ADAM_USER_ID = os.getenv('ADAM_USER_ID')
CONDA_ENV = os.getenv('CONDA_ENV')
ADAM_TASK_DIR = os.getenv('ADAM_TASK_DIR')


def _build_akb_query_command(query: str, collection: str) -> str:
    """
    构建 akb 查询命令，包含目录存在性检查
    
    Args:
        query: 查询字符串
        collection: 知识库名称
        
    Returns:
        完整的 bash 命令字符串
    """
    collection_dir = f"/share/programs/akb/database/{collection}"
    
    return f"""if [ ! -d "{collection_dir}" ]; then
    echo "知识库目录不存在: {collection_dir}"
    exit 1
fi
akb simple-query \\
    -i {collection_dir}/{collection}.index \\
    -m /share/programs/BAAI/bge-m3 \\
    -p {collection_dir}/{collection}.parquet \\
    -l 5 \\
    -f json -q "{query}\""""


class RAG:
    """
    搜寻RAG知识

    :param str query: 需要运行的命令
    :param str collection: 搜寻的知识库名称。必须是下面之一："DSDP","MPNN","PySCF","RFdiffusion","gaussian","protenix","GPU4PySCF","MolecularDynamics","RDkit","OpenBabel"
    """

    def call(self, query: str, collection: str):
        cmd = _build_akb_query_command(query, collection)
        logger.info(f"搜索知识库 {collection}: {query}")
        
        try:
            result = run(cmd, shell='/bin/bash', check=True, text=True, capture_output=True)
        except CalledProcessError as e:
            logger.error(e.stderr.strip())
            return e.stderr.strip()

        try:
            parsed_data = json.loads(result.stdout)
            # 如果返回的是数组，直接使用
            if isinstance(parsed_data, list):
                return "\n".join(parsed_data)
            # 如果返回的是对象且包含 text 字段，使用 text 字段
            elif isinstance(parsed_data, dict) and "text" in parsed_data:
                text_array = parsed_data["text"]
                if isinstance(text_array, list):
                    return "\n".join(text_array)
                else:
                    return str(text_array)
            else:
                # 其他情况返回原始输出
                return result.stdout
        except Exception as e:
            logger.error(e)
            return result.stdout


def retry_on_exception(max_retries=3, delay=5):
    """
    重试装饰器，在发生异常时最多重试指定次数
    
    Args:
        max_retries: 最大重试次数
        delay: 重试间隔时间（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        continue
                    raise last_exception
            return None
        return wrapper
    return decorator


def _make_http_request(url, data, return_json=True):
    """
    通用的 HTTP POST 请求函数
    
    Args:
        url: 请求的 URL
        data: 请求数据（字典格式）
        return_json: 是否将响应解析为 JSON，False 则返回文本
    
    Returns:
        响应数据（JSON 或文本）
    """
    if not ADAM_API_TOKEN:
        raise ValueError("ADAM_API_TOKEN environment variable is not set")
    
    headers = {
        "Authorization": f"Bearer {ADAM_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        # 将请求数据转换为JSON字符串并编码
        json_data = json.dumps(data).encode('utf-8')
        
        # 创建请求对象
        req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')
        
        context = ssl._create_unverified_context()

        # 发送请求
        with urllib.request.urlopen(req, context=context) as response:
            # 检查响应状态码
            if response.status >= 400:
                raise Exception(f"HTTP错误: {response.status}")
            
            # 读取响应
            response_data = response.read().decode('utf-8')
            
            # 根据需要返回 JSON 或文本
            if return_json:
                return json.loads(response_data)
            else:
                return response_data
                
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP请求失败 - HTTP错误 {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"HTTP请求失败 - 网络错误: {str(e)}")
    except json.JSONDecodeError as e:
        if return_json:
            raise Exception(f"HTTP请求失败 - JSON解析错误: {str(e)}")
        else:
            raise Exception(f"HTTP请求失败 - 响应解码错误: {str(e)}")
    except Exception as e:
        raise Exception(f"HTTP请求失败: {str(e)}")


def messageSend(message):
    """
    发送消息给用户
    """
    if not ADAM_API_HOST:
        raise ValueError("ADAM_API_HOST environment variable is not set")
    if not ADAM_TASK_ID:
        raise ValueError("ADAM_TASK_ID environment variable is not set")

    url = f"{ADAM_API_HOST}/api/task/create_message"
    
    request_data = {
        "task_id": ADAM_TASK_ID,
        "message": message,
        "role": "tool"
    }

    try:
        return _make_http_request(url, request_data, return_json=True)
    except Exception as e:
        raise Exception(f"发送消息失败: {str(e)}")


@retry_on_exception(max_retries=3)
def knowledgeSearch(query_info, messages_prev, project_name, collection_name, max_messages=4):
    """
    知识库检索函数
    """
    if not collection_name:
        raise ValueError("collection_name 参数是必需的")

    try:
        # 使用本地RAG实现
        rag = RAG()
        result = rag.call(query_info, collection_name)

        # 构造返回格式，保持与原有API格式一致
        response_data = {
            "code": 0,
            "data": {
                "collection_name": collection_name,
                "count": 1,
                "result_list": [{
                    "chunk_id": 0,
                    "chunk_source": "document",
                    "chunk_title": result.split("\n")[0] if result else "",
                    "chunk_type": "text",
                    "content": result,
                    "doc_info": {
                        "create_time": 0,
                        "doc_id": "local_doc",
                        "doc_name": f"{collection_name}_knowledge",
                        "doc_type": "text",
                        "source": "local"
                    },
                    "score": 1.0
                }],
                "token_usage": {
                    "embedding_token_usage": {
                        "completion_tokens": 0,
                        "prompt_tokens": 0,
                        "total_tokens": 0
                    },
                    "rerank_token_usage": 0
                }
            },
            "message": "success",
            "request_id": "local_request"
        }

        return json.dumps(response_data, ensure_ascii=False)
    except Exception as e:
        error_response = {
            "code": 1,
            "message": f"知识库搜索失败: {str(e)}"
        }
        return json.dumps(error_response, ensure_ascii=False)


class DynamicObject:
    """
    动态对象类，用于处理 JSON 响应
    
    这个类可以动态地将字典转换为对象属性，支持嵌套的字典结构
    同时保持原始数据的访问能力
    """
    def __init__(self, data):
        self._raw_data = data
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    setattr(self, key, self._convert_value(value))
                else:
                    setattr(self, key, value)
    
    def _convert_value(self, value):
        """递归转换嵌套的数据结构"""
        if isinstance(value, dict):
            return DynamicObject(value)
        elif isinstance(value, list):
            return [self._convert_value(item) for item in value]
        return value
    
    def __getattr__(self, name):
        """处理未定义的属性访问"""
        return self._raw_data.get(name)
    
    def __getitem__(self, key):
        """支持字典式访问"""
        return self._raw_data.get(key)
    
    def __str__(self):
        """返回可读的字符串表示"""
        return f"DynamicObject({self._raw_data})"
    
    def __repr__(self):
        return self.__str__()
    
    def to_dict(self):
        """将对象转换回字典"""
        return self._raw_data


@retry_on_exception(max_retries=3)
def completionCreate(request_params):
    """
    创建 openai 的代理函数
    
    Returns:
        DynamicObject: 一个动态对象，可以像访问属性一样访问 API 响应的所有字段
    """
    if not ADAM_API_HOST:
        raise ValueError("ADAM_API_HOST environment variable is not set")

    url = f"{ADAM_API_HOST}/api/chat/completions"
    
    try:
        response = _make_http_request(url, request_params, return_json=True)
        return DynamicObject(response)
    except Exception as e:
        raise Exception(f"调用聊天补全接口失败: {str(e)}")

def runCmd(cmd):
    """
    执行命令，实时输出执行结果

    修复了原实现中可能存在的阻塞和内容丢失问题
    """
    if os.getenv("ADAM_OUTPUT_RAW"):
        return cmd

    process = subprocess.Popen(
        cmd,
        shell=True,
	executable='/bin/bash',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )

    try:
        # 使用 select 来同时监控 stdout 和 stderr，避免阻塞
        while True:
            # 检查进程是否已结束
            if process.poll() is not None:
                break

            # 使用 select 来检查是否有可读的数据
            rlist, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)

            for stream in rlist:
                line = stream.readline()
                if line:
                    if stream == process.stdout:
                        print(line.strip())
                    else:
                        print(line.strip(), file=sys.stderr)

        # 读取剩余的输出（如果有）
        for line in process.stdout:
            print(line.strip())
        for line in process.stderr:
            print(line.strip(), file=sys.stderr)

        # 检查返回码
        if process.returncode != 0:
            sys.exit(process.returncode)

        return process
    finally:
        # 确保所有文件描述符都被关闭
        process.stdout.close()
        process.stderr.close()

def markdown_color(content, color):
    return f'<span style="color: {color}">{content}</span>'

def markdown_terminal(content, conda_env="base", user="Adam", workdir=""):
    user = markdown_color(f"{user}@Adam", "green")
    workdir = markdown_color(f":~/{workdir}", "blue")
    return f'({conda_env}) {user}{workdir}$ {content}'


# ========== States Management ==========

class _StatesManager:
    """内部状态管理类"""
    _tool_name = "tool"

    def _get_states_file(self) -> str:
        """获取 states.json 文件路径"""
        # 1. 优先使用环境变量
        task_dir = ADAM_TASK_DIR
        if task_dir:
            return os.path.join(task_dir, ".slurm", "states.json")

        # 2. 尝试当前目录的 .slurm
        current_dir = os.getcwd()
        local_states = os.path.join(current_dir, ".slurm", "states.json")
        if os.path.exists(local_states):
            return local_states

        # 3. 在当前目录创建
        return local_states

    def _read(self) -> dict:
        """读取 states.json，保留所有来源的数据"""
        states_file = self._get_states_file()
        if not os.path.exists(states_file):
            return {
                "files": {"updated_at": None, "sources": {}},
                "states": {"source": None, "updated_at": None, "data": {}}
            }
        try:
            with open(states_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {
                "files": {"updated_at": None, "sources": {}},
                "states": {"source": None, "updated_at": None, "data": {}}
            }

    def _write(self, data: dict):
        """写入 states.json"""
        states_file = self._get_states_file()
        os.makedirs(os.path.dirname(states_file), exist_ok=True)
        with open(states_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _set_nested(self, data: dict, key: str, value):
        """设置嵌套值，支持 dot notation"""
        keys = key.split('.')
        current = data
        for k in keys[:-1]:
            current = current.setdefault(k, {})
        current[keys[-1]] = value

    def _get_nested(self, data: dict, key: str, default=None):
        """获取嵌套值，支持 dot notation"""
        keys = key.split('.')
        current = data
        for k in keys:
            if isinstance(current, dict):
                current = current.get(k)
            else:
                return default
            if current is None:
                return default
        return current

    def set(self, key: str, value):
        """
        设置状态

        特殊 key:
            "files" - 记录文件列表，会自动补充到 files.sources[tool_name]
            其他 - 记录到 states.data
        """
        data = self._read()

        if key == "files":
            data["files"]["sources"][self._tool_name] = {
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "items": value
            }
        else:
            self._set_nested(data["states"]["data"], key, value)

        self._write(data)

    def get(self, key: str):
        """
        获取状态

        Returns:
            状态值，不存在返回 None
        """
        data = self._read()

        if key == "files":
            # 合并所有来源的文件列表
            merged = {}
            for source, content in data["files"]["sources"].items():
                for item in content.get("items", []):
                    path = item.get("path")
                    if not path:
                        continue
                    mtime = item.get("mtime", 0)
                    if path not in merged or mtime > merged[path]["mtime"]:
                        merged[path] = item
            result = list(merged.values())
            # 按 mtime 降序排序
            result.sort(key=lambda x: x.get("mtime", 0), reverse=True)
            return result

        return self._get_nested(data["states"]["data"], key)

    def cleanup(self):
        """清理当前工具的所有记录"""
        data = self._read()
        data["files"]["sources"].pop(self._tool_name, None)
        self._write(data)

    def trackPath(self, path: str, max_items: int = 30):
        """
        追踪文件/目录，自动检测文件信息并记录

        Args:
            path: 文件或目录路径
            max_items: 最大记录数量，先进先出
        """
        if not os.path.exists(path):
            return

        # 检测文件信息
        try:
            is_dir = os.path.isdir(path)
            mtime = int(os.path.getmtime(path))
            # 从环境变量获取 task_dir
            task_dir = os.getenv('ADAM_TASK_DIR')
            if task_dir:
                rel_path = os.path.relpath(path, task_dir)
            else:
                rel_path = path
        except (OSError, ValueError):
            return

        # 获取当前文件列表
        data = self._read()
        source = self._tool_name
        items = data["files"]["sources"].get(source, {}).get("items", [])

        # 检查是否已存在相同路径，存在则移除（后面会加到末尾，保持最新追踪的在最后）
        items = [item for item in items if item.get("path") != rel_path]

        # 添加到末尾（最新的位置）
        items.append({"path": rel_path, "is_dir": is_dir, "mtime": mtime})

        # 先进先出，保留最多 max_items 条
        if len(items) > max_items:
            items = items[-max_items:]

        # 写回
        data["files"]["sources"][source] = {
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "items": items
        }
        self._write(data)


# 全局实例
_states = _StatesManager()


def setState(key: str, value):
    """设置状态"""
    return _states.set(key, value)


def getState(key: str):
    """获取状态"""
    return _states.get(key)


def trackPath(path: str, max_items: int = 30):
    """
    追踪文件/目录，自动检测文件信息并记录

    Args:
        path: 文件或目录路径
        max_items: 最大记录数量，先进先出，默认 30
    """
    return _states.trackPath(path, max_items)
