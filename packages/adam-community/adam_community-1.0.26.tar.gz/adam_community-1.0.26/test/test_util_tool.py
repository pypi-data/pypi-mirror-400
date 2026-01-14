import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import sys
import os
import tempfile
import shutil
import json
import time

# 设置环境变量
os.environ['ADAM_API_TOKEN'] = 'test_token'
os.environ['ADAM_API_HOST'] = 'https://test.com'

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock OpenAI client before importing util
with patch('openai.OpenAI'):
    from adam_community.util import knowledgeSearch, completionCreate, runCmd, setState, getState, trackPath, RAG
    from adam_community.tool import Tool

class TestUtil(unittest.TestCase):
    def setUp(self):
        self.test_params = {
            "project": "test_project",
            "name": "test_collection",
            "query": "test query",
            "limit": 10
        }
        
    @patch('adam_community.util.RAG.call')
    def test_knowledgeSearch(self, mock_rag_call):
        """测试knowledgeSearch函数"""
        mock_rag_call.return_value = "test result content"

        result = knowledgeSearch(
            query_info="test query",
            messages_prev=[{"role": "user", "content": "test"}],
            project_name="test_project",
            collection_name="test_collection"
        )

        # 验证返回的是 JSON 格式
        import json
        data = json.loads(result)
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["collection_name"], "test_collection")
        mock_rag_call.assert_called_once_with("test query", "test_collection")

    @patch('subprocess.Popen')
    @patch.dict(os.environ, {'ADAM_OUTPUT_RAW': ''}, clear=True)
    def test_runCmd_success(self, mock_popen):
        """测试runCmd函数成功执行命令的情况"""
        mock_process = MagicMock()
        mock_process.poll.return_value = 0
        mock_process.returncode = 0
        mock_process.stdout.readline.return_value = "test output"
        mock_process.stderr.readline.return_value = ""
        mock_popen.return_value = mock_process
        
        process = runCmd('echo "test output"')
        self.assertEqual(process.returncode, 0)
        mock_popen.assert_called_once()

    @patch('subprocess.Popen')
    @patch.dict(os.environ, {'ADAM_OUTPUT_RAW': ''}, clear=True)
    def test_runCmd_failure(self, mock_popen):
        """测试runCmd函数执行失败的情况"""
        mock_process = MagicMock()
        mock_process.poll.return_value = 1
        mock_process.returncode = 1
        mock_process.stdout.readline.return_value = ""
        mock_process.stderr.readline.return_value = "command not found"
        mock_popen.return_value = mock_process
        
        with self.assertRaises(SystemExit) as cm:
            runCmd('nonexistent_command_123456')
        self.assertEqual(cm.exception.code, 1)

    @patch.dict(os.environ, {'ADAM_OUTPUT_RAW': 'true'}, clear=True)
    def test_runCmd_with_raw_output(self):
        """测试runCmd函数在ADAM_OUTPUT_RAW环境变量设置时的情况"""
        cmd = 'echo "test output"'
        result = runCmd(cmd)
        self.assertEqual(result, cmd)

class TestTool(unittest.TestCase):
    def setUp(self):
        class TestToolImpl(Tool):
            def call(self, kwargs):
                return "test command"
        
        self.tool = TestToolImpl()
        
    def test_inputShow(self):
        """测试inputShow方法"""
        kwargs = {
            "task_id": "test_task",
            "user": "test_user",
            "message": "test message"
        }
        
        with patch.object(self.tool, 'call', return_value="test command"):
            result = self.tool.inputShow(**kwargs)
            self.assertIn("test_user@Adam", result)
            self.assertIn("test_task", result)
        
    def test_resAlloc(self):
        """测试resAlloc方法"""
        kwargs = {
            "tool_data": "test_data",
            "tip": "test tip"
        }
        
        result = self.tool.resAlloc(kwargs)
        self.assertIn("CPU", result)
        self.assertIn("MEM_PER_CPU", result)
        self.assertIn("GPU", result)
        self.assertIn("PARTITION", result)
        
    def test_outputShow(self):
        """测试outputShow方法"""
        kwargs = {
            "stdout": "test stdout",
            "stderr": "test stderr",
            "exit_code": 0
        }
        
        result, files = self.tool.outputShow(kwargs)
        self.assertIn("test stdout", result)
        self.assertIn("test stderr", result)
        self.assertEqual(files, [])
        
    def test_markdown_color(self):
        """测试markdown_color静态方法"""
        result = Tool.markdown_color("test", "red")
        self.assertEqual(result, '<span style="color: red">test</span>')
        
    def test_markdown_terminal(self):
        """测试markdown_terminal静态方法"""
        result = Tool.markdown_terminal("test command", "test_env", "test_user", "test_dir")
        self.assertIn("test_user@Adam", result)
        self.assertIn("test_dir", result)
        self.assertIn("test command", result)


