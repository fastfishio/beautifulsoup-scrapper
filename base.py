from selenium import webdriver
import bs4
import os
import json
import regex

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
driver = webdriver.Chrome('/Users/marar/Downloads/chromedriver')


def find_hrefs(url, *, elem, attr, val):
    driver.get(url)
    content = driver.page_source
    soup = bs4.BeautifulSoup(content, features='html.parser')
    res = [a['href'] for a in soup.findAll(elem, href=True, attrs={attr: val})]
    return res


def get_apartment_details(url):
    driver.get(url)
    content = driver.page_source
    soup = bs4.BeautifulSoup(content, features='html.parser')
    name = soup.find('div', attrs={'aria-label': 'Property header', 'class': '_83988b93'}).text
    scripts = [a.contents for a in soup.findAll('script')]
    gmaps_json = None
    json_regex = regex.compile(r'\{(?:[^{}]|(?R))*\}')
    for script in scripts:
        if len(script) > 0:
            temp = json_regex.findall(script[0])
            if len(temp) > 0 and script[0].startswith("window['dataLayer']"):
                gmaps_json = temp[0]
                break
    if not gmaps_json:
        return {"name": name, "lat": None, 'lng': None, "url": url}
    gmaps_json = json.loads(gmaps_json)
    lat = gmaps_json['latitude']
    lng = gmaps_json['longitude']
    return {"name": name, "lat": lat, 'lng': lng, "url": url}


def main():
    with open('./results.json', mode='w', encoding='utf-8') as f:
        json.dump([], f)
    url = "https://www.bayut.com"
    sectors_1 = find_hrefs(url, elem='a', attr='class', val='c563947b')
    apartments_url = []
    apartment_results = []
    sectors = []
    for sector in sectors_1:
        sectors = sectors + find_hrefs(url+sector, elem='a', attr='class', val='b7880daf')
    sectors = sectors + sectors_1
    for apartment in sectors:
        apartments_url = apartments_url+find_hrefs(url+apartment, elem='a', attr='class', val='_287661cb')
        apartments_url = find_hrefs(url + apartment, elem='a', attr='class', val='_287661cb')
        # print( apartments_url)
        # i += 1
        for apartment in apartments_url:
            apartment_details = get_apartment_details(url + apartment)
            if (sector.find('apartments') != -1):
                apartment_details['type'] = "apartment"
            elif (sector.find('villas') != -1):
                apartment_details['type'] = "villa"
            else:
                apartment_details['type'] = "other"
            apartment_results.append(apartment_details)
    res = []
    for apartment in apartment_results:
         info = apartment['name'].split(',')
         if len(info) == 3:
             res.append({
                 "Source": apartment['url'],
                 "Emirate": info[2],
                 "area": info[1],
                 "name": info[0],
                 "full_address": apartment['name'],
                 'lat': apartment['lat'],
                 'long': apartment['lng'],
                 'type': apartment['type']
             })
         elif len(info) == 4:
             res.append({
                 "Source": apartment['url'],
                 "Emirate": info[3],
                 "area": info[2],
                 "name": info[0] + ',' + info[1],
                 "full_address": apartment['name'],
                 'lat': apartment['lat'],
                 'long': apartment['lng'],
                 'type': apartment['type']
             })
    with open('./results.json', mode='w', encoding='utf-8') as feedsjson:
        json.dump(res, feedsjson, indent=4)

# def mapping():
#     total = []
#     with open('total_dubai.json') as f:
#         total = total + json.load(f)
#     url = "https://www.bayut.com"
#     sectors = []
#     with open('data_dubai.json') as f:
#         sectors = [url + sector for sector in json.load(f)['root']]
#     for sector in sectors:
#         apartments = [url + a for a in find_hrefs(sector, elem='a', attr='class', val='_287661cb')]
#         for apartment in total:
#             if apartment['url'] in apartments:
#                 if (sector.find('apartments') != -1):
#                     apartment['type'] = "apartment"
#                 elif (sector.find('villas') != -1):
#                     apartment['type'] = "villa"
#                 else:
#                     apartment['type'] = "other"
#     with open('./final.json', mode='w', encoding='utf-8') as feedsjson:
#         json.dump(total, feedsjson)

#

#
# def create_last_for_update():
#     total = []
#     res = []
#     with open('final.json') as f:
#         total = json.load(f)
#     for apartment in total:
#         if 'type' in apartment.keys():
#             info = apartment['name'].split(',')
#             if len(info) == 3:
#                 res.append({
#                     "Source": apartment['url'],
#                     "Emirate": info[2],
#                     "area": info[1],
#                     "building_name": info[0],
#                     "full_address": apartment['name'],
#                     'lat': apartment['lat'],
#                     'long': apartment['lng'],
#                     'type': apartment['type']
#                 })
#             elif len(info) == 4:
#                 res.append({
#                     "Source": apartment['url'],
#                     "Emirate": info[3],
#                     "area": info[2],
#                     "building_name": info[0]+','+info[1],
#                     "full_address": apartment['name'],
#                     'lat': apartment['lat'],
#                     'long': apartment['lng'],
#                     'type': apartment['type']
#                 })
#
#     with open('./final_separated.json', mode='w', encoding='utf-8') as feedsjson:
#         json.dump(res, feedsjson, indent=4)


if __name__ == '__main__':
    main()
