<body>
<div id="iframe-container">
    <iframe id="iframe0" width="1920" height="1080" frameborder="0" style="display: none;"></iframe>
    <iframe id="iframe1" width="1920" height="1080" frameborder="0" style="display: none;"></iframe>
</div>
</body>
<script>
var ifrNo = 0;
var ifrHidden;
var ifr;
function reloadIFrame() {
    ifr = document.getElementById('iframe'+ifrNo);
    ifrNo = 1 - ifrNo;
    ifrHidden = document.getElementById('iframe'+ifrNo);
    ifr.onload = null;
    ifrHidden.onload = function() {
        ifr.style.display = 'none';
        ifrHidden.style.display = 'block';
    }
    ifrHidden.src = 'http://localhost:5000/snek';
}
reloadIFrame()
window.setInterval("reloadIFrame();", {});
</script>