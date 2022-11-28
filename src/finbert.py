from transformers import BertForSequenceClassification, BertTokenizer
import torch

finbert = 'ProsusAI/finbert'
bert = 'bert-base-uncased'

def small_text(input_ids, attention_mask, bert_model='finbert'):

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

def large_text(input_ids, attention_mask, total_len, bert_model='finbert'):

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

def text_tokenizer(txt, bert_model='finbert'):

    if bert_model == 'bert':
        tokenizer = BertTokenizer.from_pretrained(bert)
    else:
        tokenizer = BertTokenizer.from_pretrained(finbert)

    tokens = tokenizer.encode_plus(txt, add_special_tokens=False)

    input_ids = tokens['input_ids']
    attention_mask = tokens['attention_mask']

    return input_ids, attention_mask

def sentiment_analysis(txt, bert_model='finbert'):
    
    input_ids, attention_mask = text_tokenizer(txt)
    window_length = 510
    total_len = len(input_ids)    
   
    if total_len < window_length:
        proba_list = small_text(input_ids, attention_mask, bert_model)
        return proba_list
    
    elif total_len >= window_length:
        proba_list = large_text(input_ids, attention_mask, total_len, bert_model)
        return proba_list

def get_mean_from_proba(proba_list):
    # 0 - positive
    # 1 - negative
    # 2 - neutral

    with torch.no_grad():
        stacks = torch.stack(proba_list)
        stacks = stacks.resize(stacks.shape[0], stacks.shape[2])
        mean = stacks.mean(dim=0)
        sentiment = torch.argmax(mean).item()
    return mean, sentiment, stacks

def full_sentiment_run(txt, bert_model='finbert'):
    proba_list = sentiment_analysis(txt, bert_model='finbert')
    mean, stacks, sentiment = get_mean_from_proba(proba_list)
    return 

def sentiment_applier(df):

    proba_list = sentiment_analysis(df, bert_model='finbert')
    mean, sentiment, stacks = get_mean_from_proba(proba_list)

    return mean, sentiment

def sentiment_poster(df):

    sent_list = []
    sent_list.append(df['body'].apply(lambda x: sentiment_applier(x)))
    list2 = sent_list[0]

    for n in range(len(list2)): 
        df.at[n, 'prob_posi'] = float(list2[n][0][0])
        df.at[n, 'prob_nega'] = float(list2[n][0][1])
        df.at[n, 'prob_neut'] = float(list2[n][0][2])
        df.at[n, 'sentiment'] = int(list2[n][1])

    return df
