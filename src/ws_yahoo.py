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

    headers = {
    'authority': 'www.spot.im',
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    # Requests sorts cookies= alphabetically
    'cookie': 'device_uuid=80e01093-d9cb-4199-9a8d-5302402b793a; access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IiIsInZlcmlmaWVkIjpmYWxzZSwidXNlcl9pZCI6InVfS2tRM2pYV1lDN3JLIiwiZGlzcGxheV9uYW1lIjoiT3JhbmdlQ29uZSIsInVzZXJfbmFtZSI6Ik9yYW5nZUNvbmUiLCJyZWdpc3RlcmVkIjpmYWxzZSwiaW1hZ2VfaWQiOiIjT3JhbmdlLUNvbmUiLCJyb2xlcyI6W10sInNzb19kYXRhIjpudWxsLCJwcm92aWRlcnMiOm51bGwsInJlcHV0YXRpb24iOnt9LCJzcG90X2lkIjoic3BfUmJhOWFGcEciLCJsYXN0X2NoZWNrIjoxNjY5NzU3MjQ2LCJ2ZXJzaW9uIjo0LCJ4LXNwb3RpbS10b2tlbiI6IjAxMjIxMTI5ZXRSQzFMLjUxZjQzNDEwMWE3NTQ3YzdmOGIxYTE3NDIxMTg3MTA1ZDZiNTY0YjM5MDhkM2ViNTIzZmU5M2FiMGNjYWNiZjAiLCJwZXJtaXNzaW9ucyI6bnVsbCwic3BvdGltLWRldmljZS12MiI6ImRfVzMwRURPVFZkcUpjSjdBTzVpT3YiLCJuZXR3b3JrIjp7Im5ldHdvcmtfaWQiOiJuZXRfeWFob28iLCJuZXR3b3JrX25hbWUiOiJ5YWhvbyIsIm5ldHdvcmtfaW1hZ2VfaWQiOiI5ZDAwMWIwMTMxMzIyYTBiMmFmYWM1MjYyMGU3MzI4MSIsIm5ldHdvcmtfY29sb3IiOiIifSwic3BvdF9uYW1lIjoiIiwiZG9tYWluIjoiIiwicm9sZXNfbnVtYmVyIjowLCJ0ZW1wX3VzZXIiOmZhbHNlLCJleHAiOjE2Njk3NjA4NDYsInN1YiI6InVfS2tRM2pYV1lDN3JLIn0.u-U5dUwDE5pGhfMtOgju8_mD6vnJW2tgb8iOB3jCy_k; spotim-device-v2=d_W30EDOTVdqJcJ7AO5iOv',
    'origin': 'https://openweb.jac.yahoosandbox.com',
    'referer': 'https://openweb.jac.yahoosandbox.com/0.8.1/safeframe.html',
    'sec-ch-ua': '"Microsoft Edge";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56',
    'x-spotim-device-uuid': '80e01093-d9cb-4199-9a8d-5302402b793a',
    'x-spotim-page-view-id': '343b3bd3-f548-46c3-935e-30e483be67c2',
    'x-spotim-spotid': 'sp_Rba9aFpG',
    'x-spotim-token': '01221129etRC1L.51f434101a7547c7f8b1a17421187105d6b564b3908d3eb523fe93ab0ccacbf0',
    }
    
    response = requests.get(url, headers=headers)
    
    if not response.ok:
        print('Status code - get_page:', response.status_code)
        doc = ""
        # raise Exception('Failed to load page {}'.format(url))
    else:
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

def parse_paragraphs(doc):
    """Get the list of tags containing news information"""
    if doc == "":
        news_list = ""
    else:
        news_class = "caas-body" ## class name of div tag 
        news_list  = doc.find_all('div', {'class': news_class})
    
    return news_list

def parse_news_article(news_tag):
    
    if news_tag == "":
        body_string = ""
    else:
        table = news_tag[0].find_all('p')
        para_list = []
        body_string = ''
        
        for x in table:
            para_list.append(x.text)

        for x in para_list:
            body_string += ' ' + x

        body_string = body_string.replace("\"", '')
    
    return body_string

############################### Gets date of article from Yahoo Finance ################################# 

def get_article_date(url):
    date_class = 'caas-attr-meta-time' ## class name of time stamp
    doc = get_page(url)
    if doc == "":
        date = ""
    else:
        date_stamp = doc.find_all('time', {'class': date_class})
        date = date_stamp[0].get('datetime')
    
    return date

