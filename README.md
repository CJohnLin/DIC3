# 🎰 DIC3: MAB Explore vs Exploit (多臂老虎機模擬)

> **✨ 線上互動體驗 (Live Demo)**: [https://dic3.onrender.com/](https://dic3.onrender.com/)  
> *本專案已成功部署至 Render.com，您可以直接點擊上方連結體驗流暢的動態圖表與參數調整功能！*

此專案根據作業要求，模擬了多臂老虎機 (Multi-Armed Bandit) 問題當中的 **A/B 測試策略 (Explore-then-Exploit)**。為了更直觀地分析，此專案已升級為**高度互動式的現代化 Web App**，能夠計算並解答作業規定的六個問題，包含預期獎勵、遺憾值 (Regret) 以及各策略比較。

---

## 🌟 核心特色

- **🎛️ 參數即時調整面板**：自由設定老虎機 A、B、C 的期望勝率 (Means) 以及分配在探索期的測試預算 (Explore Budget) 或總預算。
- **📈 動態流暢圖表**：前台匯入強大的 `Chart.js` 來產生擁有過渡動畫、滑鼠懸停資料顯示的「累積平均回報曲線」與「機率估計對比長條圖」。
- **✨ 現代化設計風格**：擁有極具科技質感的漸層深色模式背景 (Dark Mode) 以及「玻璃擬物化 (Glassmorphism)」浮動亮面卡片！

---

## 🚀 技術堆疊 (Tech Stack)

- **Backend (API)**: `Python 3.11`, `Flask`, `Numpy`
- **Frontend (UI/UX)**: `Vanilla JS`, `Chart.js`, `HTML5 / CSS3`
- **Deployment**: `Render.com`

---

## 💻 本地端執行 (Run Locally)

如果您希望在自己的電腦上離線運行：

1. 開啟終端機並切換至此資料夾，安裝必要的依賴套件：
   ```bash
   pip install -r requirements.txt
   ```
2. 啟動 Flask 後端 API 伺服器：
   ```bash
   python app.py
   ```
3. 開啟您的網頁瀏覽器，造訪 [http://127.0.0.1:5000/](http://127.0.0.1:5000/) 即可玩轉參數分析！
