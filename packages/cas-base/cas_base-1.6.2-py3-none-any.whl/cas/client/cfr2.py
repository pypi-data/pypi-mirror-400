#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare R2 上传脚本
用于上传构建生成的压缩包到 Cloudflare R2 存储
"""

import os
import boto3
import mimetypes
from pathlib import Path
from typing import List
from datetime import datetime

class R2Config:
    """R2 配置类"""
    
    def __init__(self,app_name: str,app_version: str):
        # 从环境变量或配置文件获取 R2 配置
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.access_key_id = os.getenv('CLOUDFLARE_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('CLOUDFLARE_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('CLOUDFLARE_BUCKET_NAME')
        self.public_url = os.getenv('CLOUDFLARE_PUBLIC_URL')
        self.endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
        
        # 应用名称和版本
        self.app_name = app_name
        self.app_version = app_version
        
    def is_configured(self) -> bool:
        """检查 R2 配置是否完整"""
        return all([
            self.account_id,
            self.access_key_id,
            self.secret_access_key,
            self.bucket_name
        ])

class R2Uploader:
    """R2 上传器"""
    
    def __init__(self, config: R2Config):
        self.config = config
        self.s3_client = None
        self._init_client()
        
    def _init_client(self):
        """初始化 S3 客户端"""
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.config.endpoint_url,
                aws_access_key_id=self.config.access_key_id,
                aws_secret_access_key=self.config.secret_access_key,
                region_name='auto'
            )
        except Exception as e:
            print(f"初始化 R2 客户端失败: {e}")
            raise
            
    def upload_file(self, file_path: Path, object_key: str, progress_callback=None) -> bool:
        """上传单个文件到 R2"""
        try:
            if not file_path.exists():
                print(f"文件不存在: {file_path}")
                return False
                
            # 获取文件大小
            file_size = file_path.stat().st_size
            
            # 确定 MIME 类型
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = 'application/octet-stream'
                
            print(f"正在上传: {file_path.name} ({file_size / 1024 / 1024:.2f} MB)")
            
            # 上传文件
            with open(file_path, 'rb') as f:
                self.s3_client.put_object(
                    Bucket=self.config.bucket_name,
                    Key=object_key,
                    Body=f,
                    ContentType=content_type,
                    Metadata={
                        'upload-time': datetime.now().isoformat(),
                        'file-size': str(file_size),
                        'app-name': self.config.app_name,
                        'app-version': self.config.app_version
                    }
                )
                
            # 生成访问链接
            public_url = f"{self.config.public_url}/{object_key}"
            print(f"上传完成: {object_key}")
            print(f"访问链接: {public_url}")
            return True
            
        except Exception as e:
            print(f"上传失败: {e}")
            return False
            
    def generate_object_key(self, filename: str, build_type: str = 'full') -> str:
        """生成对象键（R2 中的文件路径）"""
        app_name = self.config.app_name
        version = self.config.app_version
        
        if build_type == 'full':
            # 完整包: app_name/app_name-v1.0.0.zip
            return f"{app_name}/{app_name}-v{version}.zip"
        else:
            # 更新包: app_name/app_name-v1.0.0_update.zip
            return f"{app_name}/{app_name}-v{version}_update.zip"
            
    def list_uploaded_files(self, prefix: str = '') -> List[dict]:
        """列出已上传的文件"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.config.bucket_name,
                Prefix=prefix,
                MaxKeys=100
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'etag': obj['ETag']
                    })
            return files
            
        except Exception as e:
            print(f"列出文件失败: {e}")
            return []

class BuildUploadManager:
    """构建上传管理器"""
    
    def __init__(self,app_name: str,app_version: str):
        self.config = R2Config(app_name,app_version)
        self.uploader = None
        if self.config.is_configured():
            self.uploader = R2Uploader(self.config)
            
    def get_dist_files(self) -> dict:
        """获取 dist 目录中的压缩包文件"""
        dist_dir = Path("dist")
        if not dist_dir.exists():
            print("dist 目录不存在，请先运行 build.py 进行构建")
            return {}
            
        files = {}
        
        # 查找完整包 (mt-sedie.zip)
        full_zip = dist_dir / f"{self.config.app_name}.zip"
        if full_zip.exists():
            files['full_package'] = full_zip
            
        # 查找更新包 (mt-sedie_update.zip)
        update_zip = dist_dir / f"{self.config.app_name}_update.zip"
        if update_zip.exists():
            files['update_package'] = update_zip
            
        return files
        
    def upload_all(self) -> bool:
        """上传所有可用的压缩包"""
        if not self.config.is_configured():
            print("R2 配置不完整，请设置以下环境变量:")
            print("  CLOUDFLARE_ACCOUNT_ID")
            print("  CLOUDFLARE_ACCESS_KEY_ID")
            print("  CLOUDFLARE_SECRET_ACCESS_KEY")
            print("  CLOUDFLARE_BUCKET_NAME (默认值为 download)")
            return False
            
        files = self.get_dist_files()
        if not files:
            print("没有找到可上传的压缩包文件")
            return False
            
        print(f"找到 {len(files)} 个文件需要上传")
        print("=" * 50)
        
        success_count = 0
        uploaded_urls = []  # 存储上传成功的文件URL
        
        # 上传完整包
        if 'full_package' in files:
            file_path = files['full_package']
            object_key = self.uploader.generate_object_key(
                file_path.name, 
                'full'
            )
            if self.uploader.upload_file(file_path, object_key):
                success_count += 1
                uploaded_urls.append(f"{self.config.public_url}/{object_key}")
            print()
            
        # 上传更新包
        if 'update_package' in files:
            file_path = files['update_package']
            object_key = self.uploader.generate_object_key(
                file_path.name, 
                'update'
            )
            if self.uploader.upload_file(file_path, object_key):
                success_count += 1
                uploaded_urls.append(f"{self.config.public_url}/{object_key}")
            print()
            
        print("=" * 50)
        print(f"上传完成: {success_count}/{len(files)} 个文件上传成功")
        
        # 显示所有上传成功的文件链接
        if uploaded_urls:
            print("\n文件访问链接:")
            for url in uploaded_urls:
                print(f"  {url}")
            
        return success_count == len(files)
        
    def upload_specific_file(self, file_path: str, build_type: str = 'full') -> bool:
        """上传指定的文件"""
        if not self.config.is_configured():
            print("R2 配置不完整")
            return False
            
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            return False
            
        object_key = self.uploader.generate_object_key(
            file_path.name, 
            build_type
        )
        
        return self.uploader.upload_file(file_path, object_key)

