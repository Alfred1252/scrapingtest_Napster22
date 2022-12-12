import requests
from api_key import apikey
import time
import csv

# set the Napster API key
api_key = apikey

# set the base URL for the Napster API
base_url = "https://api.napster.com/v2.2"



class GenreScraper:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
    
    def process_genres(self):
        genre_list = []
        genre_response = self.call_genres()
        if genre_response.status_code == 200:
            for genre in genre_response.json()['genres']:
                genre_name = genre['name']
                print(f'Processing the Genre: {genre_name} and its subgenres')
                sub_gen_ids = genre.get('links', {}).get('childGenres', {}).get('ids')
                if sub_gen_ids:
                    ids_url = ','.join(sub_gen_ids)
                    sub_genres = self.call_sub_genres(ids_url).json()
                    for sub_genre in sub_genres.get('genres'):
                        sub_genre_name = sub_genre.get('name')
                        genre_list.append({'genre_name': genre_name, 'sub_genre_name': sub_genre_name})
            kw = {'column1': 'genre_name', 'column2': 'sub_genre_name', 'column3':''}
            self.save_to_csv(data=genre_list, filename='generos.csv', column1='Genero', column2='Subgenero', column3='', kwargs=kw)

    def process_albums(self):
        albums_list = []
        kw = {'column1': 'artist_name', 'column2': 'albums', 'column3':''}
        with open('artistas.csv', 'r') as artsit_files:
            csv_reader = csv.DictReader(artsit_files)

            for index, row in enumerate(csv_reader):
                print(f"Processing albums of: {row.get('Artista')}")
                albums = self._get_artist_albums(row.get('Albums'))
                albums_list.append({'artist_name': row.get('Artista'), 'albums': albums})
                if index == 20:
                    break
        self.save_to_csv(data=albums_list, filename='albums.csv', column1='Artista', column2='Albumes', column3='', kwargs=kw)

    def process_top_artists(self):
        print('processing artists')
        artist_list = []
        genre_response = self.call_genres()
        if genre_response.status_code == 200:
            for index,genre in enumerate(genre_response.json()['genres']):
                genre_name = genre['name']
                sub_gen_ids = genre.get('links', {}).get('childGenres', {}).get('ids')
                if sub_gen_ids:
                    ids_url = ','.join(sub_gen_ids)
                    top_artists = self.call_top_artists_by_genre(ids_url).json()
                    time.sleep(3)
                    if top_artists.get('code') != 'GatewayTimeoutError':
                        for index, artist in enumerate(top_artists.get('artists')):
                            artist_name = artist.get('name')
                            print(f'processing: {artist_name}')
                            artist_albums_ids = self._get_albums_ids(artist)
                            artist_list.append({'genre_name': genre_name, 'artist_name': artist_name, 'artist_albums': artist_albums_ids})
                            if index == 20:
                                break
            kw = {'column1': 'genre_name', 'column2': 'artist_name', 'column3':'artist_albums'}
            self.save_to_csv(data=artist_list, filename='artistas.csv', column1='Genero', column2='Artista', column3='Albums', kwargs=kw)

    def process_songs_per_album(self):
        songs_list = []
        kw = {'column1': 'artist_name', 'column2': 'songs_per_album', 'column3':''}
        with open('artistas.csv', 'r') as artsit_files:
            csv_reader = csv.DictReader(artsit_files)

            for index, row in enumerate(csv_reader):
                print(f"Processing songs and albums of: {row.get('Artista')}")
                songs = self._get_songs_by_albums(row.get('Albums'))
                songs_list.append({'artist_name': row.get('Artista'), 'songs_per_album': songs})
                if index == 20:
                    break
        self.save_to_csv(data=songs_list, filename='songs_per_album.csv', column1='Artista', column2='SongsPerAlbum', column3='', kwargs=kw)
        

    
    def _get_albums_ids(self, artist):
        album_id_list = artist.get('albumGroups', {}).get('main')
        if album_id_list:
            albums_urls = ','.join(album_id_list[:200])
            return albums_urls
    
    def _get_artist_albums(self, albums_ids):
        artist_albums = []
        if albums_ids:
            artist_albums = [album.get('name') for album in self.call_artists_albums(albums_ids).json().get('albums')] # using list comprenhension to get the albums names
        return artist_albums

    
    def _get_songs_by_albums(self, albums_ids):
        songs_by_albums = []
        if albums_ids:
            songs_by_albums = [{album.get('albumName'): album.get('name')} for album in self.call_albums_songs(albums_ids).json().get('tracks')]
        return songs_by_albums


    #API REST FUNCTIONS

    def call_genres(self):
        genres = self.call_api('genres')
        return genres
    
    def call_sub_genres(self, id):
        sub_genre = self.call_api(f'genres/{id}')
        return sub_genre
    
    def call_top_artists_by_genre(self, id):
        top_artists = self.call_api(f'genres/{id}/artists/top')
        return top_artists

    def call_artists_albums(self, id):
        artist_albums = self.call_api(f'albums/{id}')
        return artist_albums

    def call_albums_songs(self, id):
        album_songs = self.call_api(f'albums/{id}/tracks')
        return album_songs

    def call_api(self, url):
        response = requests.get(
            f'{self.base_url}/{url}',
            headers={
                "apikey": self.api_key,},)
        return response
    
    def save_to_csv(self, data, filename, column1, column2, column3, **kwargs):
        with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([column1, column2, column3])

            for row in data:
                writer.writerow([row[kwargs['kwargs']['column1']], row[kwargs['kwargs']['column2']], row.get(kwargs['kwargs'].get('column3'), '')])
    



if __name__ == "__main__":
    scraper = GenreScraper(api_key, base_url)

    scraper.process_genres() # comenta si no quires procesar los generos
    #scraper.process_top_artists() # comenta si no quires procesar los artistas
    #scraper.process_albums()
    #scraper.process_songs_per_album()
