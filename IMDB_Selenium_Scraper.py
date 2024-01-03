from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By



imdb = "https://www.imdb.com"


# get_genres() function to get all the genres available for movies on IMDB.
# returns a zipped tuple of two lists containing genre name and genre link(link to the genres top movies)
def get_genres():
    imdb = "https://www.imdb.com" 
    url = "/feature/genre" 
    
    driver = webdriver.Chrome()
    driver.get(imdb + url)
    
    # genres - gives the webelement containing the list of genres in the movies section. 
    genres = driver.find_element(
        By.XPATH,
        "/html/body/div[2]/main/div/section/div/section/div/div[1]/section[2]/div[2]/div[2]",
    )

    # html -  gets the html code present in the genres webelement
    html = genres.get_attribute("innerHTML")
    soup = bs(html, "html.parser")   # using beautiful soup to parse it.
    
    genre_list = soup.select("span") # gives the list of span- tags present in the html code(The span tags contain the name of the genre).
    web_links = soup.select("a")  # gives the list of a - tags present in the html code(The a tags contain the link of the genre)
    
    #formating the results to get the results in str and zipping it, for further use.
    genre_list = [genre.text for genre in genre_list]
    genre_link = [imdb + web_link["href"] for web_link in web_links]
    genre=zip(genre_list,genre_link)
    driver.quit()
    return genre


# get_movies : computes the name and link of top 20 movies(according to popularity) available in the genre.
# input: takes the link to the genre's top movies and returns the name and link of the page of top 20 movies.
def get_movies(genre_link):
    driver = webdriver.Chrome()
    driver.get(genre_link)
    # finding the webelement containing the list of the movies.
    # Used exception handling for handling the case where No such element is present.(there is no list)
    try:
        movies = driver.find_element(
            By.XPATH,
            "/html/body/div[2]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul",
        )
    except NoSuchElementException:
        return {}
    
    html = movies.get_attribute("innerHTML")
    soup = bs(html, "html.parser")
    
    movie_list = soup.select("h3")
    
    n=min(20,len(movie_list))
    
    _movie_list = [movie_list[i].text.split()[1:] for i in range(0, n)]
    actual_movie_list = [" ".join(_movie_list[i]) for i in range(0, n)]
    
    movie_links = soup.select("a")
    _movie_links = [(imdb + movie_links[i]["href"]).split("/") for i in range(0, 2*n, 2)]
    actual_movie_links = ["/".join(movie[: len(movie) - 1]) for movie in _movie_links]
    
    movies={}
    for i in range(n):
        movies[actual_movie_list[i]]=actual_movie_links[i]
    driver.quit()
    return movies


def get_movie(movie_link):
    driver = webdriver.Chrome()
    driver.get(movie_link)
    try:
        year_element = driver.find_element(
            By.XPATH,
            "/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[1]/a",
        )
        year = int(year_element.text)
    except NoSuchElementException:
        year = -1
    try:
        rating_element = driver.find_element(
            By.XPATH,
            "/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/div[1]/div/div[1]/a/span/div/div[2]/div[1]/span[1]",
        )
        rating_html = rating_element.get_attribute("innerHTML")
        rating = float(rating_html)
    except NoSuchElementException:
        rating = -1

    director_element = driver.find_element(
        By.XPATH,
        "/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/div[2]/div/div/div/ul/li[1]/div/ul",
    )
    directors_html = director_element.get_attribute("innerHTML")
    dir_soup = bs(directors_html, "html.parser")
    dir_list = dir_soup.select("a")
    actual_director_list = [dir.text for dir in dir_list]
    directors = ", ".join(actual_director_list)
    cast_list = []
    cast_xpath = "/html/body/div[2]/main/div/section[1]/div/section/div/div[1]/section[3]/div[2]/div[2]"
    try:
        cast_ = driver.find_element(
            By.CSS_SELECTOR,
            "div.ipc-sub-grid.ipc-sub-grid--page-span-2.ipc-sub-grid--wraps-at-above-l.ipc-shoveler__grid",
        )
        cast_html = cast_.get_attribute("innerHTML")
        cast_soup = bs(cast_html, "html.parser")
        cast_members = cast_soup.contents
        
    # print(len(cast_members))
        for i in range(len(cast_members)):
            people = cast_members[i].contents[1].a.text
            cast_list.append(people)
            # print(cast_list[i])
    except NoSuchElementException:
            print("No such element exception")
            # raise
        
    movie={}
    
    movie["rating"]= rating
    movie["release_year"]= year
    movie["director"]= directors
    movie['cast']=cast_list
    
    # driver.quit()
    return movie


def get_reviews( movie_link):
    driver = webdriver.Chrome()
    url = "/reviews?sort=submissionDate&dir=desc&ratingFilter=0"
    review_link = movie_link + url
    driver.get(review_link)
    
    reviews_dict={}
    reviews_elements = driver.find_element(By.CSS_SELECTOR, "div.lister-list")
    review_ratings_elements = reviews_elements.find_elements(
        By.CSS_SELECTOR, "span.rating-other-user-rating"
    )
    
    review_dates_elements = reviews_elements.find_elements(By.CSS_SELECTOR, "span.review-date")
    review_text_elements = reviews_elements.find_elements(
        By.CSS_SELECTOR, "div.text.show-more__control"
    )
    reviews=[]
    n = min(
        10,
        len(review_ratings_elements),
        len(review_dates_elements),
        len(review_text_elements),
    )
    for i in range(n):
        rating_html = (
            review_ratings_elements[i]
            .find_element(By.TAG_NAME, "span")
            .get_attribute("innerHTML")
        )
        reviews_dict["rating"]=int(rating_html)

        date_html = review_dates_elements[i].get_attribute("innerHTML")
        reviews_dict["date"]=date_html

        reviews_text = review_text_elements[i].get_attribute("innerHTML")
        reviews_text=reviews_text.replace('<br>','\n')
        reviews_dict["text"]=reviews_text
        reviews.append(reviews_dict)
    # driver.quit()
    return reviews



    
    



