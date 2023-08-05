import requests
from bs4 import BeautifulSoup
from PIL import Image
import io

def get_product_image(asin):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.amazon.co.jp/dp/" + asin
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    img_url = soup.find("img", attrs={"id": "landingImage"}).get("src")
    return img_url

# ASINを設定
asin = "B089K35LNX"  #仮
image_url = get_product_image(asin)

# 画像を取得
response = requests.get(image_url)

# BytesIOオブジェクトを作成
image_bytes = io.BytesIO(response.content)

# PILを使用して画像を開きます。
image = Image.open(image_bytes)

# 画像を表示します。
image.show()
