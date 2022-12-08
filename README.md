## Project/Goals

The goal of this project was to create a supervised machine learning model to predict the direction of stock price movement using NLP sentiment analysis on news articles.  
By creating a web scraper capable of looping through headline URLs, a dataframe is used to hold both the headline and article text, then align this with the stock price for that day.
There is still an ongoing goal of improving all facets of this project, from function document to overall cleanup.

## Hypothesis

Stock price movement can be predicted by the sentiment of a news article, depending on the source, and strength of sentiment.

Original estimates:

- Articles that present a strong positive sentiment will be more closely related to an upwards movement in stock price
- When an an article has a neutral or negative sentiment, it will more frequently be tied to a downward movement in stock price
- Certain news sources will be more accurate than others when it comes to publishing articles and stopck price direction
- The length of the article will not be a primary feature in determining stock price movement

## EDA

A selection of stocks was picked to build the initial dataset of ~1,090 articles.  
As Finviz.com was the easiet website to obtain a large set of headline URLs for (about 80 per company), it was used exclusively.  ~80% of links on Finviz.com went to a Yahoo Finance article.
The notebook is made to accept a list of tickers, which it then creates an individual CSV for each stock ticker's articles and analysis.
This was due to the computational requirements and as an insurance policy if computation stopped mid-way.

The stock tickers selected were:

- ALB, BHP, CDE, DMLP, FCX, HBM, HL, LAC, MAG, NXE, PAAS, RIO, SBSW, TMQ, UEC, VALE, WPM

As the news articles for this project will not be directly reviewed, most of the EDA work comes on reviewing the sentiments and the distribution of sentiment percentages.
Different sources are reviewed to see who which presents a more positive image.

## Process

Data Collection:

Note - The # of articles to capture with the webscrapper is currently an integer within the ws_yahoo.py file.
Note - This can be increased, or the other two lines of code uncommented (and comment the current code) to make it capture all valid links.

- Data is scraped off of Finviz.com for URL headlines, of which the body of the articles primarily link to Yahoo Finance
- Once all articles have been scraped, the headlines and article body's are aligned with the stock price movement of that day
- A 0 represents a lower closing price than opening, and a 1 represents a higher closing price
- This makes the target variable for the supervised machine learning model
- Stock price is pulled using the Python module yfinance
- Websites are scraped using Beautiful Soup

Data Processing:

- BERT is used with PyTorch to do an initial sentiment analysis on the headline and the article body
- This produces a % between positive and negative, as well as an overall 0 (positive) or 1 (negative)
- Also used was the specialized finBERT model, which gives a value of 2 for a neutral sentiment, alongside the 0 and 1
- This was the most time consuming part of the project and where future work will be done to optimize the code
- Each stock ticker is processed in two main steps, first the article is captured and put into a CSV, then it is processed and put into a new CSV file

Feature Engineering:

Most of the features for this project are numerical and few categorical options within the data exist.
That considered, a focus was put on engineering features that could be drawn out of the sentiment of the data.

- BERT Sentiment alignment, does the headline match the body sentiment? - 0/1
- finBERT Sentiment alignment, does the headline match the body sentiment? - 0/1
- All sentiment, do sentiments align across both NLP models? - 0/1
- Headline and article length? - integer (hypothesized to not be a prominent feature)
- Individual sentiments for headline and body were one-hot encoded as there is no quantitative difference between 0 and 1 in this context

Modeling:

- Currently there is a sklearn pipeline and GridSearchCV utilizied to test multiple parameters.  
- The model still needs refinement, but can produce results greater than 50%.
- Classifier machine learning models used are Logistic Regression, Random Forest, Gradient Boost, and Extreme Gradient Boost.

Metrics:

- There are functions built within the workbook that create a metrics list and allow for direct comparison between the models.
- Expanded metrics and visualizations are a future goal of this project.

## Results

Currently the best performing model is the XGBoost which comes in around 56% on most metrics.  
More data is needed to expand the size of the training set.
The hypothesis as it stands is currently not proven or disproven statistically.

## Challenges

Overall building the web scraper to be agile and adaptive is one of the greatest challenges.
Fortunately Finviz.com primarily links to Yahoo Finance, so collecting limited data per company was possible.
Finviz.com only lists about 100 articles per stock ticker, and does not have any information for smaller companies.
The NLP models were very computational time consuming, this is probably due to the inefficiency of the code as the BERT model was retroactively put into the Python script.
Time constraints.  Currently the project needs continued refinement and I look foward to continuing my work on it.

## Future Goals

While the project as a whole can output a working model, it has a lot of room for increased efficiency.  In the future I look forward to the following:

- Collecting more data, I found that my test set was frequently obtaining the same performance across all classification models
- Code optimization, there is a lot of room for efficiency and reworking
- Future application, it could be used to automate trading on some financial platform, making trades up to a user's level of risk tolerance
- Better visuals, expanded EDA and a greater understanding of the outputs of the model
