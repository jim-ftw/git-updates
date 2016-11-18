import requests
import logging
import json
import os


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
        with open(path, 'wb') as handle:
            response = requests.get(u, stream=True)
            if not response.ok:
                logging.error('couldn\'t download file: ' + u)
            for block in response.iter_content(1024):
                handle.write(block)
        logging.info('added photo ' + str(img_number))
