#!/usr/bin/env python3
#
"""Module providing set of functions for performing searches

and parsing results for gathering twitter data from twitter.
"""
import json
from collections import defaultdict
import tweepy
from tweepy import OAuthHandler


def parse_result(term, tweets) -> dict:
    "Parses the User iterator returned by tweepy.Cursor"
    
    # Sets default value to a list if the key doesn't exist.
    results = defaultdict(list)
    for i in range(len(tweets)):
        author = tweets[i].author
        # Tweet specific attibutes
        results["created_at"].append(tweets[i].created_at.strftime("%s"))
        results["tweet_text"].append(tweets[i].text)
        # Tweet author attributes
        results["name"].append(author.name)
        results["screen_name"].append(author.screen_name)
        results["location"].append(author.location)
        results["description"].append(author.description)
        results["num_followers"].append(author.followers_count)
        results["num_following"].append(author.friends_count)
        results["num_tweets"].append(author.statuses_count)
        results["account_age"].append(author.created_at.strftime("%s"))
        # Term searched
        results["term"].append(term)
    
    results["retweet"] = [tweet.startswith("RT") for tweet in results["tweet_text"]]
    return results

def perform_search(term: str, items=1) -> tuple:
    "Gets a tweet given a specific term"
    try:
        tweet_iterator = tweepy.Cursor(
                         api.search, q=term, lang="en"
                         ).items(items)
        tweets = [tweet for tweet in tweet_iterator]

        if len(tweets):
            successful = True
        else:
            successful = False
            print(f"No results found for {term}")
    except:
        # Handles 429 errors if too many requests have been sent
        successful = False

    if successful:
        print(f"Search succesful for {term}. {len(tweets)} results found.")
        return parse_result(term, tweets)
