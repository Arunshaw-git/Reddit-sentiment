import requests 
from google import genai
import json 
import os
from dotenv import load_dotenv

load_dotenv()

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
7. If no stock ticker is mentioned, return an empty list: []

Example of CORRECT output:
[
  {
    "ticker": "AAPL",
    "sentiment": "positive",
    "reasoning": "Apple is reported to have strong quarterly earnings growth, increasing services revenue, and continued institutional accumulation, indicating positive market sentiment."
  }
]

Now analyze the following input and produce the output exactly as specified.

INPUT:
<Post text and comments go here>
INPUT:

"""

communities = [ 
    # "IndianStockMarket",
    # "StockMarket",
    "stocks"
]
timeRanges=[
    "day",
    "week",
    "month",
    "year"
]
def saveDataInJson(text):
    base_dir = os.getcwd()
    path = os.path.join(base_dir, "results")
    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, "results.json")

    print(f"\nSpecific file path: {path}")
    
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
           cleanedComments.append( { "text":comment["data"]["body"], "ups":comment["data"]["ups"],"score":comment["data"]["score"] })

    return cleanedComments[:5]


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


for community in communities:
    res = requests.get(f"https://www.reddit.com/r/{community}/top.json?t=week", headers=HEADERS)

    # for timeRange in timeRange:
    #     requests.get(f"https://www.reddit.com/r/{community}/top/?t={timeRange}/.json")

cleanedposts = cleaningThePosts(res.json())
print("\n final:",cleanedposts)



client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
promptwithdata = prompt + json.dumps(cleanedposts) 
response = client.models.generate_content(
    model="gemini-2.5-flash", contents=promptwithdata
)
print(saveDataInJson(response.text))