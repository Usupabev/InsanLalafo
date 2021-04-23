import requests
from bs4 import BeautifulSoup

data_list = []


def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1'
    }
    response = requests.get(url, headers=headers)
    return response.text


def parsing_istore(html):
    soup = BeautifulSoup(html, 'lxml')
    apple = soup.find('div', class_="h-100 container d-flex flex-wrap products-content").find_all('div', class_="col-lg-3 col-md-4 col-sm-6 col-12 mt-lg-4 mt-2 recommend-card d-flex flex-column p-4")
    for apples in apple:
        try:
            title = apples.find('div', class_="card-body bg-none text-center h-auto").find('h5').text.strip()
        except:
            title = ''

        try:
            photo = apples.find('a').find('img').get('src')
        except Exception as e:
            print(e)

        try:
            price = apples.find('p', class_="card-price-usd my-1").text.strip()
        except:
            price = ''

        data = {'title': title, 'photo': photo , 'price': price}
        data_list.append(data)

    return data_list


def parsing():
    url = 'https://istore.kg/catalog/iphone'
    data_list.clear()
    return parsing_istore(get_html(url))