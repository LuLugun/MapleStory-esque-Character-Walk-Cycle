# 楓之谷風格角色行走圖製作專案

🍁 **MapleStory-esque Character Walk Cycle Generator**

使用 **生成式 AI** 技術製作楓之谷風格角色行走動畫的完整工具包，支援多種角色類型、參考圖片指導生成，以及專業的像素藝術後處理。

## ✨ 主要特色

- 🤖 **AI驅動生成**：集成 Stable Diffusion + ControlNet
- 🎯 **多角色支援**：戰士、法師、弓箭手、忍者、海盜、騎士
- 🖼️ **參考圖片指導**：使用您的角色圖片生成一致的動畫
- 🎨 **像素藝術優化**：專業的像素藝術後處理流程
- 💻 **多種界面**：Web界面、命令行、演示模式
- 📋 **精靈表自動組合**：支援多種布局格式
- 🛠️ **完整工具鏈**：從資料準備到最終輸出

## 🚀 快速開始

### 環境安裝

```bash
# 克隆專案
git clone https://github.com/LuLugun/MapleStory-esque-Character-Walk-Cycle.git
cd MapleStory-esque-Character-Walk-Cycle

# 安裝依賴
pip install -r requirements.txt

# 快速啟動 (自動檢查環境)
chmod +x run.sh
./run.sh
```

### 基本使用

#### 方法1：Web界面 (推薦新手)
```bash
python web_ui.py
```
然後在瀏覽器開啟 http://localhost:7860

#### 方法2：命令行界面
```bash
# 生成指定角色
python main.py --character warrior --output-dir output/warrior

# 使用參考圖片生成
python main.py --reference data/raw_sprites/Kelly.png --character kelly

# 完整流程演示
python main.py --full --demo
```

#### 方法3：Kelly專用生成器
```bash
# 基於Kelly.png創建完整動畫
python create_kelly_sprites.py
```

## 📁 專案結構

```
MapleStory-esque-Character-Walk-Cycle/
├── 🎮 主要腳本
│   ├── main.py                     # 命令行主界面
│   ├── web_ui.py                   # Gradio Web界面
│   ├── demo.py                     # 功能演示
│   ├── demo_simple.py              # 簡化演示
│   └── create_kelly_sprites.py     # Kelly專用生成器
│
├── 📜 腳本模組
│   ├── scripts/
│   │   ├── data_preparation.py     # 資料預處理
│   │   ├── sprite_generator.py     # AI角色生成核心
│   │   ├── sheet_composer.py       # 精靈表組合器
│   │   ├── pixel_art_optimizer.py  # 像素藝術優化器
│   │   └── reference_guided_generator.py # 參考圖片指導生成
│   │
│   └── tools/
│       └── add_character.py        # 角色添加工具
│
├── ⚙️ 配置文件
│   ├── configs/
│   │   ├── generation_config.yaml  # 生成參數配置
│   │   ├── models_config.yaml      # 模型配置
│   │   └── kelly_test_config.yaml  # Kelly測試配置
│   │
├── 📚 資料目錄
│   ├── data/
│   │   ├── raw_sprites/            # 原始參考圖片
│   │   ├── processed/              # 處理後素材
│   │   └── references/             # 姿勢參考資料
│   │
├── 🤖 AI模型 (需要下載)
│   ├── models/
│   │   ├── checkpoints/            # Stable Diffusion檢查點
│   │   ├── lora/                   # 像素藝術LoRA模型
│   │   └── controlnet/             # ControlNet模型
│   │
├── 📤 輸出目錄
│   ├── output/
│   │   ├── frames/                 # 生成的單幀圖片
│   │   ├── sprite_sheets/          # 組合的精靈表
│   │   ├── kelly_sprites/          # Kelly專用輸出
│   │   └── reference_guided/       # 參考指導生成結果
│   │
└── 📖 文檔
    ├── docs/
    │   └── reference_guide.md      # 詳細技術指南
    ├── REFERENCE_GUIDE.md          # 使用指南
    └── README.md                   # 本文件
```

## 🎯 支援的角色類型

