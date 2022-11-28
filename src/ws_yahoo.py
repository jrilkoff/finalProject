from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import urllib
import re
import requests
import csv
import pandas as pd
from datetime import datetime, date
import yfinance as yf

def get_page(url):
    """Download a webpage and return a beautiful soup doc"""
    
    response = requests.get(url)
    if not response.ok:
        print('Status code:', response.status_code)
        # raise Exception('Failed to load page {}'.format(url))
    page_content = response.text
    doc = bs(page_content, 'html.parser')
    return doc

def get_news_tags(doc):
    """Get the list of tags containing news information"""
    
    news_class = "Ov(h) Pend(44px) Pstart(25px)" ## class name of div tag 
    news_list  = doc.find_all('div', {'class': news_class})
    return news_list

def parse_news(news_tag):
    """Get the news data point and return dictionary"""
    
    base_url = 'https://ca.finance.yahoo.com'
    news_source = news_tag.find('div').text #source
    news_headline = news_tag.find('a').text #heading
    news_url = news_tag.find('a')['href'] #link
    return { 'source' : news_source,
            'headline' : news_headline,
            'url' : base_url + news_url
        }

def scrape_yahoo_news(ticker):
    """Get the yahoo finance market news and write them to CSV file """
    
    yahoo_url = 'https://ca.finance.yahoo.com/quote/'
    url = yahoo_url + ticker
    
    doc = get_page(url)
    news_list = get_news_tags(doc)
    news_data = [parse_news(news_tag) for news_tag in news_list]
    news_df = pd.DataFrame(news_data)

    return news_df 

def parse_paragraphs(doc):
    """Get the list of tags containing news information"""
    news_class = "caas-body" ## class name of div tag 
    news_list  = doc.find_all('div', {'class': news_class})
    
    return news_list

def parse_news_article(news_tag):
    table = news_tag[0].find_all('p')
    para_list = []
    body_string = ''
    
    for x in table:
        para_list.append(x.text)

    for x in para_list:
        body_string += ' ' + x

    body_string = body_string.replace("\"", '')
    
    return body_string

def get_article_date(url):
    date_class = 'caas-attr-meta-time' ## class name of time stamp
    doc = get_page(url)
    date_stamp = doc.find_all('time', {'class': date_class})
    date = date_stamp[0].get('datetime')
    
    return date

def get_article_body(url):
        
    doc = get_page(url)
    article = parse_paragraphs(doc)
    article_body = parse_news_article(article)

    return article_body

def dataframe_prep(news_df):
    news_df['body'] = news_df['url'][:2].apply(lambda x: get_article_body(x))
    news_df['date'] = news_df['url'][:2].apply(lambda x: get_article_date(x))
    news_df['date'] = pd.to_datetime(news_df['date'], format='%Y-%m-%dT%H:%M:%S.%fZ').dt.date
    news_df[['prob_posi', 'prob_nega', 'prob_neut']] = float()
    news_df['sentiment'] = int()

    return news_df

def stock_price(ticker, start, end):
    df = yf.download(
        ticker, 
        start=start, 
        end=end, 
        progress=False
    )

    df.loc[df['Open'] > df['Close'], 'target'] = 0
    df.loc[df['Open'] < df['Close'], 'target'] = 1
    df.loc[df['Open'] == df['Close'], 'target'] = 0
    df['target'] = df['target'].astype('int')

    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d').dt.date

    return df

def dataframe_price_sentiment(ticker, start, end):

    df_price = stock_price(ticker, start, end)
    df_news = scrape_yahoo_news(ticker)
    df_prepped = dataframe_prep(df_news)

    df_final = pd.merge(df_price, df_prepped, right_on='date', left_on='Date')

    return df_final