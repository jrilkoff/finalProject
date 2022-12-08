from transformers import BertForSequenceClassification, BertTokenizer
import torch

DEBUG = False

finbert = 'ProsusAI/finbert'
bert = 'bert-base-uncased'

def ori_text_tokenizer(txt, bert_model='finbert'):

    if DEBUG:
        print(f'3-{txt}')

    if bert_model == 'bert':
        tokenizer = BertTokenizer.from_pretrained(bert)
    else:
        tokenizer = BertTokenizer.from_pretrained(finbert)

    tokens = tokenizer.encode_plus(txt, add_special_tokens=False)

    input_ids = tokens['input_ids']
    attention_mask = tokens['attention_mask']

    return input_ids, attention_mask

def text_tokenizer(txt):

    if DEBUG:
        print(f'3-{txt}')

    bert_tokenizer = BertTokenizer.from_pretrained(bert)
    finbert_tokenizer = BertTokenizer.from_pretrained(finbert)

    bert_tokens = bert_tokenizer.encode_plus(txt, add_special_tokens=False)
    finbert_tokens = finbert_tokenizer.encode_plus(txt, add_special_tokens=False)

    bert_input_ids = bert_tokens['input_ids']
    bert_attention_mask = bert_tokens['attention_mask']

    finbert_input_ids = finbert_tokens['input_ids']
    finbert_attention_mask = finbert_tokens['attention_mask']

    return bert_input_ids, bert_attention_mask, finbert_input_ids, finbert_attention_mask


###################################################################################

def ori_small_text(input_ids, attention_mask, bert_model='finbert'):

    if bert_model == 'bert':
        model = BertForSequenceClassification.from_pretrained(bert)
    else:
        model = BertForSequenceClassification.from_pretrained(finbert)
    
    proba_list = []

    input_dict = {
        'input_ids' : torch.Tensor([input_ids]).long(),
        'attention_mask' : torch.Tensor([attention_mask]).int()
    }

    outputs = model(**input_dict)

    probabilities = torch.nn.functional.softmax(outputs[0], dim =-1)
    proba_list.append(probabilities)

    return proba_list

def ori_large_text(input_ids, attention_mask, total_len, bert_model='finbert'):

    if bert_model == 'bert':
        model = BertForSequenceClassification.from_pretrained(bert)
    else:
        model = BertForSequenceClassification.from_pretrained(finbert)
        
    proba_list = []
    start = 0
    window_length = 510
    loop = True

    while loop:
        end = start + window_length
        if end >= total_len:
            loop = False
            end = total_len

        # 1 => Define the text chunk
        input_ids_chunk = input_ids[start : end]
        attention_mask_chunk = attention_mask[start : end]
        
        # 2 => Append [CLS] and [SEP]
        input_ids_chunk = [101] + input_ids_chunk + [102]
        attention_mask_chunk = [1] + attention_mask_chunk + [1]
        
        # 3 => Convert regular python list to Pytorch Tensor
        input_dict = {
            'input_ids' : torch.Tensor([input_ids_chunk]).long(),
            'attention_mask' : torch.Tensor([attention_mask_chunk]).int()
        }
        
        outputs = model(**input_dict)
        
        probabilities = torch.nn.functional.softmax(outputs[0], dim = -1)
        proba_list.append(probabilities)

        start = end
    
    return proba_list

def small_text(bert_input_ids, bert_attention_mask, finbert_input_ids, finbert_attention_mask):

    bert_model = BertForSequenceClassification.from_pretrained(bert)
    finbert_model = BertForSequenceClassification.from_pretrained(finbert)

    bert_proba_list = []
    finbert_proba_list = []

    bert_input_dict = {
        'input_ids' : torch.Tensor([bert_input_ids]).long(),
        'attention_mask' : torch.Tensor([bert_attention_mask]).int()
    }

    finbert_input_dict = {
        'input_ids' : torch.Tensor([finbert_input_ids]).long(),
        'attention_mask' : torch.Tensor([finbert_attention_mask]).int()
    }

    bert_outputs = bert_model(**bert_input_dict)
    finbert_outputs = finbert_model(**finbert_input_dict)

    bert_probabilities = torch.nn.functional.softmax(bert_outputs[0], dim =-1)
    bert_proba_list.append(bert_probabilities)

    finbert_probabilities = torch.nn.functional.softmax(finbert_outputs[0], dim =-1)
    finbert_proba_list.append(finbert_probabilities)

    return bert_proba_list, finbert_proba_list

