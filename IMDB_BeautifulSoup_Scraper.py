import requests
from lxml import etree
from bs4 import BeautifulSoup as bs

imdb = "https://www.imdb.com"
url = "/feature/genre"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
}


def get_genres():
    r = requests.get(url=imdb + url, headers=headers)
    soup = bs(r.content, "html.parser")
    r.close()
    #Using beautifulSoup to parse the Doc.
    first_div = soup.find("div", attrs={"class": "ipc-chip-list__scroller"})
    genres_tags = first_div.find_next("div", attrs={"class": "ipc-chip-list__scroller"})
    #The genre tags are stored in the second div
    genre_list = genres_tags.select(
        "span"
    )  
    # gives the list of span- tags present in the html code(The span tags contain the name of the genre).
    web_links = genres_tags.select(
        "a"
    )  
    # gives the list of a - tags present in the html code(The a tags contain the link of the genre)

    # formating the results to get the results in str and zipping it, for further use.
    genre_list = [genre.text for genre in genre_list]
    genre_link = [imdb + web_link["href"] for web_link in web_links]
    genre = zip(genre_list, genre_link)
    return genre


def get_movies(genre_link):
    
    r = requests.get(url=genre_link, headers=headers)
    soup = bs(r.content, "html.parser")
    r.close()
    #The movies list is stored in a ul 
    movies_ul = soup.find("ul", attrs={"role": "presentation"})
    if movies_ul ==None:
        return {}
    movies_list = movies_ul.select("h3")
    n=min(20,len(movies_list))
    _movie_list = [movies_list[i].text.split()[1:] for i in range(0, n)]
    actual_movie_list = [" ".join(_movie_list[i]) for i in range(0, n)]
    
    movie_links = movies_ul.select("a")
    _movie_links = [(imdb + movie_links[i]["href"]).split("/") for i in range(0, 2*n, 2)]
    actual_movie_links = ["/".join(movie[: len(movie) - 1]) for movie in _movie_links]
    
    movies={}
    
    
    for i in range(n):
        # print(i,actual_movie_links[i],actual_movie_list[i])
        movies[actual_movie_links[i]] = actual_movie_list[i]
    return movies


def get_movie(movie_link):
    r = requests.get(url=movie_link, headers=headers)
    soup = bs(r.content, "html.parser")
    r.close()
    
    # Find the div containing movie details
    movie_ = soup.find("div", attrs={"class": "sc-69e49b85-0 jqlHBQ"})
    # Try to find the release year of the movie, If the year is not found, set it as -1
    try:
        year = int(movie_.find("a").text)
    except AttributeError:
        year = -1
        
    # Try to find the rating, If the rating is not found, set it as -1
    rating = soup.find("span", attrs={"class": "sc-bde20123-1 cMEQkK"})
    try:    
        rating = float(rating.text)
    except AttributeError:
        rating = -1
    
    # Find the div containing the director's details
    director_div = soup.find("div", attrs={"class": "sc-69e49b85-3 dIOekc"})
    director_li = director_div.find("li")
    
    # Find all list items containing the directors' name
    directors_list = director_li.find_all("li")
    
    # Create a list of director's names
    directors = [director.text for director in directors_list]
    
    cast_list = []
    # Find the div containing the cast details
    cast_soup = soup.find(
        "div",
        attrs={
            "class": "ipc-sub-grid ipc-sub-grid--page-span-2 ipc-sub-grid--wraps-at-above-l ipc-shoveler__grid"
        },
    )
    #cast_members contains the list of all the members, we will just extract the name
    try:
        cast_members = cast_soup.contents
        for i in range(len(cast_members)):
            people = cast_members[i].contents[1].a.text
            cast_list.append(people)
    except:
        # If no cast details are found, leave the cast list empty
        cast_list = []
        
    movie = {}
    movie["rating"] = rating
    movie["release_year"] = year
    movie["director"] = directors
    movie["cast"] = cast_list
    return movie


def get_reviews(movie_link):
    url = "/reviews?sort=submissionDate&dir=desc&ratingFilter=0"
    r = requests.get(url=movie_link + url, headers=headers)
    soup = bs(r.content, "html.parser")
    r.close()
    
    #all reviews are present in the following div container.
    reviews_elements = soup.find("div", attrs={"class": "lister-list"}).contents

    n = min(
        10,
        len(reviews_elements) / 2,
    )
    
    reviews = []
    for i in range(1, int(2 * n), 2):

        reviews_dict = {}
        # Extracting all the relevant info from them
        
        review_ratings_elements = reviews_elements[i].find(
            "span", attrs={"class": "rating-other-user-rating"}
        )

        review_dates_elements = reviews_elements[i].find(
            "span", attrs={"class": "review-date"}
        )
        review_title_elements = reviews_elements[i].find(
            "a", attrs={"class": "title"}
        )
        review_text_elements = reviews_elements[i].find(
            "div",
            attrs={"class": "text show-more__control"}
        )
        
        #Ratings are sometimes not available with Review, if not found set it to -1
        try:
            rating_html = review_ratings_elements.find("span")
            reviews_dict["rating"] = int(rating_html.text)
        except AttributeError:
            reviews_dict["rating"] = -1
        
        #Dates, and review text are always there so, no need to check if they are present or not.
        
        date_html = review_dates_elements.text
        reviews_dict["date"] = date_html
        
        review_title=review_title_elements.text
        reviews_dict['title'] =review_title
        
        reviews_text = review_text_elements.text
        reviews_dict["text"] = reviews_text
        
        reviews.append(reviews_dict)
        

    return reviews

# get_movies("https://www.imdb.com/search/title/?title_type=feature&genres=western")