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
    info = html.find("div", attrs={"class": "info"})
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
    num_pages = int(html.find("span", attrs={"class": "tag_name pages"}).text.split(" ")[0])

    img_urls = []
    image_link = html.find_all("img", attrs={"class": "lazy preloader"})[0]
    # replace last "t" to shift to non-thumbnail version
    img_url = rreplace(image_link["data-src"], "t", "", 1)
    # split by last / and replace with 1.png etc.
    base_url = "/".join(img_url.split("/")[0:-1])
    print("Found comic {} with title: {}, Pages: {}".format(id, title, num_pages))
    for i in range(1, num_pages + 1):
        file_name = "{}.jpg".format(i)
        url = base_url + "/" + file_name
        response = requests.get(url)
        status = response.status_code
        # if status is not 200, try .png
        if status != 200:
            file_name = "{}.png".format(i)
            url = base_url + "/" + file_name
            response = requests.get(url)
            status = response.status_code
            if status != 200:
                raise Exception("Not jpg or png detected, please create an issue at https://gitlab.com/ubcseagull/doujinci/-/issues because this I don't know what formats are used.")
        print("Status code: {}".format(status))
        img_data = response.content
        download_path = os.path.join(download_folder, file_name)
        with open(download_path, "wb") as f:
            f.write(img_data)
            print("Downloaded {} to {}".format(url, download_path))
            time.sleep(1)  # slow down to be kind idk


if __name__ == "__main__":
    os.mkdir("downloads")
    download("downloads", 238602)