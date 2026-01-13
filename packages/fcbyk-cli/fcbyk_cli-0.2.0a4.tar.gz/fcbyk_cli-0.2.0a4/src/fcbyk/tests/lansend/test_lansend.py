import os
import tempfile
import pytest

from fcbyk.commands.lansend.service import LansendConfig, LansendService
from fcbyk.commands.lansend.controller import create_lansend_app


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        with open(os.path.join(temp_dir, 'test.txt'), 'w') as f:
            f.write('test content')
        yield temp_dir


@pytest.fixture
def lansend_service(temp_dir):
    config = LansendConfig(shared_directory=temp_dir)
    return LansendService(config)


@pytest.fixture
def client(lansend_service):
    app = create_lansend_app(lansend_service)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_safe_filename(lansend_service):
    assert lansend_service.safe_filename('test.txt') == 'test.txt'
    assert lansend_service.safe_filename('test*file.txt') == 'testfile.txt'
    assert lansend_service.safe_filename('测试 文件.txt') == '测试 文件.txt'


def test_format_size():
    assert LansendService.format_size(500) == "500 B"
    assert LansendService.format_size(2048) == "2.00 KB"
    assert LansendService.format_size(1572864) == "1.50 MB"
    assert LansendService.format_size(1610612736) == "1.50 GB"
    assert LansendService.format_size(None) == "unknown size"


def test_ensure_shared_directory(lansend_service, temp_dir):
    assert lansend_service.ensure_shared_directory() == temp_dir


def test_ensure_shared_directory_not_set():
    config = LansendConfig(shared_directory=None)
    service = LansendService(config)
    with pytest.raises(ValueError, match="shared directory not set"):
        service.ensure_shared_directory()


def test_abs_target_dir(lansend_service, temp_dir):
    # 先创建子目录，否则 abs_target_dir 可能返回不存在路径但本用例只是校验拼接与防逃逸
    os.makedirs(os.path.join(temp_dir, "subdir"), exist_ok=True)

    target = lansend_service.abs_target_dir("subdir")
    assert target == os.path.join(temp_dir, "subdir")

    # 测试路径遍历防护
    with pytest.raises(PermissionError):
        lansend_service.abs_target_dir("../outside")


def test_file_upload(client, temp_dir):
    # 测试文件上传（Flask test_client: 文件需放在 data 里，value 为 (fileobj, filename)）
    test_file_content = b"test upload content"

    from io import BytesIO

    data = {
        "path": "",
        "file": (BytesIO(test_file_content), "test_upload.txt"),
    }

    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert response.json["message"] == "file uploaded"

    uploaded_file = os.path.join(temp_dir, "test_upload.txt")
    assert os.path.exists(uploaded_file)
    with open(uploaded_file, "rb") as f:
        assert f.read() == test_file_content


def test_api_directory(client, temp_dir):
    response = client.get('/api/directory')
    assert response.status_code == 200
    data = response.json
    assert any(item["name"] == "test.txt" for item in data["items"])


def test_api_file(client, temp_dir):
    response = client.get('/api/file/test.txt')
    assert response.status_code == 200
    data = response.json
    assert data["content"] == "test content"
    assert data["name"] == "test.txt"


def test_api_download(client, temp_dir):
    response = client.get('/api/download/test.txt')
    assert response.status_code == 200
    assert response.data == b'test content'
    assert 'attachment' in response.headers.get('Content-Disposition', '')

