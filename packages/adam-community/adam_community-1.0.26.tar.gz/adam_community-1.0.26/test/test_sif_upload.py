import unittest
from unittest.mock import patch, MagicMock, call
from unittest.mock import mock_open
import tempfile
import shutil
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adam_community.cli.sif_build import (
    validateSifFile,
    validateImageUrl,
    checkCommandAvailable,
    checkDockerEnvironment,
    checkRequiredCommands,
    createWorkDir,
    calculateOptimalChunkSize,
    splitSifFile,
    generateDockerfile,
)


class TestValidateSifFile(unittest.TestCase):
    """测试 SIF 文件验证功能"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_sif_file(self):
        """测试有效的 SIF 文件"""
        # 创建测试文件
        test_file = Path(self.temp_dir) / "test.sif"
        test_file.write_text("test content")

        # 验证文件
        valid, error_msg = validateSifFile(test_file)

        # 断言
        self.assertTrue(valid)
        self.assertEqual(error_msg, "")

    def test_file_not_exists(self):
        """测试文件不存在"""
        test_file = Path(self.temp_dir) / "nonexistent.sif"

        valid, error_msg = validateSifFile(test_file)

        self.assertFalse(valid)
        self.assertIn("不存在", error_msg)

    def test_empty_file(self):
        """测试空文件"""
        test_file = Path(self.temp_dir) / "empty.sif"
        test_file.touch()

        valid, error_msg = validateSifFile(test_file)

        self.assertFalse(valid)
        self.assertIn("空", error_msg)


class TestValidateImageUrl(unittest.TestCase):
    """测试镜像 URL 验证功能"""

    def test_valid_urls(self):
        """测试有效的镜像 URL"""
        valid_urls = [
            "registry.example.com/namespace/image:1.0.0",
            "xxx.cn-hangzhou.cr.aliyuncs.com/openscore/openscore-core:1.0.0",
            "docker.io/library/ubuntu:20.04",
            "registry.com/org/image:latest",
            "127.0.0.1:5000/myimage:tag1"
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                valid, error_msg = validateImageUrl(url)
                self.assertTrue(valid, f"URL 应该有效: {url}")
                self.assertEqual(error_msg, "")

    def test_invalid_urls(self):
        """测试无效的镜像 URL"""
        invalid_urls = [
            "invalid-url",
            "registry.com/image",
            "registry.com/image:",
            "image:tag",
            ""
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                valid, error_msg = validateImageUrl(url)
                self.assertFalse(valid, f"URL 应该无效: {url}")
                self.assertIn("格式不正确", error_msg)


class TestCheckCommandAvailable(unittest.TestCase):
    """测试命令可用性检查"""

    def test_which_command_available(self):
        """测试 which 命令存在时"""
        # 在大多数系统上，ls 应该存在
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="/bin/ls\n"
            )

            valid, hint, url = checkCommandAvailable("ls")

            self.assertTrue(valid)
            self.assertEqual(hint, "")
            self.assertEqual(url, "")

    def test_command_not_found(self):
        """测试命令不存在"""
        with patch('subprocess.run') as mock_run:
            # 模拟 which 找不到命令
            mock_run.side_effect = FileNotFoundError("command not found")

            # 测试 split 命令提示
            valid, hint, url = checkCommandAvailable("nonexistent_cmd")

            self.assertFalse(valid)
            # 不在预定义列表中，返回通用提示
            self.assertIn("未找到", hint)


class TestCheckDockerEnvironment(unittest.TestCase):
    """测试 Docker 环境检查"""

    def test_docker_available_and_running(self):
        """测试 Docker 可用且正在运行"""
        with patch('subprocess.run') as mock_run:
            # which 找到 docker
            # docker info 成功
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout="/usr/bin/docker\n"),
                MagicMock(returncode=0, stdout="Docker is running\n")
            ]

            valid, errors = checkDockerEnvironment()

            self.assertTrue(valid)
            self.assertEqual(len(errors), 0)

    def test_docker_not_installed(self):
        """测试 Docker 未安装"""
        with patch('subprocess.run') as mock_run:
            # which 找不到 docker
            mock_run.side_effect = FileNotFoundError("docker not found")

            valid, errors = checkDockerEnvironment()

            self.assertFalse(valid)
            self.assertGreater(len(errors), 0)
            self.assertIn("Docker", errors[0])

    def test_docker_not_running(self):
        """测试 Docker 已安装但未运行"""
        with patch('subprocess.run') as mock_run:
            # which 找到 docker
            # 但 docker info 失败
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout="/usr/bin/docker\n"),
                MagicMock(returncode=1, stderr="Cannot connect to daemon\n")
            ]

            valid, errors = checkDockerEnvironment()

            self.assertFalse(valid)
            self.assertGreater(len(errors), 0)
            # 检查是否包含 daemon 提示
            error_text = "".join(errors)
            self.assertIn("daemon", error_text.lower())


class TestCheckRequiredCommands(unittest.TestCase):
    """测试所有必需命令检查"""

    def test_all_commands_available(self):
        """测试所有命令都可用"""
        with patch('adam_community.cli.sif_build.checkCommandAvailable') as mock_check:
            with patch('adam_community.cli.sif_build.checkDockerEnvironment') as mock_docker:
                # split 和 docker 都可用
                mock_check.return_value = (True, "", "")
                mock_docker.return_value = (True, [])

                valid, errors = checkRequiredCommands()

                self.assertTrue(valid)
                self.assertEqual(len(errors), 0)

    def test_split_missing(self):
        """测试 split 命令缺失"""
        with patch('adam_community.cli.sif_build.checkCommandAvailable') as mock_check:
            # split 不可用
            mock_check.side_effect = [
                (False, "split 命令未找到", "安装提示\nhttps://example.com"),
                (True, "", "")  # docker 可用
            ]

            valid, errors = checkRequiredCommands()

            self.assertFalse(valid)
            self.assertGreater(len(errors), 0)
            self.assertIn("split", errors[0])

    def test_docker_missing(self):
        """测试 Docker 缺失"""
        with patch('adam_community.cli.sif_build.checkCommandAvailable') as mock_check:
            # split 可用，docker 不可用
            mock_check.side_effect = [
                (True, "", ""),  # split 可用
                (False, "Docker 未安装", "安装 Docker\nhttps://docker.com")
            ]

            valid, errors = checkRequiredCommands()

            self.assertFalse(valid)
            self.assertGreater(len(errors), 0)


class TestCalculateOptimalChunkSize(unittest.TestCase):
    """测试自适应切片大小计算"""

    def test_no_chunking_small_file(self):
        """测试小文件不切片"""
        # 400MB
        result = calculateOptimalChunkSize(400 * 1024 * 1024)
        self.assertIsNone(result)

        # 499MB
        result = calculateOptimalChunkSize(499 * 1024 * 1024)
        self.assertIsNone(result)

    def test_100mb_chunking(self):
        """测试 100MB 切片"""
        # 500MB
        result = calculateOptimalChunkSize(500 * 1024 * 1024)
        self.assertEqual(result, "100M")

        # 1GB
        result = calculateOptimalChunkSize(1024 * 1024 * 1024)
        self.assertEqual(result, "100M")

        # 1.5GB
        result = calculateOptimalChunkSize(int(1.5 * 1024 * 1024 * 1024))
        self.assertEqual(result, "100M")

    def test_500mb_chunking(self):
        """测试 500MB 切片"""
        # 2GB
        result = calculateOptimalChunkSize(2 * 1024 * 1024 * 1024)
        self.assertEqual(result, "500M")

        # 5GB
        result = calculateOptimalChunkSize(5 * 1024 * 1024 * 1024)
        self.assertEqual(result, "500M")

        # 9.9GB
        result = calculateOptimalChunkSize(int(9.9 * 1024 * 1024 * 1024))
        self.assertEqual(result, "500M")

    def test_1gb_chunking(self):
        """测试 1GB 切片"""
        # 10GB
        result = calculateOptimalChunkSize(10 * 1024 * 1024 * 1024)
        self.assertEqual(result, "1G")

        # 20GB
        result = calculateOptimalChunkSize(20 * 1024 * 1024 * 1024)
        self.assertEqual(result, "1G")


class TestCreateWorkDir(unittest.TestCase):
    """测试工作目录创建"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_work_dir(self):
        """测试创建工作目录"""
        sif_path = Path(self.temp_dir) / "test.sif"
        sif_path.touch()

        work_dir = createWorkDir(sif_path)

        # 验证目录已创建
        self.assertTrue(work_dir.exists())
        self.assertTrue(work_dir.is_dir())

        # 验证目录名称
        self.assertEqual(work_dir.name, ".sif_build_temp")

        # 验证目录位置（在 SIF 文件同目录下）
        self.assertEqual(work_dir.parent, sif_path.parent)


