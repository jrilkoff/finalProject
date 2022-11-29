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

############################### Generic Website URL Grabber ################################# 

def get_page(url):
    """Download a webpage and return a beautiful soup doc"""
    # Not specific to any particular website, puts it in the soup
    
    response = requests.get(url)
    if not response.ok:
        print('Status code:', response.status_code)
        # raise Exception('Failed to load page {}'.format(url))
    page_content = response.text
    doc = bs(page_content, 'html.parser')
    return doc




############################### Yahoo Finance News Scraper ################################# 


def get_news_tags(doc):
    """Get the list of tags containing news information"""
    # Particular to Yahoo Finance layout
    
    news_class = "Ov(h) Pend(44px) Pstart(25px)" ## class name of div tag 
    news_list  = doc.find_all('div', {'class': news_class})
    return news_list

def parse_news(news_tag):
    """Get the news data point and return dictionary"""
    # Grabs each individual part of the news article and prepare a dictionary to be returned
    # To the     
    
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
    # This function grabs the Yahoo home page and puts it into a DF with:
    # a) News Source b) News Headline c) News URL to main article
    # This function primarily will not be used except on the Yahoo homepage
    # Function is what brings the other three together
    # TO DELETE?
    
    yahoo_url = 'https://ca.finance.yahoo.com/quote/'
    url = yahoo_url + ticker
    
    doc = get_page(url) # Generic website grabber
    news_list = get_news_tags(doc) # Specific for Yahoo
    news_data = [parse_news(news_tag) for news_tag in news_list] # Specific for Yahoo
    news_df = pd.DataFrame(news_data) # Creates dataframe

    return news_df 

######################################################################################################



############################### Pulls out individual Paragraphs, cleans ################################# 

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

def parse_paragraphs(doc):
    """Get the list of tags containing news information"""
    # Specific to the layout of Yahoo Finance Articles

    news_class = "caas-body" ## class name of div tag 
    news_list  = doc.find_all('div', {'class': news_class})
    
    return news_list

############################### Gets date of article from Yahoo Finance ################################# 

def get_article_date(url):
    date_class = 'caas-attr-meta-time' ## class name of time stamp
    doc = get_page(url)
    date_stamp = doc.find_all('time', {'class': date_class})
    date = date_stamp[0].get('datetime')
    
    return date

def get_article_body(url):
        
    doc = get_page(url) # Generic, used on any website
    article = parse_paragraphs(doc) # Used for article bodies, Yahoo Finance
    article_body = parse_news_article(article) # 

    return article_body

############################### Uses Yahoo Articles, builds dataframe for NLP ################################# 

def dataframe_prep(news_df):
    news_df['body'] = news_df['url'][:4].apply(lambda x: get_article_body(x))
    news_df['date'] = news_df['url'][:4].apply(lambda x: get_article_date(x))
    news_df['date'] = pd.to_datetime(news_df['date'], format='%Y-%m-%dT%H:%M:%S.%fZ').dt.date
    news_df[['prob_posi', 'prob_nega', 'prob_neut']] = float()
    news_df['sentiment'] = int()

    return news_df

######################################################################################################



############################### Finivz Datascraping Functions ###############################

def fv_get_page(ticker):
    """Download a webpage and return a beautiful soup doc"""
    # This specifically grabs the Finviz website page for a specific ticker and loads into BS doc


    headers = {
    'User-Agent': 'Mozilla/5.0',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}

    base_url = f'https://finviz.com/quote.ashx?t={ticker}&p=d'
    html = requests.get(base_url, headers=headers)
    doc = bs(html.content, "html.parser")

    return doc

def fv_get_news_tag(doc):
    # Can this function just be removed?  It is one line of code.
    # TO DELETE?

    news_list = doc.find('table', {'id': 'news-table'})

    return news_list

def fv_dataframe(doc):

    # news_list = doc.find('table', {'id': 'news-table'})
    url_list = doc.find_all('a')

    df_finviz = pd.DataFrame()
    df_finviz[['url', 'headline', 'source']] = ""

    for n in range(len(url_list)):
            url = url_list[n]['href']
            headline = url_list[n].text
            if 'finance.yahoo' in url:
                df_finviz.at[n, 'url'] = url
                df_finviz.at[n, 'headline'] = headline
            else:
                pass

    return df_finviz

############################### Finviz News Scraper ################################# 

def scrape_finviz(ticker):

    doc = fv_get_page(ticker)
    news_list = fv_get_news_tag(doc)
    df_news = fv_dataframe(news_list)
    df_final = dataframe_prep(df_news)

    df_final.drop(colums=['source', 'date'], inplace=True)    

    return df_final

######################################################################################


############################### Feature Engineering ################################# 

# def ()





############################### Stock price obtainer ################################# 

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


############################### Combines DF w/ Stock Price ################################# 

def dataframe_price_sentiment(ticker, start, end): #, website

    df_price = stock_price(ticker, start, end)
    
    # df_news = scrape_yahoo_news(ticker)
    df_news = scrape_finviz(ticker)
    df_prepped = dataframe_prep(df_news)

    df_final = pd.merge(df_price, df_prepped, right_on='date', left_on='Date')

    return df_final