def show_banner():
    """显示程序横幅"""
    print("=" * 60)
    print("  Cloudflare R2 构建文件上传工具")
    print("=" * 60)
    print()

def show_menu():
    """显示交互式菜单"""
    print("\n可用命令:")
    print("  1. 上传所有构建文件 (完整包 + 更新包)")
    print("  2. 上传完整包")
    print("  3. 上传更新包")
    print("  4. 上传指定文件")
    print("  5. 列出已上传的文件")
    print("  6. 检查配置状态")
    print("  0. 退出")
    print()

def interactive_mode(manager: BuildUploadManager) -> bool:
    """交互式模式"""
    while True:
        show_menu()
        
        try:
            choice = input("请选择操作 (0-6): ").strip()
            
            if choice == '0':
                print("感谢使用，再见！")
                return True
                
            elif choice == '1':
                # 上传所有文件
                print("\n正在上传所有构建文件...")
                return manager.upload_all()
                
            elif choice == '2':
                # 只上传完整包
                files = manager.get_dist_files()
                if 'full_package' not in files:
                    print("未找到完整包文件")
                    continue
                    
                file_path = files['full_package']
                object_key = manager.uploader.generate_object_key(file_path.name, 'full')
                success = manager.uploader.upload_file(file_path, object_key)
                if success:
                    public_url = f"{manager.config.public_url}/{object_key}"
                continue
                
            elif choice == '3':
                # 只上传更新包
                files = manager.get_dist_files()
                if 'update_package' not in files:
                    print("未找到更新包文件")
                    continue
                    
                file_path = files['update_package']
                object_key = manager.uploader.generate_object_key(file_path.name, 'update')
                success = manager.uploader.upload_file(file_path, object_key)
                if success:
                    public_url = f"{manager.config.public_url}/{object_key}"
                continue
                
            elif choice == '4':
                # 上传指定文件
                file_path = input("请输入文件路径: ").strip()
                if not file_path:
                    print("文件路径不能为空")
                    continue
                    
                build_type = input("文件类型 (full/update) [默认: full]: ").strip() or 'full'
                success = manager.upload_specific_file(file_path, build_type)
                if success:
                    print("文件上传成功")
                continue
                
            elif choice == '5':
                # 列出已上传文件
                files = manager.uploader.list_uploaded_files(f"{manager.config.app_name}/") if manager.uploader else []
                if not files:
                    print("没有找到已上传的文件")
                else:
                    print("\n已上传的文件:")
                    for file in files:
                        public_url = f"{manager.config.public_url}/{file['key']}"
                        print(f"  - {file['key']} ({file['size'] / 1024 / 1024:.2f} MB)")
                        print(f"    链接: {public_url}")
                        print()
                continue
                
            elif choice == '6':
                # 检查配置状态
                print("\n配置状态:")
                print(f"  应用名称: {manager.config.app_name}")
                print(f"  应用版本: {manager.config.app_version}")
                print(f"  R2 配置: {'已配置' if manager.config.is_configured() else '未配置'}")
                
                if not manager.config.is_configured():
                    print("\n需要配置的环境变量:")
                    print("  CLOUDFLARE_ACCOUNT_ID")
                    print("  CLOUDFLARE_ACCESS_KEY_ID")
                    print("  CLOUDFLARE_SECRET_ACCESS_KEY")
                    print("  CLOUDFLARE_BUCKET_NAME (可选)")
                continue
                
            else:
                print("无效的选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n\n操作被取消，再见！")
            return False
        except Exception as e:
            print(f"发生错误: {e}")
            continue

def main(app_name: str, app_version: str):
    """主函数"""
    show_banner()
    return interactive_mode(BuildUploadManager(app_name, app_version))