class TestGenerateDockerfile(unittest.TestCase):
    """测试 Dockerfile 生成"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_dockerfile(self):
        """测试生成 Dockerfile"""
        work_dir = Path(self.temp_dir)

        dockerfile_path = generateDockerfile(work_dir)

        # 验证文件已创建
        self.assertTrue(dockerfile_path.exists())
        self.assertEqual(dockerfile_path.name, "Dockerfile")

        # 读取并验证内容
        with open(dockerfile_path, 'r') as f:
            content = f.read()

        self.assertIn("FROM alpine", content)
        self.assertIn("COPY . /sif", content)


class TestSplitSifFile(unittest.TestCase):
    """测试 SIF 文件切片"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # 创建测试 SIF 文件（10MB）
        self.sif_path = Path(self.temp_dir) / "test.sif"
        with open(self.sif_path, 'wb') as f:
            f.write(b'0' * (10 * 1024 * 1024))  # 10MB

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('subprocess.run')
    def test_split_with_chunk_size(self, mock_run):
        """测试带切片大小的切片"""
        work_dir = Path(self.temp_dir)

        # 模拟 split 命令成功
        mock_run.return_value = MagicMock(returncode=0)

        chunks = splitSifFile(self.sif_path, "100M", work_dir)

        # 验证调用了 split 命令
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], "split")
        self.assertIn("-b", cmd)
        self.assertIn("100M", cmd)
        self.assertIn("-d", cmd)

    def test_no_chunking(self):
        """测试不切片（chunk_size=None）"""
        # Create a separate work directory to avoid SameFileError
        work_dir = Path(self.temp_dir) / "work"
        work_dir.mkdir()

        chunks = splitSifFile(self.sif_path, None, work_dir)

        # 应该只有一个文件（原文件的副本）
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].name, "test.sif")
        self.assertTrue(chunks[0].exists())

        # 验证文件大小
        self.assertEqual(chunks[0].stat().st_size, 10 * 1024 * 1024)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_workflow_small_file(self):
        """测试小文件的完整工作流（不切片）"""
        # 1. 创建 SIF 文件
        sif_path = Path(self.temp_dir) / "test.sif"
        file_size = 5 * 1024 * 1024  # 5MB
        with open(sif_path, 'wb') as f:
            f.write(b'0' * file_size)

        # 2. 验证文件
        valid, error = validateSifFile(sif_path)
        self.assertTrue(valid, error)

        # 3. 计算切片大小（应该不切片）
        chunk_size = calculateOptimalChunkSize(file_size)
        self.assertIsNone(chunk_size)

        # 4. 创建工作目录
        work_dir = createWorkDir(sif_path)
        self.assertTrue(work_dir.exists())

        # 5. 切片文件（不切片）
        chunks = splitSifFile(sif_path, chunk_size, work_dir)
        self.assertEqual(len(chunks), 1)

        # 6. 生成 Dockerfile
        dockerfile_path = generateDockerfile(work_dir)
        self.assertTrue(dockerfile_path.exists())

        # 7. 验证 Dockerfile 内容
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        self.assertIn("FROM alpine", content)
        self.assertIn("COPY . /sif", content)

    def test_chunk_size_boundaries(self):
        """测试切片大小的边界值"""
        test_cases = [
            (499 * 1024 * 1024, None),  # 499MB -> 不切片
            (500 * 1024 * 1024, "100M"),  # 500MB -> 100M
            (2 * 1024 * 1024 * 1024, "500M"),  # 2GB -> 500M
            (10 * 1024 * 1024 * 1024, "1G"),  # 10GB -> 1G
        ]

        for file_size, expected_chunk in test_cases:
            with self.subTest(file_size=file_size):
                result = calculateOptimalChunkSize(file_size)
                self.assertEqual(result, expected_chunk)


if __name__ == '__main__':
    unittest.main()
