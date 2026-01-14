import os

from .download import RichMultiThreadDownloader
from .stream import DatasetStreamClient

class DownloadClient:
    def __init__(self, host, max_workers=4):
        self.host = host
        self.max_workers = max_workers
        self.downloader = RichMultiThreadDownloader(max_workers=max_workers)

    async def download(self, dataset, session, output_dir):
        def download_item(bucket, obs_path, task_id, episode_id):
            filename = f'{episode_id}.h5'
            self.downloader.download_item(bucket, obs_path, output_dir, filename)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        await self.get_data_info(dataset, session, download_item)
        self.downloader.wait_finish()

    async def get_data_info(self, dataset, session, callback):
        async with DatasetStreamClient(self.host).connect() as client:
            async def process_data(data):
                bucket, task_id, episode_id = data.get('bucket'), data.get('taskId'), data.get('episodeId')
                obs_path = f'data-collector-svc/align/{task_id}/{episode_id}/{episode_id}.h5'
                callback(bucket, obs_path, task_id, episode_id)
            await client.stream_episode(
                dataset_id=dataset,
                session_id=session,
                callback=process_data
            )
