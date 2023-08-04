from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        amazon_link = request.form.get("amazon_link")
        shortened_link = shorten_amazon_link(amazon_link)
        return jsonify(shortened_link=shortened_link)
    


    return render_template("index.html")

##「dp以下の英数字（ASIN）」を「amazon.co.jp/dp/」の後ろにつけて返す
def shorten_amazon_link(url):
    # /dp/ パスのチェック
    dp_match = re.search('/dp/([A-Z0-9]+)', url)
    if dp_match:
        asin = dp_match.group(1)
        return "https://www.amazon.co.jp/dp/"+asin

    # /gp/product/ が含まれる商品もあるらしい（未確認） 少なそうなら消す予定
    gp_match = re.search('/gp/product/([A-Z0-9]+)', url)
    if gp_match:
        asin = gp_match.group(1)
        return "https://www.amazon.co.jp/dp/"+asin

    # 上記のいずれのパスもマッチしない場合
    return "amazon.co.jpの商品リンクではありません"

if __name__ == "__main__":
    app.run(debug=True, port=5001)
