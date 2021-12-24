import datetime
from fastapi import FastAPI
import requests
import time
from datetime import datetime, timedelta
import config as conf
import memory as m

# Initialize the app
app = FastAPI()
start_time = time.monotonic()
m.last_news_update = datetime.now()

# Check runtime
@app.get("/")
def read_root():
    end_time = time.monotonic()
    return {
        'runtime': str(timedelta(seconds=end_time - start_time)),
        'version': '1.0.0'
    }

@app.get("/dev")
def read_memory():
    if m.last_news_update.date() == datetime.today().date():
        print("No update today")
    return {
        'New Date': m.last_news_update,
    }

# News API Endpoint
@app.get("/news/headlines")
def read_headlines():
    url = f"{conf.NEWS_API_URL}top-headlines?country=id&apiKey={conf.NEWS_API_KEY}"

    # If saved data is empty, fetch and save data
    if (m.last_news_update.date() != datetime.today().date() or not bool(m.NEWS_HEADLINES)):
        print("Fetching news headlines")
        m.NEWS_HEADLINES.update(requests.get(url).json())
        m.last_news_update = datetime.now()
    else:
        print("Using saved data")
    data = m.NEWS_HEADLINES

    # Only return 15 top headlines
    return data['articles'][:15]

@app.get("/news/sources")
def read_sources():
    url = f"{conf.NEWS_API_URL}top-headlines/sources?country=us&apiKey={conf.NEWS_API_KEY}"

    # If saved data is empty, fetch and save data
    if (not bool(m.NEWS_SOURCES)):
        m.NEWS_SOURCES.update(requests.get(url).json())
    return m.NEWS_SOURCES['sources']

@app.get("/news/search/{query}")
def read_everything(query: str):
    url = f"{conf.NEWS_API_URL}everything?q={query}&apiKey={conf.NEWS_API_KEY}"
    response = requests.get(url)
    data: list = response.json()['articles']

    if (len(data) != 0):
        return data[:20]
    else:
        return {
            'status': 'error',
            'message': 'No data found'
        }

# Hoax Endpoint

# Get latest hoax data
@app.get("/hoax/latest")
def read_latest_hoax():
    response = requests.get(f"{conf.HOAX_V1_URL}/latest/10/{conf.HOAX_API_KEY}")
    return response.json()

# Get hoax by query
@app.get("/hoax/search/{query}")
def read_search_hoax(query: str):
    response = requests.get(f"{conf.HOAX_V1_URL}/tags/{query}/{conf.HOAX_API_KEY}")

    data = response.json()

    if (len(data) > 10):
        return data[:10]
    else:
        return data

# Get hoax validator authors v1
@app.get('/hoax/authors')
def read_authors():
    if(len(m.HOAX_AUTHORS) == 0):
        get_hoax_authors()
    
    return m.HOAX_AUTHORS

# Get hoax validator author by id
@app.get('/hoax/authors/{id}')
def read_author(id: str):
    if(len(m.HOAX_AUTHORS) == 0):
        get_hoax_authors()

    available_author = {}

    for author in m.HOAX_AUTHORS:
        if (author['id'] == id):
            available_author.update(author)

    if (bool(available_author)):
        return available_author
    else:
        return {
            'status': 'error',
            'message': 'Author not found'
        }
    
# Get hoax validator authors v2
def get_hoax_authors():
    url = f"{conf.HOAX_V2_URL}/antihoax/get_authors"
    m.HOAX_AUTHORS = requests.post(url, data={'key': conf.HOAX_API_KEY}).json()