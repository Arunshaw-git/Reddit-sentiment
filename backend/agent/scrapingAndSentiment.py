import requests 
import json 
import os
from dotenv import load_dotenv
import datetime
load_dotenv()
# from openai import OpenAI
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
-Reasoning should not contain metadata about posts but the reason mentioned in the posts and comments.  

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

def saveDataInJson(text,timeRange):
    timestamp = datetime.date.today().isoformat()
    base_dir = os.getcwd()

    path = os.path.join(base_dir, "results", timeRange)
    os.makedirs(path, exist_ok=True)

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
        
    return cleaned


# client = OpenAI(
#   base_url="https://openrouter.ai/api/v1",
#   api_key=os.getenv("OPENROUTER_API_KEY"),
# )

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for timeRange in timeRanges:
    cleanedposts = []
    completedTimeRange = "" 
    for community in communities:
        res = requests.get(f"https://www.reddit.com/r/{community}/top.json?t={timeRange}/", headers=HEADERS)

        if res.status_code != 200:
            print("!200",res)
            continue
        cleanedposts.extend(cleaningThePosts(res.json()))
              
    print(f"\n\n Cleaned posts for {timeRange}:",cleanedposts)
    # all_results = []
    
    promptwithdata = prompt + json.dumps(cleanedposts)

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=promptwithdata      
    )
    # for chunk in chunk_list(cleanedposts, 1):
    #     print("\nchunk:",chunk)
    #     chunk_results = analyze_chunk(chunk)
    #     all_results.extend(chunk_results)

    # final_results = merge_results(all_results)
    parsed = cleanResutIntoJson(response.text)
    print("\n ResultSavedOrNot:",saveDataInJson(
        parsed,
        timeRange
    ))
    