
soup_str="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<div class="yj jy" href="ssss">
    <div></div>
</div>
<div id="yj  jy"></div>
</body>
</html>
"""
from bs4 import BeautifulSoup

soup = BeautifulSoup(soup_str, "lxml")

print soup.find_all('body')[0].find_all('div',attrs={'class':None})[0]
r = soup.find_all('div')[0].get('href')
print r
