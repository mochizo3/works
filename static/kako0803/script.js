document.getElementById("pasteAndSubmit").addEventListener("click", async function() {
  // クリップボードの内容を取得
  let clipboardText = await navigator.clipboard.readText();

  // テキストエリアにペースト
  document.getElementById("amazon-link").value = clipboardText;

  // フォームを送信
  document.getElementById("linkForm").submit();
});

//クリップボードにコピー
  const linkField = document.getElementById('shortenedLinkField');
    navigator.clipboard.writeText(linkField.value);
    alert('リンクをコピーしました！');