def get_article_body(url):
        
    doc = get_page(url) # Generic, used on any website
    article = parse_paragraphs(doc) # Used for article bodies, Yahoo Finance
    article_body = parse_news_article(article) #
    
    return article_body

############################### Uses Yahoo Articles, builds dataframe for NLP #########################################################################

def dataframe_prep(news_df):

    num = 2 # determines # rows

    sentiment_probability = ['fb_body_posi', 'fb_body_nega', 'fb_body_neut', 'fb_head_posi', 'fb_head_nega', 'fb_head_neut',
        'b_body_posi', 'b_body_nega', 'b_head_posi', 'b_head_nega']
    sentiment_numeric = ['fb_body_stmt', 'fb_head_stmt', 'b_body_stmt', 'b_head_stmt']

    print('Obtaining individual articles')
    
    # news_df['body'] = news_df['url'].apply(lambda x: get_article_body(x))
    news_df['body'] = news_df['url'].iloc[:num].apply(lambda x: get_article_body(x))
    
    print('Obtaining dates of articles')
    
    # news_df['date'] = news_df['url'].apply(lambda x: get_article_date(x))
    news_df['date'] = news_df['url'].iloc[:num].apply(lambda x: get_article_date(x))
    news_df = news_df.drop(news_df[news_df.date == ""].index)
    news_df['date'] = pd.to_datetime(news_df['date'], format='%Y-%m-%dT%H:%M:%S.%fZ').dt.date
    news_df[sentiment_probability] = float()
    news_df[sentiment_numeric] = int()
    news_df = news_df.reset_index()

    return news_df
####################################################################################################################################################



############################### Finivz Datascraping Functions ###############################

def fv_get_page(ticker):
    """Download a webpage and return a beautiful soup doc"""

    headers = {
    'authority': 'www.spot.im',
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    # Requests sorts cookies= alphabetically
    'cookie': 'device_uuid=80e01093-d9cb-4199-9a8d-5302402b793a; access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IiIsInZlcmlmaWVkIjpmYWxzZSwidXNlcl9pZCI6InVfS2tRM2pYV1lDN3JLIiwiZGlzcGxheV9uYW1lIjoiT3JhbmdlQ29uZSIsInVzZXJfbmFtZSI6Ik9yYW5nZUNvbmUiLCJyZWdpc3RlcmVkIjpmYWxzZSwiaW1hZ2VfaWQiOiIjT3JhbmdlLUNvbmUiLCJyb2xlcyI6W10sInNzb19kYXRhIjpudWxsLCJwcm92aWRlcnMiOm51bGwsInJlcHV0YXRpb24iOnt9LCJzcG90X2lkIjoic3BfUmJhOWFGcEciLCJsYXN0X2NoZWNrIjoxNjY5NzU3MjQ2LCJ2ZXJzaW9uIjo0LCJ4LXNwb3RpbS10b2tlbiI6IjAxMjIxMTI5ZXRSQzFMLjUxZjQzNDEwMWE3NTQ3YzdmOGIxYTE3NDIxMTg3MTA1ZDZiNTY0YjM5MDhkM2ViNTIzZmU5M2FiMGNjYWNiZjAiLCJwZXJtaXNzaW9ucyI6bnVsbCwic3BvdGltLWRldmljZS12MiI6ImRfVzMwRURPVFZkcUpjSjdBTzVpT3YiLCJuZXR3b3JrIjp7Im5ldHdvcmtfaWQiOiJuZXRfeWFob28iLCJuZXR3b3JrX25hbWUiOiJ5YWhvbyIsIm5ldHdvcmtfaW1hZ2VfaWQiOiI5ZDAwMWIwMTMxMzIyYTBiMmFmYWM1MjYyMGU3MzI4MSIsIm5ldHdvcmtfY29sb3IiOiIifSwic3BvdF9uYW1lIjoiIiwiZG9tYWluIjoiIiwicm9sZXNfbnVtYmVyIjowLCJ0ZW1wX3VzZXIiOmZhbHNlLCJleHAiOjE2Njk3NjA4NDYsInN1YiI6InVfS2tRM2pYV1lDN3JLIn0.u-U5dUwDE5pGhfMtOgju8_mD6vnJW2tgb8iOB3jCy_k; spotim-device-v2=d_W30EDOTVdqJcJ7AO5iOv',
    'origin': 'https://openweb.jac.yahoosandbox.com',
    'referer': 'https://openweb.jac.yahoosandbox.com/0.8.1/safeframe.html',
    'sec-ch-ua': '"Microsoft Edge";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56',
    'x-spotim-device-uuid': '80e01093-d9cb-4199-9a8d-5302402b793a',
    'x-spotim-page-view-id': '343b3bd3-f548-46c3-935e-30e483be67c2',
    'x-spotim-spotid': 'sp_Rba9aFpG',
    'x-spotim-token': '01221129etRC1L.51f434101a7547c7f8b1a17421187105d6b564b3908d3eb523fe93ab0ccacbf0',
    }
    
    
    # headers = {
    # 'User-Agent': 'Mozilla/5.0',
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}

    base_url = f'https://finviz.com/quote.ashx?t={ticker}&p=d'
    html = requests.get(base_url, headers=headers)
    
    if not html.ok:
        print('Status code - fv_page:', html.status_code)
        # pass
        # raise Exception('Failed to load page {}'.format(url))

    doc = bs(html.content, "html.parser")
        
    # response = requests.get(url)
    # if not response.ok:
    #     print('Status code:', response.status_code)
    #     # raise Exception('Failed to load page {}'.format(url))
    # page_content = response.text
    # doc = bs(page_content, 'html.parser')
       
    return doc

