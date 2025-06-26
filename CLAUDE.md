# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個 Python 套件，為 LangChain 的快取系統實作 Google Cloud Storage (GCS) 後端。主要元件是 `GCSStandardCache`，將 LLM 回應儲存在 GCS 儲存桶中以避免重複的 API 呼叫。

## 開發環境設定

此專案使用 `uv` 作為套件管理器。安裝相依套件：
```bash
uv sync --group dev
```

## 核心元件

- **GCSStandardCache** (`src/langchain_cache_gcs/__init__.py`): 主要快取實作，負責在 GCS 儲存桶中儲存/檢索 LLM 回應
- **test.py**: 使用範例和測試腳本

## 架構設計

快取運作機制：
1. 從提示詞 + LLM 字串組合生成 SHA256 雜湊鍵值
2. 將回應以 JSON 格式儲存到 GCS，包含時間戳記元資料
3. 在 LangChain 的 ChatGeneration 物件與可序列化格式間轉換
4. 支援透過前綴批次清除快取

## 常用指令

執行測試範例：
```bash
uv run test.py
```

建置套件：
```bash
uv build
```

## 設定需求

快取需要：
- Google Cloud 認證（透過服務帳戶或應用程式預設認證）
- GCS 儲存桶名稱和選擇性的專案 ID  
- 環境變數載入（test.py 使用 python-dotenv）

## 相依套件

- google-cloud-storage: GCS 用戶端程式庫
- langchain: LangChain 核心框架
- langchain-xai: XAI 提供者（開發用相依套件，用於測試）

## 文件與註解規範

撰寫文件、註解時應使用台灣繁體中文。