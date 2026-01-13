"""
静态资源下载工具
用于下载 CDN 资源到本地，避免网络依赖
"""
import os
import click
import urllib.request
from typing import Dict, List, Tuple


class AssetDownloader:
    """静态资源下载器"""
    
    def __init__(self, assets_dir: str, resources: Dict[str, str]):
        """
        初始化下载器
        
        Args:
            assets_dir: 资源保存目录路径
            resources: 资源映射 {文件名: CDN URL}
        """
        self.assets_dir = assets_dir
        self.resources = resources
    
    def ensure_assets_dir(self):
        """确保 assets 目录存在"""
        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)
    
    def check_missing_files(self) -> List[str]:
        """
        检查缺失的文件
        
        Returns:
            缺失文件名列表
        """
        missing_files = []
        for filename in self.resources.keys():
            file_path = os.path.join(self.assets_dir, filename)
            if not os.path.exists(file_path):
                missing_files.append(filename)
        return missing_files
    
    def download_file(self, filename: str, url: str) -> bool:
        """
        下载单个文件
        
        Args:
            filename: 文件名
            url: 下载 URL
            
        Returns:
            是否下载成功
        """
        try:
            click.echo(f"  Downloading {filename}...", nl=False)
            file_path = os.path.join(self.assets_dir, filename)
            urllib.request.urlretrieve(url, file_path)
            click.echo(" ✓")
            return True
        except Exception as e:
            click.echo(f" ✗ Failed: {e}")
            return False
    
    def download_missing(self, silent: bool = False) -> Tuple[int, int]:
        """
        下载所有缺失的文件
        
        Args:
            silent: 是否静默模式（不输出提示信息）
            
        Returns:
            (成功数量, 总数量)
        """
        self.ensure_assets_dir()
        missing_files = self.check_missing_files()
        
        if not missing_files:
            # 所有文件都存在
            return 0, 0
        
        if not silent:
            click.echo("\nFirst time running, downloading static resources...")
            click.echo("Please ensure network connection is available to download resources from CDN.\n")
        
        success_count = 0
        for filename in missing_files:
            url = self.resources[filename]
            if self.download_file(filename, url):
                success_count += 1
        
        if not silent:
            if success_count == len(missing_files):
                click.echo(f"\n✓ All static resources downloaded successfully ({success_count}/{len(missing_files)})")
            else:
                click.echo(f"\n⚠ Some static resources failed to download ({success_count}/{len(missing_files)})")
                click.echo("Some features may be limited, but the application can still run normally.")
        
        return success_count, len(missing_files)
    
    def get_file_path(self, filename: str) -> str:
        """
        获取文件的完整路径
        
        Args:
            filename: 文件名
            
        Returns:
            文件的绝对路径
        """
        return os.path.join(self.assets_dir, filename)
    
    def file_exists(self, filename: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            filename: 文件名
            
        Returns:
            文件是否存在
        """
        return os.path.exists(self.get_file_path(filename))


def create_web_assets_downloader(resources: Dict[str, str]) -> AssetDownloader:
    """
    创建 web 静态资源下载器（默认保存到 web/static/assets）
    
    Args:
        resources: 资源映射 {文件名: CDN URL}
        
    Returns:
        AssetDownloader 实例
    """
    # 计算 web/static/assets 目录路径
    current_file = os.path.abspath(__file__)
    utils_dir = os.path.dirname(current_file)
    fcbyk_dir = os.path.dirname(utils_dir)
    web_dir = os.path.join(fcbyk_dir, 'web')
    assets_dir = os.path.join(web_dir, 'static', 'assets')
    
    return AssetDownloader(assets_dir, resources)