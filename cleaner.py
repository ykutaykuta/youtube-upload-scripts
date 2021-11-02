import json
from pathlib import Path

DATA_FILE = "data.json"


def main():
    delete_lists = list()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        obj = json.loads(f.read())
        delete_lists.append(obj["video_file"])
        # delete_lists.append(obj["title_file"])
        delete_lists.append(obj["log_file"])
        text_files = obj["text_files"]
        for ele in text_files:
            delete_lists.append(ele)
        chapter_range = obj["chapter_range"]
        begin = chapter_range["begin"]
        gap = chapter_range["gap"]

    for ele in delete_lists:
        path = Path(ele)
        if path.exists():
            path.unlink()
            print("deleted file: {}".format(ele))

    obj["chapter_range"]["begin"] = begin + gap
    print("the next chapter: {}".format(obj["chapter_range"]["begin"]))
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, indent=4))


if __name__ == "__main__":
    main()
    exit(0)
