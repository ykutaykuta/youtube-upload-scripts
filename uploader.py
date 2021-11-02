import argparse
import json
import os

from selenium import webdriver
from selenium.webdriver.remote.file_detector import LocalFileDetector

import loggin
import upload

DATA_FILE = "data.json"
PLAYLIST_ID = "PLmBofFz16wfqSc8KNwBE81ExKed_c0EIZ"


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--cookies", help="File json store cookies for login", default="")
    argparser.add_argument("--file", help="Video file to upload", default="")
    argparser.add_argument("--title", help="Video title", default="Test Title")
    argparser.add_argument("--description", help="Video description", default="Test Description")

    ### Default refer to Film & Animation category ###
    argparser.add_argument("--category", default="1",
                           help="Numeric video category. " + "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    argparser.add_argument("--tags", help="Video tags, comma separated", default="")
    args = argparser.parse_args()

    if args.cookies == "":
        args.cookies = "cookies.json"
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        obj = json.loads(f.read())
        video_file = obj["video_file"]
        title_file = obj["title_file"]
        chapter_range = obj["chapter_range"]
        begin = chapter_range["begin"]
        gap = chapter_range["gap"]
    if args.file == "":
        args.file = video_file
    args.title = "Truyện audio: Toàn chức pháp sư ({} - {})".format(begin, begin + gap - 1)
    with open(title_file, "r", encoding="utf-8") as f:
        description = f.read()
    args.description = description

    if not os.path.exists(args.file):
        print("File '{} not exists".format(args.file))
        exit("Please specify a valid file using the --file=parameter.")

    if not os.path.exists(args.cookies):
        print("Cookies file '{} not exists".format(args.cookies))
        exit("Please specify a valid file using the --cookies=parameter.")

    driver = webdriver.Chrome()
    driver.set_window_size(1920, 1080)
    loggin.login_using_cookie_file(driver, args.cookies)
    driver.get("https://www.youtube.com")

    assert "YouTube" in driver.title

    try:
        loggin.confirm_logged_in(driver)
        driver.get("https://studio.youtube.com")
        assert "Channel dashboard" in driver.title
        driver.file_detector = LocalFileDetector()
        upload.upload_file(driver, args.file, args.title, args.description, PLAYLIST_ID, args.tags)
    except Exception as e:
        driver.close()
        print(f"Failed to upload video '{args.file}' with Exception '{e}'")
        return 1
    return 0


if __name__ == '__main__':
    exit(main())
