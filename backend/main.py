import requests
import re
import time
from datetime import datetime
from string import punctuation
from operator import itemgetter
from collections import Counter
from Data.big_mock_data import big_mock_posts

# Retrieves the reddit posts of the last day for the given sort. Default is `new`.
def get_reddit_posts(sort = 'new'):
    allposts = []
    after = ''

    i = 1
    while i < 10:
        while True:
            payload = {'limit': '50', 'after': after}
            response = requests.get(f'https://www.reddit.com/r/wallstreetbets/{sort}.json', params=payload)
            posts = response.json()
            if 'data' in posts and posts['data'] is not None:
                if ('children' in posts['data'] and posts['data']['children'] is not None):
                    after = posts['data']['after']
                    allposts.extend(posts['data']['children'])
                    newpostcount = len(posts['data']['children'])
                    print(f'#{i}: Received {newpostcount} new posts.')
                break
            else:
                if 'error' in posts and posts['error'] == 429:
                    print(f'#{i}: Request blocked. Trying again...')
                else:
                    print(posts)
                time.sleep(5)
        
        if (post_is_stale(allposts[-1])):
            print(f'Posts are out of date after request #{i}.')
            break
        i += 1
    
    return allposts

## cheks if the given post is older than 1 day
def post_is_stale(post):
    createdAt = datetime.utcfromtimestamp(post['data']['created'])
    time_between = datetime.now() - createdAt
    return time_between.days > 1

# Merge the posts to one array
def merge_posts(posts):
    full_text = ''
    for post in posts:
        if ('title' in post['data'] and post['data']['title'] is not None):
            title_without_duplicates = uniquify(post['data']['title'])
            full_text += title_without_duplicates
        # if ('selftext' in post['data'] post['data']['selftext'] is not None):
        #     text_without_duplicates = uniquify(post['data']['selftext'])
        #     full_text += text_without_duplicates

    return full_text

## Removes duplicates from given string
def uniquify(string):
    output = []
    seen = set()
    for word in string.split():
        if word not in seen:
            output.append(word)
            seen.add(word)
    return ' '.join(output)

# Filter the given text. Remove words from the wordlists and calls `clean_test`.
def filter_text(full_text):
    with open('./Data/english_words.txt') as f:
        common_words = f.readlines()
    common_words = [x.strip() for x in common_words]

    with open('./Data/blacklist_words.txt') as f:
        blacklist = f.readlines()
    blacklist = [x.strip() for x in blacklist]

    filtered_text = full_text
    common_words.extend(blacklist)
    for word in common_words:
        filtered_text = filtered_text.replace(word, '')
    
    filtered_text = clean_text(filtered_text)
    return filtered_text

## Removes single char strings form the given string
def clean_text(text):
    cleaned_text = text
    cleaned_text = ' '.join( [w for w in cleaned_text.split() if len(w)>1] )
    cleaned_text = ' '.join(cleaned_text.split())
    return cleaned_text

# Removes mentions with a frequency below 5 and removes strings with numbers
def filter_irrelevat_mentions(mentions):
    relevant_mentions = []
    for mention in mentions:
        if (mention[1] > 4 and not hasNumbers(mention[0])):
            relevant_mentions.append(mention)

    return relevant_mentions

### checks if the given string contains numbers
def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))

if __name__ == '__main__':
    posts = get_reddit_posts()
    full_text = merge_posts(posts)
    filtered_text = filter_text(full_text)
    mentions = Counter(filtered_text.split()).most_common()
    analysis_result = filter_irrelevat_mentions(mentions)

    print(analysis_result)
