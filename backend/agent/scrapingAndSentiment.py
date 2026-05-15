from db import save_sentiment_results
import requests 
import json 
import sys
import time
print("PYTHON AGENT STARTED")
sys.stdout.flush()
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
import os
import datetime
import config

from google import genai
from google.genai import errors
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

HEADERS = {
    "User-Agent": "reddit-stock-sentiment/0.1 by Arun"
}
prompt = """
Extract investment sentiment from the input.

Investments can be:
- Stocks (use ticker if available)
- Sectors or industries if no stock is specified

Rules:
- Merge duplicate investments into one entry
-Reasoning should be a detailed analysis. It should not contain metadata about posts but the reason mentioned in the posts and comments with some more relavant data from the internet but not any personal bad experience like they bought at the top and are in loss right now.  
-Confidence should be a decimal between 0 and 1 representing how certain you are about the sentiment.

Output ONLY a valid JSON array of objects.
No markdown, no code blocks, no extra text.

Each dict must have exactly these keys in order:
"asset", "sentiment", "reasoning", "url", "score", "subreddit", "num_comments", "upvote_ratio", "confidence"

Sentiment must be: positive, negative, or neutral.

If nothing relevant, return [].
"""
communities = [ 
    "IndianStockMarket",
    "StockMarket",
    "stocks"
]

timeRanges=[
    "today",
    "week",
    "month",
    "year"
]

def cleanResutIntoJson(result):
    text = result.strip()
     # Remove ```json or ``` at start
    text = re.sub(r'^```(?:json)?', '', text, flags=re.IGNORECASE).strip()
    # Remove ``` at end
    text = re.sub(r'```$', '', text).strip()
    
    return json.loads(text)


import os
import shutil

def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        print("Folder does not exist:", folder_path)
        return

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)          # delete file
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)      # delete subfolder
        except Exception as e:
            print(f"Failed to delete {item_path}: {e}")


def saveDataInJson(text,timeRange):
    timestamp = datetime.date.today().isoformat()
    base_dir = os.getcwd()

    path = os.path.join(base_dir, "results", timeRange)
    os.makedirs(path, exist_ok=True)
    clear_folder(path)
    file_path = os.path.join(path, f"{timeRange}_{timestamp}.json")

    print(f"\nSpecific file path: {file_path}")
    try:
        with open(file_path,"w", encoding="utf-8") as f:
            json.dump(text,f,indent=2,ensure_ascii=False)
    except Exception as e:
        print("Invalid",e )
        return False
    
    return True
        
        
def getCleanComments(link):
    res = requests.get(f"https://www.reddit.com{link}.json" , headers=HEADERS)

    if res.status_code != 200:
        print("\nstatus code 200 while fetching comments\n")
        return []

    comments = res.json()
    cleanedComments= []

    for comment in comments[1]["data"]["children"]: 
        if comment["kind"] == "t1" and comment["data"]["author"] != "AutoModerator":
           cleanedComments.append( { 
               "text":comment["data"]["body"],
                "ups":comment["data"]["ups"],
                "score":comment["data"]["score"]
            })

    return cleanedComments[:2]


def cleaningThePosts(wholePostsJson):
    cleaned  =[]
    for item in wholePostsJson["data"]["children"]:
        # post["post"] = post["data"]["selftext"]  i thought i could just change the dict's elements of the list 
        post = item["data"]
        cleaned.append({
            "post_text": post["selftext"],
            "score": post["score"],
            "num_comments": post["num_comments"],
            "subreddit": post["subreddit"],
            "upvote_ratio":post["upvote_ratio"],
            "url":post["permalink"],
            "score":post["score"],
            "comments":getCleanComments(post["permalink"])
        })
        
    return cleaned[:6]


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not loaded. Check .env path.")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=30),
    retry=retry_if_exception_type(errors.ServerError),
    before_sleep=lambda retry_state: print(f"Retrying Gemini call (attempt {retry_state.attempt_number}) due to high demand...")
)
def generate_content_with_retry(client, model, content):
    return client.models.generate_content(model=model, contents=content)

def analyze_sentiment(client, content):
    # Optimized list of the most performant models
    models = [
        "gemini-3-flash-preview",
        "gemini-2.5-flash", 
        "gemini-2.0-flash"
    ]
    last_error = None
    
    for model_name in models:
        try:
            print(f"Attempting analysis with {model_name}...")
            return generate_content_with_retry(client, model_name, content)
        except errors.ServerError as e:
            print(f"Model {model_name} is currently overloaded (503). Trying fallback...")
            last_error = e
            continue
        except errors.ClientError as e:
            print(f"Model {model_name} not available or invalid (404/400). Trying fallback...")
            last_error = e
            continue
        except Exception as e:
            print(f"Unexpected error with model {model_name}: {repr(e)}")
            raise e
            
    if last_error:
        print("CRITICAL: All Gemini models are currently experiencing high demand.")
    raise last_error if last_error else Exception("No active models available")

def run_agent():
    print("Starting sentiment analysis agent...")
    for timeRange in timeRanges:
        cleanedposts = []
        for community in communities:
            print(f"Fetching posts from r/{community} for {timeRange}...")
            res = requests.get(f"https://www.reddit.com/r/{community}/top.json?t={timeRange}/", headers=HEADERS)

            if res.status_code != 200:
                print(f"couldnt get posts for the {community} ", res)
                continue
            cleanedposts.extend(cleaningThePosts(res.json()))
            time.sleep(2) # Avoid Reddit 429s
                
        print(f"\n\n Cleaned posts for {timeRange}:", len(cleanedposts))
        
        if cleanedposts :
            promptwithdata = prompt + json.dumps(cleanedposts)
            print(f"Running LLM analysis for {timeRange}...")
            try:
                response = analyze_sentiment(client, promptwithdata)
                parsed = cleanResutIntoJson(response.text)
                if parsed:
                    status = save_sentiment_results(parsed, timeRange)
                    print(f"\n ResultSaved for {timeRange}:", status)
                else:
                    print(f"No data parsed for this {timeRange}")
            except Exception as e:
                print(f"Gemini call failed for {timeRange} after all retries", repr(e))
        else:
            print(f"No cleaned posts for this {timeRange}")
        
        time.sleep(4)
    print("Agent run completed.")

if __name__ == "__main__":
    run_agent()
