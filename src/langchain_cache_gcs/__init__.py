import hashlib
import json
import time
from typing import Any
from typing import List
from typing import Optional

from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from langchain_core.caches import BaseCache
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration

class GCSStandardCache(BaseCache):
    def __init__(
        self, bucket_name: str, prefix: str = "langchain_cache/", project_id: str = None
    ):
        """初始化 GCS 快取
        Args:
            bucket_name: GCS 儲存桶名稱
            prefix: 儲存快取物件的前綴路徑
            project_id: GCP 專案 ID
        """
        self.client = storage.Client(project=project_id)
        self.bucket = self.client.bucket(bucket_name)
        self.prefix = prefix.rstrip("/") + "/"

    def _get_key(self, prompt: str, llm_string: str) -> str:
        """生成快取鍵（基於提示和 LLM 字串的哈希）"""
        combined = f"{prompt}:{llm_string}".encode()
        return self.prefix + hashlib.sha256(combined).hexdigest() + ".json"

    def lookup(self, prompt: str, llm_string: str) -> Optional[List[Any]]:
        """查詢快取"""
        try:
            blob = self.bucket.get_blob(self._get_key(prompt, llm_string))
            if blob is None:
                return None
            data = json.loads(blob.download_as_text())
            cached_response = data.get("response")

            # 為了與 LangChain 相容，需要將字串轉換回 ChatGeneration 物件
            if cached_response:

                generations = []
                for response_text in cached_response:
                    message = AIMessage(content=response_text)
                    generation = ChatGeneration(message=message)
                    generations.append(generation)
                return generations

            return None
        except GoogleCloudError as e:
            print(f"Error accessing GCS: {e}")
            return None
        except Exception as e:
            print(f"Error deserializing data: {e}")
            return None

    def update(self, prompt: str, llm_string: str, return_val: List[Any]) -> None:
        """更新快取"""
        # 將 ChatGeneration 物件轉換為可序列化的格式
        serializable_response = []
        for item in return_val:
            if hasattr(item, "text"):  # ChatGeneration 物件
                serializable_response.append(item.text)
            elif hasattr(item, "content"):  # 其他訊息物件
                serializable_response.append(item.content)
            else:
                serializable_response.append(str(item))

        blob = self.bucket.blob(self._get_key(prompt, llm_string))
        blob.upload_from_string(
            json.dumps(
                {"response": serializable_response, "timestamp": int(time.time())}
            ),
            content_type="application/json",
        )

    def clear(self) -> None:
        """清除快取（刪除指定前綴下的所有物件）"""
        blobs = self.bucket.list_blobs(prefix=self.prefix)
        for blob in blobs:
            blob.delete()

