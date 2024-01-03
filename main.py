import pymongo
import IMDB_BeautifulSoup_Scraper as scrape

#connecting to the local mongo client
client = pymongo.MongoClient("mongodb://localhost:27017")

#Creating the Database 
mydb=client['MovieReviewsDBBeautifulSoup']

#Creating collections genres and movies
genre=mydb['Genres']
movies=mydb['Movies']

#Getting the genre names and the link to their popular movies page.
genres=scrape.get_genres()

for (genre_name,genre_link) in genres:
    
    #Extracting top 20 movies.
    movies_dict=scrape.get_movies(genre_link)
    movie_list=[]
    movie_id_list=[]
    
    # Extracting the details for the movies
    for movie_link,movie_name in movies_dict.items():
        movie_list.append(movie_name)
        
        # Using the unique link which imdb uses to define each movie's webpage,
        # we will define the id of a movie in the DB
        
        movie_id=movie_link.split('/')[-1]
        movie_id_list.append(movie_id)
        
        # If the movie is already in the db, we ignore it.
        if movies.find_one({'_id':movie_id}):
            continue
        
        #Extracting the details of the movie like rating, cast,year of release and directors
        movie=scrape.get_movie(movie_link)

        #Extracting the reviews of the movie
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
    

