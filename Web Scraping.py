import requests
from bs4 import BeautifulSoup
import sqlite3
from sqlalchemy import create_engine, Column, String, Integer, Base
from sqlalchemy.orm import sessionmaker
import schedule
import time

Base = declarative_base()

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    link = Column(String)

engine = create_engine('sqlite:///news.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def clean_data(data):
    return data.strip().replace('\n', ' ')

def scrape_news():
    url = "https://news.ycombinator.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    headlines = soup.find_all('a', class_='storylink')
    
    for headline in headlines:
        title = clean_data(headline.text)
        link = headline['href']
        
        news_item = News(title=title, link=link)
        session.add(news_item)
    
    session.commit()
    print("News data stored successfully.")

try:
    scrape_news()
except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Error: {e}")

def job():
    try:
        scrape_news()
    except Exception as e:
        print(f"Error: {e}")

schedule.every().hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
