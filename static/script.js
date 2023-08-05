function copyToClipboard() {
  const linkField = document.getElementById('shortenedLinkField');
  navigator.clipboard.writeText(linkField.value);
  alert('リンクをコピーしました！');
}

document.getElementById("linkForm").addEventListener("submit", function(event) {
  event.preventDefault();
  
  let amazonLink = document.getElementById("amazon_link").value;
  
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
  });
});