def large_text(bert_input_ids, bert_attention_mask, finbert_input_ids, finbert_attention_mask, total_len):

    bert_model = BertForSequenceClassification.from_pretrained(bert)
    finbert_model = BertForSequenceClassification.from_pretrained(finbert)

    bert_proba_list = []
    finbert_proba_list = []

    start = 0
    window_length = 510
    loop = True

    while loop:
        end = start + window_length
        if end >= total_len:
            loop = False
            end = total_len

        # 1 => Define the text chunk
        bert_input_ids_chunk = bert_input_ids[start : end]
        finbert_input_ids_chunk = finbert_input_ids[start : end]
        bert_attention_mask_chunk = bert_attention_mask[start : end]
        finbert_attention_mask_chunk = finbert_attention_mask[start : end]
        
        # 2 => Append [CLS] and [SEP]
        bert_input_ids_chunk = [101] + bert_input_ids_chunk + [102]
        finbert_input_ids_chunk = [101] + finbert_input_ids_chunk + [102]
        bert_attention_mask_chunk = [1] + bert_attention_mask_chunk + [1]
        finbert_attention_mask_chunk = [1] + finbert_attention_mask_chunk + [1]
        
        # 3 => Convert regular python list to Pytorch Tensor
        bert_input_dict = {
            'input_ids' : torch.Tensor([bert_input_ids_chunk]).long(),
            'attention_mask' : torch.Tensor([bert_attention_mask_chunk]).int()
        }

        finbert_input_dict = {
            'input_ids' : torch.Tensor([finbert_input_ids_chunk]).long(),
            'attention_mask' : torch.Tensor([finbert_attention_mask_chunk]).int()
        }
        
        bert_outputs = bert_model(**bert_input_dict)
        finbert_outputs = finbert_model(**finbert_input_dict)
        
        bert_probabilities = torch.nn.functional.softmax(bert_outputs[0], dim = -1)
        finbert_probabilities = torch.nn.functional.softmax(finbert_outputs[0], dim = -1)
        bert_proba_list.append(bert_probabilities)
        finbert_proba_list.append(finbert_probabilities)

        start = end
    
    return bert_proba_list, finbert_proba_list

###################################################################################

def ori_sentiment_analysis(txt, bert_model='finbert'):
    
    if DEBUG:
        print(f'2-{txt}')

    input_ids, attention_mask = text_tokenizer(txt)
    window_length = 510
    total_len = len(input_ids)    
   
    if total_len < window_length:
        proba_list = small_text(input_ids, attention_mask, bert_model)
        return proba_list
    
    elif total_len >= window_length:
        proba_list = large_text(input_ids, attention_mask, total_len, bert_model)
        return proba_list

def ori_get_mean_from_proba(proba_list):
    # 0 - positive
    # 1 - negative
    # 2 - neutral

    with torch.no_grad():
        stacks = torch.stack(proba_list)
        stacks = stacks.resize(stacks.shape[0], stacks.shape[2])
        mean = stacks.mean(dim=0)
        sentiment = torch.argmax(mean).item()
    return mean, sentiment, stacks

def ori_sentiment_applier(df):

    if DEBUG:
        print(f'1-{df}')

    proba_list = sentiment_analysis(df, bert_model='finbert')
    mean, sentiment, stacks = get_mean_from_proba(proba_list)

    return mean, sentiment

def sentiment_analysis(txt):
    
    bert_model = BertForSequenceClassification.from_pretrained(bert)
    finbert_model = BertForSequenceClassification.from_pretrained(finbert)

    if DEBUG:
        print(f'2-{txt}')

    bert_input_ids, bert_attention_mask, finbert_input_ids, finbert_attention_mask = text_tokenizer(txt)
    window_length = 510

    bert_total_len = len(bert_input_ids)    
    finbert_total_len = len(finbert_input_ids)    
   
    if bert_total_len < window_length:
        bert_proba_list, finbert_proba_list = small_text(bert_input_ids, bert_attention_mask, finbert_input_ids, finbert_attention_mask)
        return bert_proba_list, finbert_proba_list
    
    elif bert_total_len >= window_length:
        bert_proba_list, finbert_proba_list = large_text(bert_input_ids, bert_attention_mask, finbert_input_ids, finbert_attention_mask, bert_total_len)
        return bert_proba_list, finbert_proba_list

    if finbert_total_len < window_length:
        bert_proba_list, finbert_proba_list = small_text(bert_input_ids, bert_attention_mask, finbert_input_ids, finbert_attention_mask)
        return bert_proba_list, finbert_proba_list
    
    elif finbert_total_len >= window_length:
        bert_proba_list, finbert_proba_list = large_text(bert_input_ids, bert_attention_mask, finbert_input_ids, finbert_attention_mask, finbert_total_len)
        return bert_proba_list, finbert_proba_list

