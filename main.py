import pymongo
import IMDB_BeautifulSoup_Scraper as scrape

client = pymongo.MongoClient("mongodb://localhost:27017")


mydb=client['MovieReviewsDBBeautifulSoup']

genre=mydb['Genres']
movies=mydb['Movies']
genres=scrape.get_genres()
for (genre_name,genre_link) in genres:
    
    movies_dict=scrape.get_movies(genre_link)
    movie_list=[]
    movie_id_list=[]
    for movie_link,movie_name in movies_dict.items():
        movie_list.append(movie_name)
        movie_id=movie_link.split('/')[-1]
        movie_id_list.append(movie_id)
        if movies.find_one({'_id':movie_id}):
            continue
        
        movie=scrape.get_movie(movie_link)

        reviews=scrape.get_reviews(movie_link)
        
        movies.insert_one({
            '_id' : movie_id,
            'name': movie_name,
            'rating' : movie['rating'],
            'release_year' : movie['release_year'],
            'director' :movie['director'],
            'cast' : movie['cast'],
            'reviews' :reviews
        }
            
        )
    genre.insert_one({
        'genre': genre_name,
        'movies' : movie_list,
        'movies_id' : movie_id_list
    })
client.close()
    

