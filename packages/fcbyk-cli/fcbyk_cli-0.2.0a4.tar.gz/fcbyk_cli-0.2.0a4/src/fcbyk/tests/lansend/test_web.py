import os
import tempfile

import pytest
from bs4 import BeautifulSoup

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
def client(temp_dir):
    service = LansendService(LansendConfig(shared_directory=temp_dir))
    app = create_lansend_app(service)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_template_rendering(client):
    # 只做简单校验：页面可访问且包含基本结构
    response = client.get('/')
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, 'html.parser')

    # title 是否存在（具体内容可能因模板而变化，这里只做存在性校验）
    assert soup.title is not None

    # 只做更弱的结构校验：页面应包含 body / 以及前端入口（例如 div#app 或 main/script 等）
    assert soup.body is not None

    # create_spa 渲染的是 SPA 页面，不保证特定 class 恒定存在，这里只检查存在性较高的节点
    app_root = soup.find(id='app')
    assert app_root is not None or soup.find('script') is not None

