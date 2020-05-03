#!/usr/bin/env python3

import opml
import feedparser
import youtube_dl
import sys
import os
import argparse
from time import time, mktime, strptime
from datetime import datetime


def read_last(fname: str) -> float:
    with open(fname, "r") as f:
        return datetime.utcfromtimestamp(float(f.read()))


def write_last(fname: str):
    with open(fname, "w") as f:
        f.write(str(time()))


def init_last(fname: str):
    write_last(fname)
    print(f'initialized "{fname}" with current timestamp')


def download(fname_last: str, fname_opml: str):
    outline = opml.parse(fname_opml)

    ptime = read_last(fname_last)
    ftime = time()

    urls = [x.xmlUrl for x in outline[0]]

    videos = []
    for i in range(0, len(urls)):
        feed = feedparser.parse(urls[i])
        for j in range(0, len(feed["items"])):
            timef = feed["items"][j]["published_parsed"]
            dt = datetime.fromtimestamp(mktime(timef))
            if dt > ptime:
                videos.append(feed["items"][j]["link"])
        print(
            f"parsing... {i + 1}/{len(urls)} ({len(videos)})", end="\r",
        )

    print("\ndone")
    print(f"{len(videos)} new videos found")

    ydl_opts = {
        "ignoreerrors": True,
        "outtmpl": "%(uploader)s - %(title)s.%(ext)s",
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(videos)

    write_last(fname_last)


def main():
    parser = argparse.ArgumentParser(
        description="automatically download your newest youtube videos"
    )
    parser.add_argument(
        "timestamp", help="file in which to record the download timestamp"
    )
    parser.add_argument("subs", help="file containing the subscription_manager export")
    args = parser.parse_args()

    if not os.path.exists(args.timestamp):
        init_last(args.timestamp)

    download(args.timestamp, args.subs)


if __name__ == "__main__":
    main()
