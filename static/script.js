// 短縮アドレスのコピー
async function copyToClipboard() {
  const copyText = document.getElementById('shortenedLinkField');
  try {
    await navigator.clipboard.writeText(copyText.value);
    alert('リンクがコピーされました');
  } catch (err) {
    console.error('Failed to copy text: ', err);
  }
}

document.getElementById("product_image").onload = function() {
  document.getElementById("downloadButton").classList.remove("hidden");
}


document.addEventListener("DOMContentLoaded", function() {
  /////////////////////////////////////////////////////
  // グラフのデータを設定
  const priceData = [
    { x: [], y: [], type: 'scatter', mode: 'lines' }
  ];

  // 動的アノテーションを追加
  const plotlyGraph = document.getElementById('plotlyGraph');
  const annotation = {
    xref: 'x',
    yref: 'y',
    ax: 0,
    ay: -20,
    bgcolor: 'rgba(255, 255, 255, 0.8)',
    arrowhead: 4,
    arrowsize: 1,
    arrowwidth: 2,
    arrowcolor: '#636363',
    showarrow: true,
  };

  plotlyGraph.addEventListener('plotly_hover', (data) => {
    const point = data.points[0];
    const price = point.y;

    annotation.x = point.x;
    annotation.y = point.y;
    annotation.text = `￥${price.toLocaleString()} 円`;

    console.log("Annotation text:", annotation.text);

    console.log('Relayout called');  // ここに追加
    Plotly.relayout('plotlyGraph', { annotations: [annotation] });
  });

  plotlyGraph.addEventListener('plotly_unhover', () => {
    Plotly.relayout('plotlyGraph', { annotations: [] });
  });


  /////////////////////////////////////////////////////
  // テキストエリアの消去
  document.getElementById('amazon_link').addEventListener('click', function() {
    if (this.getAttribute('data-first-click') === 'true') {
      this.value = '';
      this.setAttribute('data-first-click', 'false');
    }
  });

  document.getElementById("linkForm").addEventListener("submit", function(event) {
    event.preventDefault();

    let amazonLink = document.getElementById("amazon_link").value;

    ///////////////////////////////////////////////////////
    //fetch
    fetch('/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'amazon_link=' + encodeURIComponent(amazonLink)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("shortenedLinkField").value = data.shortened_link;
      
        // ASINを取得して画像のURLを生成
        const asinMatch = data.shortened_link.match(/\/dp\/([A-Z0-9]+)/);
        if(asinMatch) {
            const ASIN = asinMatch[1];
            const imgURL = `/get-image/${ASIN}`;
            document.getElementById("product_image").src = imgURL;

            const productImageElement = document.getElementById("product_image");
            productImageElement.style.display = 'block';

          // 商品名と商品概要と現在価格の取得
          fetch(`/get-details/${ASIN}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById("nameField").value = data.product_name;
                document.getElementById("aboutField").value = data.product_description;
                document.getElementById("priceField").value = data.product_price + "円";
              })
              .catch(error => {
                  console.error('Error fetching product details:', error);
                  //BeautifulSoupのエラー
                  //KeepaAPPIのエラー　どちらかわかるようにするか？
              });
          // 価格履歴データを取得
          fetch(`/price-history/${ASIN}`)
              .then(response => response.json())
              .then(data => {
            
                // Create date objects from the valid timestamps
                priceData[0].x = data.x.map(dateStr => new Date(dateStr));
                priceData[0].y = data.y;
            
                const timestamps = priceData[0].x.map(dateObj => dateObj.getTime());
            
                // Find min and max timestamps
                const minTimestamp = Math.min(...timestamps);
                const maxTimestamp = Math.max(...timestamps);
            
                // 文字列に変換
                const minDate = new Date(minTimestamp).toISOString();
                const maxDate = new Date(maxTimestamp).toISOString();
            
                // グラフのレイアウトを設定
                const layout = {
                  title: '価格推移',
                  annotations: [],
                  xaxis: {
                    title: '日付',
                    type: 'date',
                    tickformat: "%Y-%m",
                    range: [minDate, maxDate]
                  },
                  yaxis: {
                    title: '価格 (円)',
                    tickformat: ',.0f 円' // 追加分
                  },
                  width: 1000,
                  height: 400
                  // autosize: true, // 自動サイズ調整を有効にする
                  // responsive: true, // レスポンシブデザインを有効にする
                };

                priceData[0].line = {
                  shape: 'hv', // ステップグラフの形状を設定
                  color: 'green', // 線の色を設定
                  width: 2      // 線の太さを設定
                };
            
                // priceData[0].opacity = 1.0; // 透明度を設定 (0.0から1.0の範囲)
            
                priceData[0].fill = 'tozeroy';
                priceData[0].fillcolor = 'rgba(144, 206, 156, 0.3)';
            
                layout.xaxis.range = [minDate, maxDate];
                layout.yaxis.range = [Math.min(...data.y), Math.max(...data.y)];
            
                Plotly.newPlot('plotlyGraph', priceData, layout);
              });
        }
    });
  });
});
