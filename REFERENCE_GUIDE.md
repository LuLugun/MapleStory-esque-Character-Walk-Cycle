# 🎨 楓之谷風格角色參考範本完整指南

## 📋 提供角色參考範本的三種主要方法

### 🔥 方法1: 圖像參考範本（推薦）

將楓之谷風格的參考圖片放入專案目錄，AI會學習其視覺特徵。

**步驟：**
1. 準備32×48像素的楓之谷角色圖片
2. 放入 `data/raw_sprites/` 目錄
3. 命名格式：`{角色名}_reference.png` 或 `{角色名}_walk_cycle.png`

**範例：**
```bash
# 將參考圖片複製到指定位置
cp my_knight.png data/raw_sprites/knight_reference.png
```

### 🔥 方法2: 文字提示詞範本（最靈活）

通過詳細的文字描述來指導AI生成特定風格的角色。

**編輯位置：** `configs/generation_config.yaml`

**格式：**
```yaml
character_templates:
  角色名:
    positive: "正向描述詞，裝備，外觀，顏色等"
    style: "風格類型"
    negative: "要避免的特徵（可選）"
```

**實際範例：**
```yaml
character_templates:
  ninja:
    positive: "black ninja, katana, mask, dark clothing, stealthy pose"
    style: "japanese martial arts"
  
  pirate:
    positive: "pirate captain, tricorn hat, cutlass, eyepatch, naval uniform"
    style: "maritime adventure"
```

### 🔥 方法3: 工具輔助添加（最簡單）

使用專門的工具腳本來添加角色參考。

**使用方法：**
```bash
# 互動式添加角色
python3 tools/add_character.py --interactive

# 批量從目錄添加
python3 tools/add_character.py --batch /path/to/images/

# 列出現有角色
python3 tools/add_character.py --list
```

## 🎯 當前已支援的角色範本

我們已經為您預設了6種角色類型：

| 角色 | 描述 | 風格 |
|------|------|------|
| **戰士 (warrior)** | 重甲戰士，劍盾配備 | 中世紀奇幻 |
| **弓箭手 (archer)** | 輕裝射手，弓箭裝備 | 森林遊俠 |
| **法師 (mage)** | 魔法師，法杖和長袍 | 奇幻魔法 |
| **忍者 (ninja)** | 黑衣忍者，武士刀配備 | 日式武術 |
| **海盜 (pirate)** | 海盜船長，三角帽眼罩 | 海洋冒險 |
| **騎士 (knight)** | 聖騎士，板甲十字標誌 | 宗教戰士 |

## 🔧 提示詞撰寫技巧

### ✅ 好的提示詞範例：
```yaml
positive: "armored paladin, silver plate armor, holy sword, white cape, golden cross emblem, righteous pose"
```
**特點：** 具體裝備 + 顏色 + 材質 + 姿勢

### ❌ 不良提示詞範例：
```yaml
positive: "cool character, awesome, epic"
```
**問題：** 過於抽象，缺乏具體描述

### 📝 提示詞構成要素：

1. **基礎描述**：角色職業/類型
2. **裝備細節**：武器、防具、配件
3. **顏色資訊**：主要色彩搭配
4. **風格修飾**：材質、圖案、特殊效果
5. **動作姿勢**：standing, walking, battle pose

## 🎨 實際使用範例

### 添加新角色："魔劍士"

**1. 配置提示詞：**
```yaml
magic_swordsman:
  positive: "magic swordsman, enchanted blade, mystical armor, purple energy aura, spell casting pose"
  style: "fantasy magic warrior"
  negative: "modern clothing, guns, technology"
```

**2. 生成角色：**
```bash
python3 main.py --generate
# 或使用Web界面
python3 web_ui.py
```

### 使用自己的參考圖片

**1. 準備圖片：**
- 確保是32×48像素的像素藝術
- PNG格式，透明背景
- 清晰的角色輪廓

**2. 放置文件：**
```bash
cp custom_character.png data/raw_sprites/custom_reference.png
```

**3. 配置提示詞：**
```yaml
custom:
  positive: "基於您圖片的具體描述"
  style: "pixel art game character"
```

## 🚀 高級技巧

### 1. 組合式角色設計
```yaml
battle_mage:
  positive: "battle mage, staff and sword combo, leather and cloth armor mix, elemental magic effects"
  style: "hybrid warrior-mage"
```

### 2. 特定色彩主題
```yaml
ice_warrior:
  positive: "ice warrior, blue crystal armor, frost sword, white cape, ice magic aura, cold breath effect"
  style: "ice elemental theme"
```

### 3. 文化風格融合
```yaml
samurai_monk:
  positive: "samurai monk, traditional robes, katana, prayer beads, temple warrior, zen meditation pose"
  style: "japanese spiritual warrior"
```

## 🎮 生成和測試

添加角色參考後，您可以通過以下方式測試生成效果：

### 命令行方式：
```bash
# 完整流程
python3 main.py --full

# 僅生成
python3 main.py --generate

# 僅組合精靈表
python3 main.py --compose
```

### Web界面方式：
```bash
python3 web_ui.py
# 在瀏覽器中打開 http://localhost:7860
```

### 快速啟動：
```bash
bash run.sh
# 選擇相應的操作選項
```

## 📊 品質優化建議

### 參考圖片品質：
- ✅ 32×48或256×384像素
- ✅ 清晰的像素邊緣
- ✅ 透明背景
- ✅ 楓之谷風格色彩

### 提示詞優化：
- ✅ 具體而詳細的描述
- ✅ 包含顏色和材質
- ✅ 指定動作和姿勢
- ✅ 避免過於複雜的描述

### 生成參數調整：
```yaml
generation_params:
  guidance_scale: 7.5      # 增加以更貼近提示詞
  num_inference_steps: 25  # 增加以提高品質
```

## 🛠️ 故障排除

### 常見問題：

**Q: 生成的角色與參考不相似？**
A: 
1. 檢查參考圖片品質
2. 調整提示詞更具體
3. 增加guidance_scale參數

**Q: 角色細節不清晰？**
A: 
1. 增加num_inference_steps
2. 確保參考圖片清晰
3. 調整負向提示詞排除模糊特徵

**Q: 顏色不正確？**
A: 
1. 在提示詞中明確指定顏色
2. 檢查參考圖片的色彩
3. 添加色彩相關的關鍵詞

## 🎉 開始使用

現在您已經了解了完整的參考範本提供方法！選擇最適合您的方式：

1. **初學者**：直接修改`configs/generation_config.yaml`中的提示詞
2. **進階用戶**：使用`tools/add_character.py`工具
3. **專業用戶**：結合圖片參考和詳細提示詞

立即開始創造您的楓之谷風格角色吧！ 🍁✨ 