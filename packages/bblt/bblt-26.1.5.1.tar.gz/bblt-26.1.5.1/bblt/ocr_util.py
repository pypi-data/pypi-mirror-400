import base64
import os
import sys
import requests
import json
from paddleocr import PaddleOCR

dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(dir)


class ocr:
    headers = {'Content-type': "application/json; charset=UTF-8", 'Accept': "application/json"}
    host = "http://10.136.52.51:9990"
    threshold = 0.7

    def __init__(self):
        file_dir = str(__file__).replace(str(__file__).split("/")[-1], "")

    def get_location(self, copy, result, note='contains', index=0):
        url = f'{self.host}/shdr/get_element_location_from_result'
        data = {"result": result, "copy": f"{copy}", "notes": note, "threshold": self.threshold}
        resp = json.loads(requests.post(url=url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), headers=self.headers).content)
        return resp['response'][index]

    def get_copy_list(self, result):
        copy_list=[]
        for item in result[0]:
            copy_list.append(item[-1][0])
        return copy_list

    def get_ocr_result_of_image(self, image):
        return PaddleOCR(use_angle_cls=True, lang="ch").ocr(image, cls=True)

    def img_to_base64(self, file_path: str):
        with open(file_path, 'rb') as f:
            img_data = base64.b64encode(f.read())
        self.img_data = img_data
        return img_data