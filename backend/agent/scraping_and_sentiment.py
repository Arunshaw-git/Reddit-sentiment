import requests 
import json 
import os
from dotenv import load_dotenv
import datetime
load_dotenv()
from openai import OpenAI

HEADERS = {
    "User-Agent": "reddit-stock-sentiment/0.1 by Arun"
}
prompt = """
You are a financial sentiment analysis engine.

Analyze the given Reddit post and its comments.
Extract all stock tickers explicitly mentioned or clearly implied.

Return the output as a Python list of dictionaries ONLY.

STRICT FORMAT RULES (DO NOT VIOLATE):
1. The output MUST be a valid Python list: [{...}, {...}]
2. Each dictionary MUST have EXACTLY these keys in this exact order:
   1) "ticker"
   2) "sentiment"
   3) "reasoning"
3. "sentiment" MUST be one of: "positive", "negative", "neutral"
4. "reasoning" MUST be a concise financial explanation justifying the sentiment.
5. DO NOT include markdown, explanations, headings, or any extra text.
6. DO NOT wrap the output in code blocks.
7. IF INSTEAD OF STOCK A SECTOR IS METIONED LIKE HEALTH, OIL, BANKING,ETC. YOU PUT THAT SECTOR IN THE TICKER.
8. IF A SAME STOCK IS MENTIONED MUTLIPLE TIME YOU JUST ENCAPSULATE IT INTO ONE OBJECT AFTER EVALUTAING BY LOOKING AT ALL THE POSTS, DO NOT REPEATE IT
Example of CORRECT output:
[
  {
    "ticker": "AAPL" or "Health Sector",
    "sentiment": "positive",
    "reasoning": "Apple is reported to have strong quarterly earnings growth, increasing services revenue, and continued institutional accumulation, indicating positive market sentiment."
  }
]

Now analyze the following input and produce the output exactly as specified.

INPUT:

"""

communities = [ 
    # "IndianStockMarket",
    # "StockMarket",
    "stocks"
]

timeRanges=[
    "today",
    "week",
    "month",
    "year"
]

def chunk_list(data, size):
    for i in range(0, len(data), size):
        yield data[i:i + size]


def analyze_chunk(posts_chunk):
    prompt_with_data = prompt + json.dumps(posts_chunk)
    print("\nrunning the ai api \n")
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528:free",
        messages=[{
            "role": "user",
            "content": prompt_with_data
        }],
        temperature=0
    )

    content = response.choices[0].message.content.strip()
    print("\nop per chunk:\n",content)
    if not content:
        return []

    try:
        return json.loads(content.replace("'", '"'))
    except Exception:
        print("❌ JSON parse failed:", content)
        return []


def merge_results(results):
    merged = {}

    for item in results:
        ticker = item["ticker"]

        if ticker not in merged:
            merged[ticker] = item
        else:
            # simple sentiment dominance logic
            if merged[ticker]["sentiment"] != item["sentiment"]:
                merged[ticker]["sentiment"] = "neutral"

    return list(merged.values())


def saveDataInJson(text,timeRange):
    timestamp = datetime.date.today().isoformat()
    base_dir = os.getcwd()

    path = os.path.join(base_dir, "results", timeRange)
    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, f"{timeRange}_{timestamp}.json")

    print(f"\nSpecific file path: {file_path}")
    try:
        with open(file_path,"w", encoding="utf-8") as f:
            f.write(text)
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
        if comment["kind"] == "t1":
           cleanedComments.append( { 
               "text":comment["data"]["body"],
                "ups":comment["data"]["ups"],
                "score":comment["data"]["score"]
            })

    return cleanedComments[:3]


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


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

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
    all_results = []

    for chunk in chunk_list(cleanedposts, 2):
        chunk_results = analyze_chunk(chunk)
        all_results.extend(chunk_results)

    final_results = merge_results(all_results)

    print("\n lol:",saveDataInJson(
        json.dumps(final_results, indent=2),
        timeRange
    ))
    