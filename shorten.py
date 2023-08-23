from flask import Flask, render_template, jsonify, send_file, request
import keepa
import datetime
import plotly.graph_objs as go
import re
from bs4 import BeautifulSoup
import requests  
import io
import math
import os



app = Flask(__name__)

# アクセスキーを設定してKeepa APIを初期化
# access_key  = os.environ.get('API_KEY')
access_key  = '8b62i2uuu64uuipdqfc9psg1nsjc96hta8rq8tgc588rh4illke1l01074p0e0r5'


api = keepa.Keepa(access_key)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        amazon_link = request.form.get("amazon_link")
        shortened_link = shorten_amazon_link(amazon_link)
        return jsonify(shortened_link=shortened_link)
    return render_template("index.html")

@app.route('/get-image/<ASIN>')
def image_endpoint(ASIN):
    try:
        image_data = get_product_image(ASIN)
        if not image_data:
            return "Image data not found", 404

        # send_file関数を使用して画像データを直接返す
        return send_file(io.BytesIO(image_data), mimetype='image/jpeg')

    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return "Internal Server Error", 500


@app.route('/get-details/<ASIN>')
def get_details_endpoint(ASIN):
    try:
        product_name, product_description = get_product_details(ASIN)
        product_price = get_current_price(ASIN)

        if not product_name or not product_description or not product_price:
            return "Product details not found", 404
        
        return jsonify(product_name=product_name, product_description=product_description, product_price=product_price)
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return "Internal Server Error", 500


@app.route("/price-history/<ASIN>")
def price_history(ASIN):
    response = api.query(ASIN, domain='JP', stats=180, history=True, to_datetime=True)
    new_price_data = response[0]['data']['NEW']
    new_price_times = response[0]['data']['NEW_time']
    
    # 販売日と価格を結合
    price_history = list(zip(new_price_times, new_price_data))

    # NaN or -0.01 を除外
    price_history = [(date, price*100) for date, price in price_history if not isinstance(price, str) and price != -0.01 and price is not None and not (isinstance(price, float) and math.isnan(price))]

    # 日付と価格に分割
    dates, prices = zip(*price_history)

    # 最新の日付を取得
    latest_date = max(dates)

    # 最新の日から180日前の日付を取得
    days_ago = latest_date - datetime.timedelta(days=180)

    # 180日前からの価格データをフィルタリング
    filtered_dates = [date for date in dates if date >= days_ago]
    filtered_prices = prices[-len(filtered_dates):]

    data = {
        "x": filtered_dates,
        "y": filtered_prices
    }
    return jsonify(data)


####################################################################################
#Amazonの商品リンクを短縮
####################################################################################

def shorten_amazon_link(url):
    dp_match = re.search('/dp/([A-Z0-9]+)', url)
    if dp_match:
        ASIN = dp_match.group(1).upper()
        return "https://www.amazon.co.jp/dp/"+ASIN
    else:
        return "amazon.co.jpの商品リンクではありません"

####################################################################################
#商品画像の取得
####################################################################################

def get_product_image(ASIN):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.amazon.co.jp/dp/" + ASIN
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        app.logger.error(f"Failed to fetch Amazon page. HTTP status: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    element_with_id = soup.find(id="landingImage")

    if not element_with_id or not element_with_id.has_attr("src"):
        app.logger.error(f"Image element not found for ASIN {ASIN}")
        return None

    img_url = element_with_id["src"]
    response = requests.get(img_url)

    if response.status_code != 200:
        app.logger.error(f"Failed to fetch image. HTTP status: {response.status_code}")
        return None
    return response.content

####################################################################################
#商品名と商品概要、現在価格の取得
####################################################################################

def get_product_details(ASIN):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.amazon.co.jp/dp/" + ASIN
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        app.logger.error(f"Failed to fetch Amazon page. HTTP status: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    # 商品名を取得
    title_element = soup.find(id="productTitle")
    if not title_element:
        app.logger.error(f"Product title element not found for ASIN {ASIN}")
        return None
    product_name = title_element.text.strip()

    # 商品の概要を取得
    about_element = soup.find(id="feature-bullets")
    if not about_element:
        app.logger.error(f"Product description element not found for ASIN {ASIN}")
        return None
    product_description = " ".join(li.text.strip() for li in about_element.find_all("li"))

    return product_name, product_description

def get_current_price(ASIN):
    response = api.query(ASIN, domain='JP', history=True)
    new_price_data = response[0]['data']['NEW']

    # NaN or -0.01 を除外して最後の価格（現在の価格）を取得
    current_price = next((price * 100 for price in reversed(new_price_data) if not isinstance(price, str) and price != -0.01 and price is not None and not (isinstance(price, float) and math.isnan(price))), None)

    return current_price

####################################################################################
#Flaskアプリの起動
####################################################################################

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)