def get_mean_from_proba(bert_proba_list, finbert_proba_list):
    # 0 - positive
    # 1 - negative
    # 2 - neutral

    with torch.no_grad():
        bert_stacks = torch.stack(bert_proba_list)
        finbert_stacks = torch.stack(finbert_proba_list)

        bert_stacks = bert_stacks.resize(bert_stacks.shape[0], bert_stacks.shape[2])
        finbert_stacks = finbert_stacks.resize(finbert_stacks.shape[0], finbert_stacks.shape[2])

        bert_mean = bert_stacks.mean(dim=0)
        finbert_mean = finbert_stacks.mean(dim=0)

        bert_sentiment = torch.argmax(bert_mean).item()
        finbert_sentiment = torch.argmax(finbert_mean).item()

    return bert_mean, bert_sentiment, bert_stacks, finbert_mean, finbert_sentiment, finbert_stacks

def bert_sentiment_applier(df):

    if DEBUG:
        print(f'1-{df}')

    bert_proba_list, finbert_proba_list = sentiment_analysis(df)
    
    bert_mean, bert_sentiment, bert_stacks, finbert_mean, finbert_sentiment, finbert_stacks = get_mean_from_proba(bert_proba_list, finbert_proba_list)

    return bert_mean, bert_sentiment

def finbert_sentiment_applier(df):

    if DEBUG:
        print(f'1-{df}')

    bert_proba_list, finbert_proba_list = sentiment_analysis(df)
    
    bert_mean, bert_sentiment, bert_stacks, finbert_mean, finbert_sentiment, finbert_stacks = get_mean_from_proba(bert_proba_list, finbert_proba_list)

    return finbert_mean, finbert_sentiment

###################################################################################

def ori_sentiment_poster(df):

    body_list = []
    head_list = []

    if DEBUG:
        print(f'4 - {df}')

    head_list.append(df['headline'].apply(lambda x: sentiment_applier(x)))
    body_list.append(df['body'].apply(lambda x: sentiment_applier(x)))
    
    head_list.append(df['headline'].apply(lambda x: sentiment_applier(x)))
    body_list.append(df['body'].apply(lambda x: sentiment_applier(x)))
    
    list2 = body_list[0]
    list1 = head_list[0]

    for n in range(len(list2)): 
        df.at[n, 'body_posi'] = float(list2[n][0][0])
        df.at[n, 'body_nega'] = float(list2[n][0][1])
        df.at[n, 'body_neut'] = float(list2[n][0][2])
        df.at[n, 'body_stmt'] = int(list2[n][1])

    for n in range(len(list1)): 
        df.at[n, 'head_posi'] = float(list1[n][0][0])
        df.at[n, 'head_nega'] = float(list1[n][0][1])
        df.at[n, 'head_neut'] = float(list1[n][0][2])
        df.at[n, 'head_stmt'] = int(list1[n][1])

    return df

def sentiment_poster(df):

    bert_body_list = []
    bert_head_list = []

    finbert_body_list = []
    finbert_head_list = []

    if DEBUG:
        print(f'4 - {df}')

    bert_head_list.append(df['headline'].apply(lambda x: bert_sentiment_applier(x)))
    bert_body_list.append(df['body'].apply(lambda x: bert_sentiment_applier(x)))
    
    finbert_head_list.append(df['headline'].apply(lambda x: finbert_sentiment_applier(x)))
    finbert_body_list.append(df['body'].apply(lambda x: finbert_sentiment_applier(x)))
    
    bert_list2 = bert_body_list[0]
    bert_list1 = bert_head_list[0]

    finbert_list2 = finbert_body_list[0]
    finbert_list1 = finbert_head_list[0]

    for n in range(len(bert_list2)): 
        df.at[n, 'b_body_posi'] = float(bert_list2[n][0][0])
        df.at[n, 'b_body_nega'] = float(bert_list2[n][0][1])
        # df.at[n, 'body_neut'] = float(bert_list2[n][0][2])
        df.at[n, 'b_body_stmt'] = int(bert_list2[n][1])

    for n in range(len(bert_list1)): 
        df.at[n, 'b_head_posi'] = float(bert_list1[n][0][0])
        df.at[n, 'b_head_nega'] = float(bert_list1[n][0][1])
        # df.at[n, 'head_neut'] = float(bert_list1[n][0][2])
        df.at[n, 'b_head_stmt'] = int(bert_list1[n][1])

    for n in range(len(finbert_list2)): 
        df.at[n, 'fb_body_posi'] = float(finbert_list2[n][0][0])
        df.at[n, 'fb_body_nega'] = float(finbert_list2[n][0][1])
        df.at[n, 'fb_body_neut'] = float(finbert_list2[n][0][2])
        df.at[n, 'fb_body_stmt'] = int(finbert_list2[n][1])

    for n in range(len(finbert_list1)): 
        df.at[n, 'fb_head_posi'] = float(finbert_list1[n][0][0])
        df.at[n, 'fb_head_nega'] = float(finbert_list1[n][0][1])
        df.at[n, 'fb_head_neut'] = float(finbert_list1[n][0][2])
        df.at[n, 'fb_head_stmt'] = int(finbert_list1[n][1])

    return df
