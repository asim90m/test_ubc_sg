import requests
from bs4 import BeautifulSoup
import re
import os
import time


def rreplace(s, old, new, occurrence):
    """
    Replace, starting from the end
    """
    li = s.rsplit(old, occurrence)
    return new.join(li)


def download(download_folder, id):
    url = "https://nhentai.xxx/g/" + str(id)  # net has cloudflare
    try:
        response = requests.request("get", url)
        if response.status_code in (200,):
            response = response.content
        else:
            raise Exception(
                "Response not 200 from server. Note that this app uses nhentai.xxx instead of nhentai.net,"
                "because nhentai.net has cloudflare protection. Check if nhentai.xxx/g/{} exists.".format(
                    id
                )
            )
    except Exception as e:
        raise e
    html = BeautifulSoup(response, "html.parser")
    info = html.find("div", attrs={"id": "info"})
    if info is None:
        raise Exception(
            "This error probably indicates that nhentai.xxx/g/{} does not exist. DoujinCI"
            "uses nhentai.xxx instead of nhentai.net because .net has cloudflare bot protection"
            "which is really tricky to get around. You can try searching nhentai.xxx for the title"
            "to see if it has been uploaded under a different ID, upload it to nhentai.xxx yourself, or"
            "wait for someone else to upload it. You can also run this repository manually, which is hard.".format(
                id
            )
        )
    title = info.find("h1").text
    # cover = html.find('div', attrs={'id': 'cover'})
    # img_id = re.search('/galleries/([0-9]+)/cover.(jpg|png|gif)$', cover.a.img.attrs['src'])
    img_urls = []
    for i in html.find_all("div", attrs={"class": "thumb-container"}):
        img_src = i.img.attrs["data-src"]
        img_src_non_thumb = rreplace(img_src, "t", "", 1)
        img_urls.append(img_src_non_thumb)
    page_count = len(img_urls)
    print("Found comic {} with title: {}, Pages: {}".format(id, title, page_count))
    for url in img_urls:
        file_name = os.path.basename(url)
        response = requests.get(url)
        print("Status code: {}".format(response.status_code))
        img_data = response.content
        download_path = os.path.join(download_folder, file_name)
        with open(download_path, "wb") as f:
            f.write(img_data)
            print("Downloaded {} to {}".format(url, download_path))
            time.sleep(1)  # slow down to be kind idk
