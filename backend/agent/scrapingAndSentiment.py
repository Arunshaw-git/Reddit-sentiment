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
import re

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
-Reasoning should not contain metadata about posts but the reason mentioned in the posts and comments with some more relavant data from the internet but not any personal bad experience like they bought at the top and are in loss right now.  

Output ONLY a valid JSON array of objects.
No markdown, no code blocks, no extra text.

Each dict must have exactly these keys in order:
"asset", "sentiment", "reasoning"

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


# def chunk_list(data, size):
#     for i in range(0, len(data), size):
#         yield data[i:i + size]


# def analyze_chunk(posts_chunk):
#     print("\nrunning the ai api \n")
#     post = json.dumps(posts_chunk)
#     response = client.chat.completions.create(
#         model="deepseek/deepseek-r1-0528:free",
#         messages=[
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content":post}
#         ],
#         temperature=0
#     )

#     content = response.choices[0].message.content.strip()
#     print("\nop per chunk:\n",content)
#     if not content:
#         return []

#     try:
#         return json.loads(content)
#     except Exception:
#         print("❌ JSON parse failed:", content)
#         return []


# def merge_results(results):
#     merged = {}

#     for item in results:
#         ticker = item["ticker"]

#         if ticker not in merged:
#             merged[ticker] = item
#         else:
#             # simple sentiment dominance logic
#             if merged[ticker]["sentiment"] != item["sentiment"]:
#                 merged[ticker]["sentiment"] = "neutral"

#     return list(merged.values())
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
            "comments":getCleanComments(post["permalink"])
        })
        
    return cleaned[:6]


# client = OpenAI(
#   base_url="https://openrouter.ai/api/v1",
#   api_key=os.getenv("OPENROUTER_API_KEY"),
# )
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not loaded. Check .env path.")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for timeRange in timeRanges:
    cleanedposts = []
    completedTimeRange = "" 
    for community in communities:
        res = requests.get(f"https://www.reddit.com/r/{community}/top.json?t={timeRange}/", headers=HEADERS)

        if res.status_code != 200:
            print(f"couldnt get posts for the ${community} ",res)
            continue
        cleanedposts.extend(cleaningThePosts(res.json()))
              
    print(f"\n\n Cleaned posts for {timeRange}:",cleanedposts)
    # all_results = []
    if cleanedposts :
        promptwithdata = prompt + json.dumps(cleanedposts)
        print("running the llm")
        print("Prompt with data: ", promptwithdata)
        try:
            print("Calling Gemini...")
            response = client.models.generate_content(
            model="gemini-2.5-flash", contents=promptwithdata      
            )
        except Exception as e:
            print("Gemini call failed", repr(e))
            raise
    else:
        print(f"No cleaned posts for this {timeRange}")
        response =[]
    
    # for chunk in chunk_list(cleanedposts, 1):
    #     print("\nchunk:",chunk)
    #     chunk_results = analyze_chunk(chunk)
    #     all_results.extend(chunk_results)

    # final_results = merge_results(all_results)
    parsed = cleanResutIntoJson(response.text)

    print("Gemini:\n",parsed)
    if parsed:
        print("\n ResultSavedOrNot:",save_sentiment_results(parsed, timeRange))
        requests.get(f"https://reddit-sentiment-0l0e.onrender.com/invalidate/{timeRange}")
    else:
        print(f"No data saving for this {timeRange}")
    time.sleep(4)

