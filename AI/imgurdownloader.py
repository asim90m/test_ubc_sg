import sys
import os


def download(download_folder, imgur_link):
    # can't use f strings in Python 3.5
    print("Trying to download from {} to {}".format(imgur_link, download_folder))
    cmd = "gallery-dl -d {} -o 'filename={{num}}.{{ext}}' -o 'directory=' {}".format(download_folder, imgur_link)
    os.system(cmd)


if __name__ == "__main__":
    # just for testing this in isolation
    assert len(sys.argv) == 3, "Provide a folder and link"
    download(sys.argv[1], sys.argv[2])
