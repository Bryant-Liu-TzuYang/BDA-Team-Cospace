import pandas as pd
import openai
import time
import re
from tqdm import tqdm
from collections import Counter

# 設定 API 金鑰
openai.api_key = "這邊放你的API KEY"

# 讀取資料
df = pd.read_csv("data.csv")
df["string"] = df["SalePageTitle"].astype(str) + " " + df["SaleProductDescShortContent"].astype(str)

all_keywords = []
row_keywords = []

# 單筆呼叫函數（新版 API 語法）
def get_keywords_from_text(text, topn=5):
    prompt = f"""請幫我從下面這段中文內容中，找出2到3字長的高頻中文關鍵字（排除英文、純數字），回傳前{topn}個，格式如下（不需多餘說明）：
1 | 關鍵字1
2 | 關鍵字2
...
{text}
"""
    for _ in range(3):  # 最多重試三次
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print("Error:", e)
            time.sleep(5)
    return ""

# 加入進度條
for _, row in tqdm(df.iterrows(), total=len(df), desc="抓取關鍵字中"):
    text = row["string"]
    out = get_keywords_from_text(text, topn=5)
    keys = re.findall(r'\|\s*([\u4e00-\u9fa5]{2,3})', out)
    all_keywords.extend(keys)
    row_keywords.append(", ".join(keys))
    time.sleep(1.5)

df["TopKeywords"] = row_keywords

# 整體統計 Top 100
counter = Counter(all_keywords)
top100 = counter.most_common(100)
result_df = pd.DataFrame([(i+1, word) for i, (word, _) in enumerate(top100)], columns=["排名", "關鍵字"])

# 存檔
df.to_csv("with_row_keywords.csv", index=False)
result_df.to_csv("top100_keywords.csv", index=False)

print(result_df.head(10))