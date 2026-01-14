from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

response = client.chat.completions.create(
      model="deepseek/deepseek-r1-0528:free",
      messages=[
        {
          "role": "user",
          "content": """You are a financial sentiment analysis engine.
            Analyze the given Reddit post and its comments.
            Extract all stock tickers explicitly mentioned or clearly implied.
            Example of CORRECT output:
            [
              {
                "ticker": "AAPL" or "Health Sector",
                "sentiment": "positive",
                "reasoning": "Apple is reported to have strong quarterly earnings growth, increasing services revenue, and continued institutional accumulation, indicating positive market sentiment."
              }
            ]
            i/p:
            [{'post_text': "Which makes no sense, since they don't even charge interest, they just process transactions. Am I missing something here or there's an opportunity for making a quick buck here? I don't think that congress will allow that idea to go anywhere anyways, either.", 'score': 525, 'num_comments': 152, 'subreddit': 'stocks', 'upvote_ratio': 0.95, 'comments': [ {'text': '10% rate would cause banks to cancel higher risk cc’s.  I don’t think it will happen, but a lot of things I didn’t think would happen have happened.\n\nI took a 1% position in V at 328 about an hour ago, so shit is prob gonna hit the fan.', 'ups': 311, 'score': 311}, {'text': 'No because logically it still makes sense. Because the belief is that banks will close existing accounts and deny other accounts for high risk borrowers. The high risk borrowers are ironically the ones who use the most credit cards. How does Visa and Mastercard make money? They make it on volume processing, so logic still follows that they would reduce revenue because of a drop in volume. Actually probably disproportionately if what I said is true about high risk borrowers using cards more.', 'ups': 112, 'score': 112}]}]
             """
        }
      ]
    )
print(f"\n{response.choices[0].message.content} ")