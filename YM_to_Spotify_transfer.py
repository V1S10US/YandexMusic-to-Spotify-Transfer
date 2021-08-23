from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import re

def run_driver():
    chrome_options = Options()  # add options for chrome driver

    chrome_options.add_argument('--headless')  # no window
    chrome_options.add_argument('--log-level=3')  # no logging

    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
    return driver

def create_local_html_page(page_filename, page_source):
    with open(page_filename + '.html',mode= 'w',encoding='UTF-8') as file:
        file.write(page_source)  # make local .html

def get_local_html_page(page_filename, url):

    driver = run_driver()

    driver.get(url)
    create_local_html_page(page_filename, driver.page_source)
    path_to_local_html_page = str('file://' + os.getcwd() + '\\' + page_filename + '.html')

    driver.get(path_to_local_html_page)

    return driver

def delete_local_html_page(page_path):
    os.remove(page_path)

def get_albums(yandex_username):
    url = 'https://music.yandex.ru/users/' + yandex_username + '/albums/'

    driver = get_local_html_page('album_page', url)

    mu_json = driver.execute_script('return Mu')

    albums_artists = {}

    albums_ids = mu_json['pageData']['albumIds']

    for album_id in albums_ids:  # fill albums_artists
        try:
            driver.get('https://music.yandex.ru/album/' + str(album_id))

            albums_artists[album_id] = {}

            albums_artists[album_id]['album_title'] = driver.find_element_by_xpath(
                    "//h1[@class='deco-typo']").text  # get album name

            albums_artists[album_id]['artist_name'] = driver.find_element_by_xpath(
                    "//span[@class='d-artists']//a[@class='d-link deco-link']").text  # get artist name

        except:
            raise Exception

    delete_local_html_page('album_page.html')
    driver.quit()

    return  albums_artists

def get_my_playlists_id(yandex_username):
    url = 'https://music.yandex.ru/users/'+ yandex_username + '/playlists/'

    driver = get_local_html_page('playlist_page', url)

    mu_json = driver.execute_script('return Mu')
    # get playlist ids
    my_playlists_id = mu_json['pageData']['playlistIds']

    return my_playlists_id

def get_my_playlists(yandex_username):
    # get playlist ids
    my_playlists_id = get_my_playlists_id(yandex_username)
    my_playlists_for_spotify = {}

    for pl_id in my_playlists_id:
        # создадим ссылку на плейлист
        my_playlist_url = 'https://music.yandex.ru/users/' + yandex_username + '/playlists/' + str(pl_id)
        # создадим и перейдем на локальную страницу плейлиста
        driver = get_local_html_page('my_playlist', my_playlist_url)
        # получим массив с данными плейлистов
        mu_json = driver.execute_script('return Mu')

        # создадим словарь, в который запишем название трека и имя исполнителя
        my_playlists = {}
        # получим из json значение id трека и id плейлиста в формате track_id:playlist_id
        all_track_ids = mu_json['pageData']['playlist']['trackIds']
        # получим название плейлиста
        playlist_name = mu_json['pageData']['playlist']['title']

        for i in all_track_ids:
        # получим id трека
            track_id = re.findall(r'\d+(?=:)', i)[0]
        # перейдем на страницу трека
            driver.get(''.join(['https://music.yandex.ru/track/', track_id]))
        # создадим вложенный словарь для каждого плейлиста
            my_playlists[i] = {}
        # запишем в словарь название трека
            try:
                my_playlists[i]['track_name'] = \
                driver.find_elements_by_xpath("//span[@class='']//a[@class='d-link deco-link']")[0].text
            except:
                my_playlists[i]['track_name'] = ['']
                # запишем в словарь имя исполнителя
            try:
                my_playlists[i]['artist_name'] = driver.find_elements_by_xpath(
                    "//span[@class='d-artists']//a[@class='d-link deco-link']")[0].text
            except:
                my_playlists[i]['track_name'] = ['']

            # запишем в словарь название плейлиста, его треки и имена исполнителей
        my_playlists_for_spotify[playlist_name] = my_playlists

        # удалим локальный html-файл
        delete_local_html_page('my_playlist.html')


        # закроем браузер
        driver.quit()

    return my_playlists_for_spotify

def get_liked_playlists_data(yandex_username):
    url = 'https://music.yandex.ru/users/' + yandex_username + '/playlists/'

    driver = get_local_html_page('playlist_page', url)

    mu_json = driver.execute_script('return Mu')

    liked_playlists_data = {}

    bookmarked_playlists_data = mu_json['pageData']['bookmarks']

    for i in range(len(bookmarked_playlists_data)):
        try:
            # создадим вложенный словарь для каждого плейлиста
            liked_playlists_data[i] = {}
            # запишем во вложенный словарь id плейлиста
            liked_playlists_data[i]['id'] = bookmarked_playlists_data[i]['kind']
            # запишем во вложенный словарь имя пользователя
            liked_playlists_data[i]['yandex_username'] = bookmarked_playlists_data[i]['owner']['login']
            # запишем во вложенный словарь название плейлиста
            liked_playlists_data[i]['playlist_title'] = bookmarked_playlists_data[i]['title']
        except:
            pass

        delete_local_html_page('playlist_page.html')

        return liked_playlists_data


def get_liked_playlists(yandex_username):
    liked_playlists_data = get_liked_playlists_data(yandex_username)

    liked_playlists_for_spotify = {}

    for key, value in liked_playlists_data.items():

        url = 'https://music.yandex.ru/users/' + \
               str(value['yandex_username']) + \
               '/playlists/' + str(value['id'])

        driver = get_local_html_page(str(key), url)

        mu_json = driver.execute_script('return Mu')

        liked_playlists = {}

        all_track_ids = mu_json['pageData']['playlist']['trackIds']
        playlist_name = mu_json['pageData']['playlist']['title']

        for i in all_track_ids:
            try:
                track_id = re.findall(r'\d+(?=:)', all_track_ids[i])[0]

                driver.get(''.join(['https://music.yandex.ru/track/', track_id]))

                liked_playlists[i] = {}

                try:
                    liked_playlists[i]['track_name'] = \
                    driver.find_elements_by_xpath("//span[@class='']//a[@class='d-link deco-link']")[0].text
                except:
                    liked_playlists[i]['track_name'] = ['']


                try:
                    liked_playlists[i]['artist_name'] = driver.find_elements_by_xpath(
                        "//span[@class='d-artists']//a[@class='d-link deco-link']")[0].text
                except:
                    liked_playlists[i]['artist_name'] = ['']

            except:
                pass

        liked_playlists_for_spotify[playlist_name] = liked_playlists

        delete_local_html_page(str(key) + '.html')

        driver.quit()

    return  liked_playlists_for_spotify
