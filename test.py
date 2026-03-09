<!DOCTYPE html>
<html>
<head>
<title>For You ❤️</title>
<style>
body{
text-align:center;
font-family:Arial;
background:#ffe6e6;
margin-top:100px;
}
button{
padding:10px 20px;
font-size:18px;
}
</style>
</head>

<body>

<h2>Do you love me? ❤️</h2>

<button onclick="showLove()">Yes</button>

<p id="msg"></p>

<script>
function showLove(){
document.getElementById("msg").innerHTML="I knew it! ❤️😊";
}
</script>

</body>
</html>