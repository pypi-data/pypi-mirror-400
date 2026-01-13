# 快速發布指南 / Quick Publishing Guide

## 測試發布到 TestPyPI

### 步驟 1: 獲取 TestPyPI Token

1. 訪問 https://test.pypi.org/
2. 註冊或登入帳號
3. 前往 https://test.pypi.org/manage/account/token/
4. 創建新的 API token（選擇 "Entire account" 範圍）
5. **複製並保存** token（只會顯示一次）

### 步驟 2: 設置環境變數

**Windows (PowerShell)**:
```powershell
$env:UV_PUBLISH_TOKEN = "pypi-你的testpypi_token"
```

**Linux/Mac**:
```bash
export UV_PUBLISH_TOKEN="pypi-你的testpypi_token"
```

### 步驟 3: 構建並發布

```bash
# 確保所有測試通過
uv run pytest

# 構建套件
uv build

# 發布到 TestPyPI
uv publish --index testpypi
```

### 步驟 4: 測試安裝

```bash
# 安裝測試
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ fhl-bible-api

# 測試功能
python -c "from fhl_bible_api import FHLBibleClient; c = FHLBibleClient(); r = c.get_verse(1,1,1); print(r.records[0].text); c.close()"
```

---

## 正式發布到 PyPI

### 步驟 1: 獲取 PyPI Token

1. 訪問 https://pypi.org/
2. 註冊或登入帳號
3. 前往 https://pypi.org/manage/account/token/
4. 創建新的 API token（選擇 "Entire account" 範圍）
5. **複製並保存** token（只會顯示一次）

### 步驟 2: 設置環境變數

**Windows (PowerShell)**:
```powershell
$env:UV_PUBLISH_TOKEN = "pypi-你的pypi_token"
```

**Linux/Mac**:
```bash
export UV_PUBLISH_TOKEN="pypi-你的pypi_token"
```

### 步驟 3: 最終檢查

```bash
# 運行所有測試
uv run pytest --cov=fhl_bible_api

# 程式碼檢查
uv run ruff check .

# 構建套件
uv build
```

### 步驟 4: 發布

```bash
# 發布到 PyPI
uv publish
```

### 步驟 5: 驗證

```bash
# 等待幾分鐘後安裝
pip install fhl-bible-api

# 測試
python -c "from fhl_bible_api import FHLBibleClient; print('Success!')"
```

---

## 使用自動化腳本

```bash
# 運行互動式發布腳本
uv run python publish.py

# 腳本會:
# 1. 運行測試
# 2. 檢查程式碼
# 3. 格式化程式碼
# 4. 構建套件
# 5. 詢問發布目標 (TestPyPI/PyPI)
```

---

## 常見問題

### Q: Token 格式是什麼？
A: 格式為 `pypi-xxxxx...`，從 PyPI/TestPyPI 網站生成。

### Q: 如何檢查 token 是否設置？
A: 
```bash
# Windows
echo $env:UV_PUBLISH_TOKEN

# Linux/Mac
echo $UV_PUBLISH_TOKEN
```

### Q: 發布失敗提示 "403 Forbidden"？
A: 檢查：
- Token 是否正確
- Token 是否過期
- 是否使用了正確的 token（TestPyPI vs PyPI）
- 套件名稱是否已被佔用

### Q: 如何更新已發布的套件？
A: 
1. 更新 `pyproject.toml` 中的版本號
2. 更新 `src/fhl_bible_api/__init__.py` 中的 `__version__`
3. 重新構建並發布

### Q: 可以刪除已發布的版本嗎？
A: PyPI 不允許刪除版本，但可以 "yank" 標記為不推薦。建議發布前在 TestPyPI 充分測試。

### Q: Token 會過期嗎？
A: Token 不會自動過期，但建議定期更換以確保安全。

---

## 安全提醒

⚠️ **重要**：
- 永遠不要把 token 提交到 git
- 不要在公開場合分享 token
- 使用完後清除環境變數（可選）
- 為 PyPI 和 TestPyPI 使用不同的 token

```bash
# 清除環境變數 (Windows PowerShell)
Remove-Item Env:UV_PUBLISH_TOKEN

# 清除環境變數 (Linux/Mac)
unset UV_PUBLISH_TOKEN
```

---

## 檢查清單

發布前確認：

- [ ] 所有測試通過 (`uv run pytest`)
- [ ] 程式碼檢查通過 (`uv run ruff check .`)
- [ ] 版本號已更新
- [ ] CHANGELOG.md 已更新
- [ ] README.md 已更新
- [ ] 已在 TestPyPI 測試過
- [ ] UV_PUBLISH_TOKEN 已設置
- [ ] 使用正確的 token（TestPyPI vs PyPI）

---

## 參考資源

- **TestPyPI**: https://test.pypi.org/
- **PyPI**: https://pypi.org/
- **uv 文檔**: https://docs.astral.sh/uv/
- **完整發布指南**: [PUBLISHING.md](PUBLISHING.md)
- **命令參考**: [COMMANDS.md](COMMANDS.md)
