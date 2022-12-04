import pandas as pd

DEBUG = False

def features(df):

    if DEBUG:
        print(df.head())

    # length of headline/body
    df['len_head'] = df['headline'].apply(lambda x: len(x.split()))
    df['len_body'] = df['body'].apply(lambda x: len(x.split()))

    # weight of sentiment
    df.loc[df['body_stmt'] == 2, 'body_weight'] = df['prob_neut'] / (df['prob_posi'] + df['prob_nega'])

    return df

