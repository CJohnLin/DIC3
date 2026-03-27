# DIC3: MAB 探索與利用 (Explore vs Exploit) 作業

此 Flask 應用程式根據作業要求模擬了多臂老虎機 (Multi-Armed Bandit) 問題中的 A/B 測試策略，計算並回答了作業中的六個問題，包含預期獎勵、遺憾值 (Regret) 以及各策略的比較，同時將模擬結果可視化。

## 如何執行此應用程式

1. 在此資料夾 (`c:\Users\林佳宏\Desktop\DIC3`) 中開啟終端機 (Terminal 或命令提示字元 / PowerShell)。
2. 安裝必要的依賴套件：
   ```bash
   pip install -r requirements.txt
   ```
3. 執行 Flask 應用程式：
   ```bash
   python app.py
   ```
4. 開啟您的網頁瀏覽器，並前往 http://127.0.0.1:5000/ 即可檢視作業結果與圖表。

## 專案結構
- `app.py`: 主要的 Flask 伺服器，包含 A/B 測試的模擬邏輯與 Matplotlib 圖表生成。
- `templates/index.html`: 負責展示回答與圖表結果的網頁介面。
- `requirements.txt`: Python 所需的相依套件清單 (Flask, numpy, matplotlib)。