class TestStatesManager(unittest.TestCase):
    """测试 StatesManager 功能"""

    def setUp(self):
        """每个测试前创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # 重置 _states 的缓存
        from adam_community.util import _StatesManager
        _StatesManager._states_file = None

    def tearDown(self):
        """每个测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        # 重置 _states 的缓存
        from adam_community.util import _StatesManager
        _StatesManager._states_file = None

    def test_set_and_get_state(self):
        """测试设置和获取状态"""
        setState("stage", "data_cleaning")
        result = getState("stage")
        self.assertEqual(result, "data_cleaning")

    def test_set_nested_state(self):
        """测试设置嵌套状态"""
        setState("config.threshold", 0.5)
        result = getState("config.threshold")
        self.assertEqual(result, 0.5)

    def test_set_object_state(self):
        """测试设置对象状态"""
        data = {"stage": "analysis", "rows": 1000}
        setState("result", data)
        result = getState("result")
        self.assertEqual(result["stage"], "analysis")
        self.assertEqual(result["rows"], 1000)

    def test_get_nonexistent_state(self):
        """测试获取不存在的状态"""
        result = getState("nonexistent")
        self.assertIsNone(result)

    def test_set_files(self):
        """测试设置文件列表"""
        files = [
            {"path": "output/result.json", "is_dir": False, "mtime": 1704100800},
            {"path": "cache", "is_dir": True, "mtime": 1704100000}
        ]
        setState("files", files)

        # 验证文件写入
        states_file = os.path.join(self.temp_dir, ".slurm", "states.json")
        self.assertTrue(os.path.exists(states_file))

        with open(states_file, 'r') as f:
            data = json.load(f)
            self.assertIn("tool", data["files"]["sources"])
            self.assertEqual(len(data["files"]["sources"]["tool"]["items"]), 2)

    def test_get_files_merges_sources(self):
        """测试获取文件列表时合并多个来源"""
        # 先写入 server 的文件
        server_file = os.path.join(self.temp_dir, ".slurm", "states.json")
        os.makedirs(os.path.dirname(server_file), exist_ok=True)
        with open(server_file, 'w') as f:
            json.dump({
                "files": {
                    "updated_at": "2024-01-01T00:00:00Z",
                    "sources": {
                        "server": {
                            "updated_at": "2024-01-01T00:00:00Z",
                            "items": [
                                {"path": "src/main.py", "is_dir": False, "mtime": 1704100000}
                            ]
                        }
                    }
                },
                "states": {"source": None, "updated_at": None, "data": {}}
            }, f)

        # 写入 tool 的文件
        setState("files", [
            {"path": "output/result.json", "is_dir": False, "mtime": 1704100800}
        ])

        # 获取并验证合并
        files = getState("files")
        self.assertEqual(len(files), 2)
        paths = [f["path"] for f in files]
        self.assertIn("src/main.py", paths)
        self.assertIn("output/result.json", paths)

    def test_get_files_sorted_by_mtime(self):
        """测试文件列表按 mtime 降序排序"""
        setState("files", [
            {"path": "old.txt", "is_dir": False, "mtime": 1704100000},
            {"path": "new.txt", "is_dir": False, "mtime": 1704100800},
            {"path": "middle.txt", "is_dir": False, "mtime": 1704100400}
        ])

        files = getState("files")
        mtimes = [f["mtime"] for f in files]
        self.assertEqual(mtimes, sorted(mtimes, reverse=True))

    def test_preserve_existing_data(self):
        """测试写入时保留已有数据"""
        # 先写入 server 数据
        server_file = os.path.join(self.temp_dir, ".slurm", "states.json")
        os.makedirs(os.path.dirname(server_file), exist_ok=True)
        with open(server_file, 'w') as f:
            json.dump({
                "files": {
                    "updated_at": "2024-01-01T00:00:00Z",
                    "sources": {
                        "server": {
                            "updated_at": "2024-01-01T00:00:00Z",
                            "items": [{"path": "main.py", "is_dir": False, "mtime": 1704100000}]
                        }
                    }
                },
                "states": {
                    "source": "server",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "data": {"server_stage": "init"}
                }
            }, f)

        # 写入 tool 状态
        setState("stage", "processing")

        # 验证 server 数据保留
        with open(server_file, 'r') as f:
            data = json.load(f)
            self.assertIn("server", data["files"]["sources"])
            self.assertEqual(data["states"]["data"]["server_stage"], "init")
            self.assertEqual(data["states"]["data"]["stage"], "processing")

    def test_nonexistent_directory_creates_slurm(self):
        """测试不存在的目录会自动创建 .slurm"""
        os.chdir(self.original_cwd)  # 切回非临时目录
        test_dir = os.path.join(self.temp_dir, "new_task")
        os.makedirs(test_dir)
        os.chdir(test_dir)

        setState("stage", "test")
        states_file = os.path.join(test_dir, ".slurm", "states.json")
        self.assertTrue(os.path.exists(states_file))

    def test_trackPath_file(self):
        """测试追踪文件"""
        # 设置环境变量
        os.environ['ADAM_TASK_DIR'] = self.temp_dir

        try:
            # 创建测试文件
            test_file = os.path.join(self.temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test content")

            trackPath(test_file)

            files = getState("files")
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0]["path"], "test.txt")
            self.assertFalse(files[0]["is_dir"])
        finally:
            del os.environ['ADAM_TASK_DIR']

    def test_trackPath_directory(self):
        """测试追踪目录"""
        # 设置环境变量
        os.environ['ADAM_TASK_DIR'] = self.temp_dir

        try:
            # 创建测试目录
            test_dir = os.path.join(self.temp_dir, "output")
            os.makedirs(test_dir)

            trackPath(test_dir)

            files = getState("files")
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0]["path"], "output")
            self.assertTrue(files[0]["is_dir"])
        finally:
            del os.environ['ADAM_TASK_DIR']

    def test_trackPath_nonexistent(self):
        """测试追踪不存在的路径"""
        trackPath("/nonexistent/path/file.txt")
        files = getState("files")
        self.assertEqual(len(files), 0)

    def test_trackPath_updates_existing(self):
        """测试追踪已存在的文件会更新 mtime 并移动到末尾"""
        # 设置环境变量
        os.environ['ADAM_TASK_DIR'] = self.temp_dir

        try:
            # 先创建几个文件
            for name in ["a.txt", "b.txt", "file.txt"]:
                with open(os.path.join(self.temp_dir, name), 'w') as f:
                    f.write(name)

            # 追踪这些文件
            trackPath(os.path.join(self.temp_dir, "a.txt"))
            trackPath(os.path.join(self.temp_dir, "b.txt"))
            trackPath(os.path.join(self.temp_dir, "file.txt"))

            files = getState("files")
            self.assertEqual(len(files), 3)
            # file.txt 应该在最后（最新追踪的）
            self.assertEqual(files[2]["path"], "file.txt")

            # 再次追踪 file.txt，它应该移动到末尾
            time.sleep(0.1)  # 等待以确保 mtime 不同
            with open(os.path.join(self.temp_dir, "file.txt"), 'w') as f:
                f.write("v2")
            mtime2 = int(os.path.getmtime(os.path.join(self.temp_dir, "file.txt")))

            trackPath(os.path.join(self.temp_dir, "file.txt"))

            files = getState("files")
            self.assertEqual(len(files), 3)
            # file.txt 仍然在最后
            self.assertEqual(files[2]["path"], "file.txt")
            # mtime 已更新
            self.assertEqual(files[2]["mtime"], mtime2)
        finally:
            del os.environ['ADAM_TASK_DIR']

    def test_trackPath_max_items_fifo(self):
        """测试追踪超过最大数量时先进先出"""
        # 设置环境变量
        os.environ['ADAM_TASK_DIR'] = self.temp_dir

        try:
            # 创建 35 个文件
            for i in range(35):
                with open(os.path.join(self.temp_dir, f"file_{i}.txt"), 'w') as f:
                    f.write(str(i))

            # 追踪所有文件
            for i in range(35):
                trackPath(os.path.join(self.temp_dir, f"file_{i}.txt"))

            files = getState("files")
            # 应该保留 30 条（file_5 到 file_34）
            self.assertEqual(len(files), 30)

            # 检查最新追踪的文件是否保留
            filenames = [f["path"] for f in files]
            self.assertIn("file_34.txt", filenames)
            self.assertIn("file_5.txt", filenames)

            # 检查最早追踪的文件是否被移除
            self.assertNotIn("file_0.txt", filenames)
            self.assertNotIn("file_1.txt", filenames)
            self.assertNotIn("file_2.txt", filenames)
            self.assertNotIn("file_3.txt", filenames)
            self.assertNotIn("file_4.txt", filenames)
        finally:
            del os.environ['ADAM_TASK_DIR']

    def test_trackPath_with_task_dir_env(self):
        """测试追踪时使用环境变量的 task_dir"""
        # 设置环境变量
        os.environ['ADAM_TASK_DIR'] = self.temp_dir

        try:
            # 在子目录中创建文件
            sub_dir = os.path.join(self.temp_dir, "src")
            os.makedirs(sub_dir)
            test_file = os.path.join(sub_dir, "main.py")
            with open(test_file, 'w') as f:
                f.write("print('hello')")

            trackPath(test_file)

            files = getState("files")
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0]["path"], "src/main.py")
        finally:
            del os.environ['ADAM_TASK_DIR']


if __name__ == '__main__':
    unittest.main() 