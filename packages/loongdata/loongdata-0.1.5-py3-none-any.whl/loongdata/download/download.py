import asyncio
from asyncio import CancelledError

from obs import ObsClient
import os
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn
)
from rich.console import Console
from concurrent.futures import ThreadPoolExecutor
import threading

class LoongObsClient:
    def __init__(self, access_key_id='HPUATWPNH6CPOZKR2MCL',
                          secret_access_key='xWC2J5gdw53G9MHvjKeIUer22K0rEKqitRUroEfq',
                          server='http://obs.cn-east-3.myhuaweicloud.com'):
        self.obs_client = ObsClient(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            server=server
        )

    def list_objects(self, bucket_name, prefix=None, max_keys=1000, delimiter=None, marker=None):
        resp = self.obs_client.listObjects(bucket_name, prefix, max_keys=max_keys,
                                           delimiter=delimiter, marker=marker, encoding_type='url')

        result = []
        if resp.status < 300:
            for content in resp.body.contents:
                result.append({
                    'key': content.key,
                    'size': content.size,
                    'lastModified': content.lastModified,
                })
        return result

    def download_file(self, bucket_name, object_key, local_file_path, callback=None):
        resp = self.obs_client.getObject(bucket_name, object_key, downloadPath=local_file_path, progressCallback=callback)
        return resp.status < 300

class RichMultiThreadDownloader:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.futures = []
        self.lock = threading.Lock()
        self.console = Console()
        self.client = LoongObsClient()

        # 创建进度显示
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=self.console
        )

    def download_with_progress(self, bucket_name, url, filename, save_dir="."):
        """使用rich进度条下载文件"""
        tmp_path = os.path.join(save_dir, filename + '.tmp')
        save_path = os.path.join(save_dir, filename)

        with self.progress:
            task_id = self.progress.add_task(
                f"[cyan]Download {filename}",
                filename=filename,
                start=True
            )
            if os.path.exists(save_path):
                total = os.path.getsize(save_path)
                self.progress.update(task_id, completed=total, total=total)
                return filename, True
            def _progress_callback(bytes_transferred, bytes_total, seconds):
                self.progress.update(task_id, completed=bytes_transferred, total=bytes_total)
            self.client.download_file(bucket_name, url, tmp_path, _progress_callback)

        os.rename(tmp_path, save_path)
        return filename, True

    def download_all(self, bucket_name, file_list, output_dir):
        """多线程下载所有文件"""
        tasks = {}

        with self.progress:
            # 为每个文件创建进度条任务
            for filename, url in file_list.items():
                task_id = self.progress.add_task(
                    f"[cyan]Download {filename}",
                    filename=filename,
                    start=False
                )
                tasks[filename] = (url, task_id)

            # 多线程下载
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for filename, (url, task_id) in tasks.items():
                    # 开始任务
                    self.progress.start_task(task_id)
                    # 提交下载任务
                    future = executor.submit(
                        self.download_with_progress,
                        bucket_name, url, filename, task_id, output_dir
                    )
                    futures.append((future, filename))

                # 收集结果
                results = []
                for future, filename in futures:
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        self.console.print(f"[red]✗ {filename} 下载失败: {e}")
                        results.append((filename, False))

        return results

    def download_item(self, bucket_name, obs_path, output_dir, filename):
        future = self.executor.submit(
            self.download_with_progress,
            bucket_name, obs_path, filename, output_dir
        )
        self.futures.append(future)

    def wait_finish(self):
        results = []
        for future in self.futures:
            try:
                result = future.result()
                results.append(result)
            except asyncio.CancelledError:
                print("[red]✗ Download interrupted by user")
            except Exception as e:
                self.console.print(f"[red]✗ 下载失败: {e}")
                results.append((None, False))
        return results