| 角色類型 | 描述 | 特色裝備 |
|---------|------|----------|
| **warrior** | 重甲戰士 | 劍盾、板甲 |
| **archer** | 輕裝射手 | 弓箭、皮甲 |
| **mage** | 魔法師 | 法杖、長袍 |
| **ninja** | 忍者 | 武士刀、黑衣 |
| **pirate** | 海盜船長 | 三角帽、眼罩 |
| **knight** | 聖騎士 | 聖劍、十字紋章 |

## 🔧 高級功能

### 添加自定義角色
```bash
# 互動式添加新角色
python tools/add_character.py

# 或手動編輯 configs/generation_config.yaml
```

### 像素藝術優化
```bash
# 對生成的圖片進行像素藝術優化
python scripts/pixel_art_optimizer.py --input output/frames/ --output output/optimized/
```

### 批量處理
```bash
# 批量生成多個角色
python main.py --characters warrior,mage,archer --batch
```

## 📋 配置說明

### 生成參數 (configs/generation_config.yaml)
- `num_inference_steps`: 推理步數 (推薦30-50)
- `guidance_scale`: 指導強度 (推薦7.5-12.0)
- `image_size`: 輸出尺寸 (推薦256x384)
- `frame_count`: 動畫幀數 (推薦8幀)

### 角色模板
每個角色都有詳細的提示詞模板，包含：
- 基礎外觀描述
- 裝備細節
- 顏色配置
- 動作姿勢

## 🎨 使用流程

1. **準備參考圖片** (可選)
   - 將32×48像素的楓之谷角色圖片放入 `data/raw_sprites/`

2. **選擇生成方式**
   - 使用內建角色模板
   - 或提供自定義參考圖片

3. **執行生成**
   - Web界面：調整參數並點擊生成
   - 命令行：執行相應指令

4. **後處理優化**
   - 自動進行像素藝術優化
   - 組合成精靈表格式

5. **匯出結果**
   - 單幀PNG圖片
   - 完整精靈表
   - JSON元數據

## 🛠️ 技術架構

- **AI引擎**: Stable Diffusion 1.5/XL
- **控制技術**: ControlNet (OpenPose, Reference)
- **像素風格**: 專用LoRA模型
- **後處理**: PIL + OpenCV + scikit-image
- **界面框架**: Gradio + Rich Console
- **配置管理**: YAML + OmegaConf

## 📊 輸出格式

### 單幀圖片
- 格式：PNG (支援透明背景)
- 尺寸：32×48 到 512×512 可選
- 命名：`{角色名}_frame_{幀數:02d}.png`

### 精靈表
- 水平排列：8幀一行
- 網格排列：2×4 或 4×2
- 帶標註版本：包含幀數標記
- JSON元數據：包含動畫時序資訊

## 🎯 效能建議

- **GPU推薦**: NVIDIA RTX 3060 或以上
- **記憶體**: 最少8GB，推薦16GB
- **硬碟**: 預留10GB以上空間存放模型
- **CPU**: 支援MPS的Apple Silicon也可以運行

## 📄 版權聲明

本專案僅供學術研究和個人學習使用。楓之谷相關美術資產版權歸 Nexon 所有。

**注意事項**：
- ✅ 個人學習和研究使用
- ✅ 開源貢獻和改進
- ❌ 商業用途和販售
- ❌ 侵犯原作版權

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 本專案
2. 創建功能分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -am '添加新功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 創建 Pull Request

## 📚 參考資源

- [The Spriters Resource](https://www.spriters-resource.com/pc_computer/maplestory/) - 楓之谷素材資源
- [Hugging Face Diffusers](https://huggingface.co/docs/diffusers) - AI模型文檔
- [ControlNet](https://github.com/lllyasviel/ControlNet) - 姿勢控制技術
- [Aseprite](https://www.aseprite.org/) - 像素藝術編輯器

## 🐛 故障排除

### 常見問題
1. **模型下載失敗**: 檢查網路連接和硬碟空間
2. **記憶體不足**: 降低batch size或圖片尺寸
3. **生成效果不佳**: 調整guidance_scale和inference_steps
4. **角色不一致**: 使用reference_guided_generator.py

詳細故障排除請參考 [REFERENCE_GUIDE.md](REFERENCE_GUIDE.md)

---

**�� 立即開始創作您的楓之谷風格角色！** 