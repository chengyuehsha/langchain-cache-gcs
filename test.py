import time

from langchain.globals import set_llm_cache
from langchain_cache_gcs import GCSStandardCache
from langchain_xai import ChatXAI
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # 初始化 LLM
    llm = ChatXAI(
        model="grok-3-mini",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=1,
    )

    # 設置 GCS 標準快取
    set_llm_cache(
        GCSStandardCache(bucket_name="my-rss-459510", project_id="my-rss-459510")
    )

    # 測試快取
    start = time.time()
    print(llm.invoke("Tell me a joke"))
    print(f"First call: {time.time() - start} seconds")

    start = time.time()
    print(llm.invoke("Tell me a joke"))
    print(f"Second call: {time.time() - start} seconds")








