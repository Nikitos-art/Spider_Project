import requests
import wget

url = 'https://q-xx.bstatic.com/xdata/images/hotel/max500/114021095.jpg?k' \
      '=3fb7b6523a25a09ae1b5ecd953d7bb662f0dd68ccd2ec075c1b748c19ad14960&o= '

wget.download(url)

# response = requests.get(url)
#
# with open('batumi.jpg', 'wb') as f:
#     f.write(response.content)