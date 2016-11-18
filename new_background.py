import requests
import logging
import json
import os
import urllib
from PIL import ImageFile


def getsizes(uri):
    # get file size *and* image size (None if not known)
    file = urllib.urlopen(uri)
    size = file.headers.get("content-length")
    if size:
        size = int(size)
    p = ImageFile.Parser()
    while 1:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            return p.image.size[0]
            break
    file.close()
    return size, None


def add_background_img(bg_folder, img_number, lsphotos_json):
    with open(lsphotos_json, 'r') as f:
        js = json.loads(f.read())
    img = 'lsphotos/image' + str(img_number).zfill(6) + '.jpg'
    urls = []
    for item in js['images']:
        if img in item["media_file_path"]:
            urls.append(item['media_url'])
    path = os.path.join(bg_folder, str(img_number) + '.jpg')
    for u in urls:
        size = getsizes(u)
        if size > 999:
            with open(path, 'wb') as handle:
                response = requests.get(u, stream=True)
                if not response.ok:
                    logging.error('couldn\'t download file: ' + u)
                for block in response.iter_content(1024):
                    handle.write(block)
            logging.info('added photo ' + str(img_number))
        else:
            logging.info(str(img_number) + ' is too small (' + str(size) + ')')
