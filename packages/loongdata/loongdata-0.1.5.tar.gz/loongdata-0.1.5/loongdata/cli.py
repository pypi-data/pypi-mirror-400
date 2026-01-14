import argparse
from .download import DownloadClient
import os
import asyncio

def main():
    parser = argparse.ArgumentParser(description="Loongdata Open Source Data Client")
    parser.add_argument("action", default="download", help="data action", choices=["download"])
    parser.add_argument("--dataset", required=True, help="Dataset id in loong data platform")
    parser.add_argument("--session", help="Loongdata download session")
    parser.add_argument("--output", help="Output directory", default='')
    parser.add_argument("--host", help="Loongdata server host",
                        default=os.getenv("LOONGDATA_HOST", "http://dojo-api.openloong.org.cn"))
    parser.add_argument("--max-worker", help="Max download worker threads", type=int, default=5)

    args = parser.parse_args()

    if args.action == "download":
        output_dir = args.output if args.output else f"./{args.dataset}"
        client = DownloadClient(args.host, args.max_worker)
        asyncio.run(client.download(args.dataset, args.session, output_dir))