def fv_get_news_tag(doc):
    # Can this function just be removed?  It is one line of code.
    # TO DELETE?

    news_list = doc.find('table', {'id': 'news-table'})

    return news_list

def fv_parse_news(news_tag):
    """Get the news data point and return dictionary"""

    news_source = news_tag.find('div').text #source
    news_headline = news_tag.find('a').text #heading
    news_url = news_tag.find('a')['href'] #link
    
    # base_url = 'https://ca.finance.yahoo.com'
    # news_source = news_tag.find('div', {'class': 'news-link-left'}).text #source
    # news_headline = news_tag.find('a') #heading .text
    
    # if news_headline == -1:
    #     print('yes')

    # news_headline = news_tag.find('div', {'class': 'news-link-left'})
    # print(news_headline)
    # news_url = news_tag.find('a')
    # news = news_url.find('href') #link ['href']
    # print(news)
    return { 'source' : news_source,
            'headline' : news_headline,
            'url' : news_url # base_url + 
           }

def fv_get_article_body(url):
        
    doc = fv_get_page(url)
    article = parse_paragraphs(doc)
    article_body = parse_news_article(article)
    
    return article_body

def fv_dataframe(news_list):

    url_list = news_list.find_all('a')
    source_list = news_list.find_all('span')

    df_finviz = pd.DataFrame()
    df_finviz[['url', 'headline', 'source']] = ""

    for n in range(len(url_list)):
            url = url_list[n]['href']
            headline = url_list[n].text
            if '%' not in source_list[n].text:
                source = source_list[n].text
            else:
                pass                
                            
            if 'finance.yahoo' in url:
                df_finviz.loc[n, 'url'] = url
                df_finviz.loc[n, 'headline'] = headline
                df_finviz.loc[n, 'source'] = source
            else:
                pass
    # df_finviz.drop(columns='source', inplace=True)

    return df_finviz

############################### Finviz News Scraper ################################# 

def scrape_finviz(ticker):

    doc = fv_get_page(ticker)
    news_list = fv_get_news_tag(doc)
    df_news = fv_dataframe(news_list)
    df_final = dataframe_prep(df_news)

    # df_final.drop(columns=['source', 'date'], inplace=True)    

    return df_final

######################################################################################


############################### Feature Engineering ################################# 


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
    df['company'] = ticker

    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d').dt.date

    return df


############################### Combines DF w/ Stock Price ################################# 

def dataframe_price_sentiment(ticker, start, end): #, website

    print(f'Obtaining price for: {ticker}')
    df_price = stock_price(ticker, start, end)

    print(f'Obtaining URLs for: {ticker}')
    df_news = scrape_finviz(ticker)

    print('Preparing dataframe')
    df_prepped = dataframe_prep(df_news)

    print('Final adjustments...')
    df_final = pd.merge(df_price, df_prepped, right_on='date', left_on='Date')

    return df_final