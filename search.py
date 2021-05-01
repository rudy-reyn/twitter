#!/usr/bin/env python3
#
# perform_searches.py
from twitter import perform_search
import os
import sys
import json
import time
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import pymongo


with open("info.json", "r") as con_info:
    tw_connect = json.load(con_info)["twitterAPI"]
    c_auth = tw_connect[0]["Consumer Keys"][0]
    app_auth = tw_connect[0]["Authentication Tokens"][0]

auth = OAuthHandler(c_auth["API key"], c_auth["API key secret"])
auth.set_access_token(app_auth["Access token"],
                      app_auth["Access token secret"])
api = tweepy.API(auth)

relevant_terms = json.load(open("terms.json", "r"))["terms"]
print("Performing automated searches for specified terms on twitter.")

def search():
    log = open("searches.log", "a+")
    term = np.random.choice(relevant_terms)
    results = perform_search(term, 1250)

    print("*********************************************************", file=log)

    if results:
        try:
            # postgres database connection
            connection = "postgres://postgres:1349@localhost:1234/twitter"
            engine = create_engine(connection)
            df = pd.DataFrame(results)
            df.to_sql("search_results", engine, index=False, if_exists="append")
            
            message = f"""Search at: {time.strftime('%Y-%m-%d-%H:%M')}
                      \rSearch results for term {term} saved to search_results in postgres."""
            print(message, file=log)

        except Exception as EX:
            # A connection may need to be established if an exception occurs.
            try:
                # mongo database connection
                with open("info.json") as info:
                    db_connection = json.load(info)["mongo"]["connection"]
                
                client = pymongo.MongoClient(db_connection)
                twdb = client["twitter"]
                collection = twdb["search_result_backups"]
                collection.insert_one(results.copy())
                
                message = f"""Exception at: {time.strftime('%Y-%m-%d-%H:%M')}
                      \rSearch results for term {term} failed to save to search_results in postgres.
                      \rSaving to search_results_backup in mongodb instead."""
                print(message, file=log)

            except Exception as MX:
                message = f"""Exception at: {time.strftime('%Y-%m-%d-%H:%M')}
                          \r{MX}.
                          \rBackup save to search_result_backups failed."""
                print(message, file=log)

        finally: 
            # Also saving search results to local backups folder.
            df = pd.DataFrame(results)
            name = f"result-backups/result-backup-{round(time.time())}-import.csv"
            df.to_csv(name, index=False)

    # If results returned nothing
    else:
        message = f"""Exception at: {time.strftime('%Y-%m-%d-%H:%M')}
                  \rNo results found for {term}."""
        print(message, file=log)

    print("*********************************************************\n", file=log)

if __name__ == "__main__":
    if not os.path.exists("result-backups"):
        os.mkdir("result-backups")
    
    while True:
        search()
        time.sleep(60 * 17)
        print("Sleeping. ")
