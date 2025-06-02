# 楓之谷風格角色行走圖製作專案

## 專案概述

本專案使用 **生成式 AI** 快速製作「楓之谷風格」的 **行走圖（Walk Cycle Sprite Sheet）**，包含模型選擇、資料準備、AI 控制技術與後製組板。

## 專案結構

```
PsMCP/
├── data/                    # 資料目錄
│   ├── raw_sprites/         # 原始楓之谷素材
│   ├── processed/           # 處理後的素材
│   └── references/          # 參考圖片
├── models/                  # AI 模型相關
│   ├── checkpoints/         # SD 檢查點
│   ├── lora/               # LoRA 模型
│   └── controlnet/         # ControlNet 模型
├── scripts/                # 自動化腳本
│   ├── data_preparation.py  # 資料預處理
│   ├── sprite_generator.py  # 角色生成
│   └── sheet_composer.py    # 拼版組合
├── output/                 # 輸出結果
│   ├── frames/             # 單幀圖片
│   └── sprite_sheets/      # 最終拼版
├── configs/                # 配置文件
│   ├── generation_config.yaml
│   └── models_config.yaml
└── requirements.txt        # 依賴套件

```

## 重點摘要

1. **資料來源**：蒐集楓之谷角色像素圖，僅用於學術／個人研究
2. **模型選擇**：Stable Diffusion 1.5/XL + 像素藝術 LoRA
3. **角色一致性**：ControlNet (OpenPose/Reference-Only) 或 AnimateDiff
4. **產生流程**：8~12 張範例走路幀 → 上取樣 → AI 生成 → 拼版
5. **自動化**：ComfyUI/自訂工作流一鍵生成

## 快速開始

1. 安裝依賴：`pip install -r requirements.txt`
2. 準備資料：`python scripts/data_preparation.py`
3. 生成角色：`python scripts/sprite_generator.py`
4. 組合拼版：`python scripts/sheet_composer.py`

## 版權聲明

楓之谷美術屬於 Nexon 著作財產；本專案僅作個人研究或學習用途，不可直接販售或發佈素材。

## 參考資源

- [The Spriters Resource](https://www.spriters-resource.com/pc_computer/maplestory/)
- [Pixel-Art Sprite Sheet SD 模型](https://www.reddit.com/r/StableDiffusion/comments/yj1kbi/ive_trained_a_new_model_to_output_pixel_art/)
- [ControlNet GitHub](https://github.com/lllyasviel/ControlNet)
- [Aseprite 官方文檔](https://www.aseprite.org/docs/sprite-sheet/) 