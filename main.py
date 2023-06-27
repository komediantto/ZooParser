import datetime
from typing import List
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import aiohttp
import asyncio
import requests
import json
import pandas as pd
from tqdm import tqdm

HOME_URL = 'https://4lapy.ru/'
URL = 'https://4lapy.ru/catalog/koshki/korm-koshki/?section_id=2&sort=popular&page='

ua = UserAgent()

headers = {
    'authority': '4lapy.ru',
    'method': 'GET',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': 'PHPSESSID=ujkb2vc20c4fordp8680jivpa4; _gcl_au=1.1.1963394895.1687777043; rrpvid=647046516711006; _ym_uid=1687777043813840516; _ym_d=1687777043; _gid=GA1.2.929256931.1687777043; rcuid=64996f134363c3c2e29fe0d9; _ymab_param=q9hHpnI-Z_edXXdiYjzI-5Oms5t7eLhmHpna9QkDeBNBnLsNEJ5R1P0kxIdR-nRZTby99aQZujwneuXxEqsE9jX8CpU; flocktory-uuid=d78ab1b7-16bb-4830-b025-25b00654b125-2; __exponea_etc__=3b1497f8-464b-474d-8edd-cd5578b779e6; _gpVisits={"isFirstVisitDomain":true,"idContainer":"1000259C"}; adrdel=1; adrcid=AtXbsV1C_wOlEWXIK1YZUKg; cancel_mobile_app=0; testcookie=e0a5fe5fe86ada300005a1978e97b378493ad3f; BX_USER_ID=a5464cb55669de1f20a1b4787278a866; _ym_isad=2; _userGUID=0:ljcqvkk2:ARwx~ZMvpAWJdPnVrHWruQEzib5wxKZk; tmr_lvid=7793f8214741d5667d09be10a48d11fa; tmr_lvidTS=1687777049571; 4LP_product_subscribe=eBez0s4nspMXtzSOHXmfs71BIGazeAIE; user_geo_location=%5B%5D; 4LAPY_abtest=Y; DIGI_CARTID=96275532519; rrlevt=1687786673210; show_mobile_app=null; hide_mobile_app=1; __exponea_time2__=-0.11462926864624023; _ym_visorc=b; _gp1000259C={"hits":53,"vc":1,"ac":1,"a6":1,"a1":1}; _ga=GA1.2.764111291.1687777043; _ga_GRN90Z74D3=GS1.1.1687799892.2.1.1687799894.58.0.0; skipCache=0; dSesn=8bba192a-8530-5ea9-3d7b-7aed4291d01a; _dvs=0:ljd4hbge:qj7nMQHLbpiYoZ9MMsOMb4haOFu5FCIo; digi_uc=W1sidiIsIjQ0MzM1IiwxNjg3Nzk5ODk3MjQxXSxbInYiLCI0MTYxNCIsMTY4Nzc5MTkwOTI5NV0sWyJ2IiwiMTQ4NzEyIiwxNjg3NzkxODgzNTg3XSxbInYiLCI0NDMzOSIsMTY4Nzc5MTgxOTcwMl0sWyJ2IiwiNDE1MzAiLDE2ODc3ODY2ODkyNDNdLFsidiIsIjQ0MzA1IiwxNjg3Nzg2NjI5MzU0XSxbInYiLCI0NDM0NyIsMTY4Nzc4NjUxMDQ2NV0sWyJ2IiwiMTQ4MDUxIiwxNjg3NzgzNTYwNTA1XSxbInYiLCI0NDM0MSIsMTY4Nzc4MzUyMzM4NV0sWyJ2IiwiMTEyNTI2IiwxNjg3NzgxNzE1NDQ5XSxbImN2IiwiNDQzNDciLDE2ODc3OTE5MzU1NzFdLFsiY3YiLCI0NDMzNSIsMTY4Nzc5MTg4OTE5Nl0sWyJjdiIsIjQxNjMwIiwxNjg3Nzg2OTI1NzY4XV0=; tmr_detect=0%7C1687799899559',
    'sec-ch-ua': '"Chromium";v="112", "YaBrowser";v="23", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "Linux",
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.1.750 Yowser/2.5 Safari/537.36'
}


def get_data() -> List[dict]:
    json_list = []
    i = 0
    for page_num in tqdm(range(1, 26), desc='Searching...'):
        page_url = URL + str(page_num)
        response = requests.get(page_url, headers=headers)
        result = response.text
        soup = BeautifulSoup(result, 'lxml')
        card_list = soup.find_all('div', class_='b-common-item__image-wrap')
        prices = soup.find_all('a', class_='b-weight-container__link js-price active-link')
        for price, card in zip(prices, card_list):
            new_price = price.get('data-price')
            old_price = price.get('data-oldprice')
            offer_id = price.get('data-offerid')
            if old_price == '':
                old_price = new_price
                new_price = ''

            link = HOME_URL + card.find('a').get('href')
            onclick = card.find('a').get('onclick').replace('\'', '\"')
            start_index = onclick.find('{')
            end_index = onclick.rfind('}') + 1
            json_data = onclick[start_index:end_index]
            data = json.loads(json_data)

            brand = data['ecommerce']['click']['products'][0]['brand']
            name = data['ecommerce']['click']['products'][0]['name']
            articul = data['ecommerce']['click']['products'][0]['id']

            result = {
                'articul': articul,
                'id': offer_id,
                'name': name,
                'link': link,
                'regular-price': old_price,
                'promo-price': new_price,
                'brand': brand
            }
            json_list.append(result)

    return json_list


async def check_availability(item):
    async with aiohttp.ClientSession(headers=headers) as session:
        url = f'https://4lapy.ru/ajax/catalog/product-info/product/pickup/?offer={item["id"]}'
        async with session.get(url, timeout=100) as response:
            await asyncio.sleep(1)
            availability = await response.json()
            if not availability['data']:
                return None
            return item


async def check_available(json_list):
    tasks = []
    async with aiohttp.ClientSession():
        for item in json_list:
            task = asyncio.create_task(check_availability(item))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return [item for item in results if item is not None]


def create_xlsx(json_list):
    df = pd.DataFrame(json_list)
    date = datetime.datetime.now().strftime('%H:%M_%d-%m-%Y')
    df.to_excel(f'{date}.xlsx', index=False)
    print(f'Файл {date}.xlsx создан')


def main():
    json_list = get_data()
    print('Check availability...')
    loop = asyncio.get_event_loop()
    clear_list = loop.run_until_complete(check_available(json_list))
    create_xlsx(clear_list)


if __name__ == '__main__':
    main()
