import tkinter as tk
import re

def clicked():
    url = tf1.get()
    shortened_url = shorten_amazon_link(url)
    tf2.delete(0, tk.END)  # 出力フィールドの内容をクリア
    tf2.insert(0, shortened_url)  # 結果を出力フィールドに設定

#この関数のチェックをする
def shorten_amazon_link(url):
    dp_match = re.search('/dp/([A-Z0-9]+)', url)
    if dp_match:
        asin = dp_match.group(1)
        return "https://www.amazon.co.jp/dp/"+asin

    gp_match = re.search('/gp/product/([A-Z0-9]+)', url)
    if gp_match:
        asin = gp_match.group(1)
        return "https://www.amazon.co.jp/dp/"+asin

    return "amazon.co.jpの商品リンクではありません"

root = tk.Tk()
root.title("関数のチェック")
root.geometry("600x100")

#1
tf1 = tk.Entry(root, width=100)
tf1.grid(row=0, column=0)
btn = tk.Button(root, text = "短縮", command=clicked)
btn.grid(row=0, column=1)

#2
tf2 = tk.Entry(root, width=100)
tf2.grid(row=1, column=0)
lb1 = tk.Label(root, text="")
lb1.grid(row=1, column=1)

root.mainloop()
