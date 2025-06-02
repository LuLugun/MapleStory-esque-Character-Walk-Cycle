# 🎨 角色參考範本提供指南

本指南說明如何為楓之谷風格角色生成工具提供參考範本，以獲得更準確和一致的AI生成結果。

## 📋 參考範本的類型

### 1. 📷 圖像參考範本
將參考圖片放置在對應目錄中，AI會學習其風格和特徵。

#### 目錄結構：
```
data/
├── raw_sprites/           # 原始精靈圖參考
│   ├── warrior_walk_cycle.png
│   ├── archer_walk_cycle.png
│   └── custom_character.png
├── references/            # 額外參考資料
│   ├── poses/            # 姿勢參考
│   ├── style_ref/        # 風格參考
│   └── color_palette/    # 色彩參考
```

#### 圖像要求：
- **格式**: PNG (支援透明背景)
- **尺寸**: 原始32×48像素，或256×384像素
- **風格**: 像素藝術風格，清晰的輪廓
- **背景**: 透明或純色背景
- **內容**: 角色側視圖，行走姿勢

### 2. 📝 文字提示詞範本
在配置文件中定義角色的詳細描述。

#### 配置位置：`configs/generation_config.yaml`

```yaml
prompts:
  character_templates:
    # 現有角色
    warrior:
      positive: "armored warrior, sword, shield, brown hair, blue armor"
      style: "medieval fantasy"
    
    # 自定義角色範例
    ninja:
      positive: "black ninja, katana, mask, stealthy pose, dark clothing"
      style: "japanese martial arts"
    
    pirate:
      positive: "pirate captain, tricorn hat, cutlass, eyepatch, naval uniform"
      style: "maritime adventure"
    
    knight:
      positive: "holy knight, plate armor, cross symbol, golden details, righteous"
      style: "religious warrior"
```

## 🎯 提供參考範本的方法

### 方法1: 添加圖像參考

1. **準備參考圖片**
   ```bash
   # 將楓之谷角色圖片放入 raw_sprites 目錄
   cp your_character.png data/raw_sprites/
   ```

2. **圖片命名規範**
   ```
   {角色名}_walk_cycle.png    # 完整行走週期
   {角色名}_idle.png          # 待機動作
   {角色名}_reference.png     # 單張參考圖
   ```

3. **確保圖片品質**
   - 清晰的像素邊緣
   - 一致的光照和陰影
   - 符合楓之谷風格的色彩

### 方法2: 修改提示詞範本

1. **編輯配置文件**
   ```bash
   nano configs/generation_config.yaml
   ```

2. **添加新角色範本**
   ```yaml
   character_templates:
     your_character:
       positive: "詳細的角色描述, 裝備, 外觀特徵, 顏色"
       style: "風格描述"
       negative: "要避免的特徵"  # 可選
   ```

3. **提示詞撰寫技巧**
   - 使用具體的裝備描述
   - 包含顏色和材質資訊
   - 指定動作和姿勢
   - 避免過於複雜的描述

### 方法3: 使用ControlNet姿勢控制

1. **創建姿勢參考**
   ```python
   # 在 data/references/poses/ 目錄下
   # 添加 JSON 格式的姿勢定義
   {
     "keypoints": [
       {"name": "head", "x": 0.5, "y": 0.15},
       {"name": "torso", "x": 0.5, "y": 0.5},
       {"name": "left_arm", "x": 0.3, "y": 0.4},
       {"name": "right_arm", "x": 0.7, "y": 0.4}
     ]
   }
   ```

2. **姿勢控制優勢**
   - 確保動作一致性
   - 控制身體比例
   - 指定特定動作幀

## 🛠️ 實用工具和腳本

### 1. 批量添加參考範本

```python
# 創建 add_reference.py
import shutil
from pathlib import Path

def add_character_reference(char_name, image_path, description):
    # 複製圖片到參考目錄
    dest_path = f"data/raw_sprites/{char_name}_reference.png"
    shutil.copy(image_path, dest_path)
    
    # 添加到配置（需要手動編輯YAML）
    print(f"請在 configs/generation_config.yaml 中添加：")
    print(f"""
    {char_name}:
      positive: "{description}"
      style: "customize as needed"
    """)

# 使用範例
add_character_reference(
    "custom_mage", 
    "path/to/your/mage.png",
    "blue robes, staff with crystal, pointed hat, magical aura"
)
```

### 2. 參考圖片預處理

```python
# 創建 preprocess_reference.py
from PIL import Image
import numpy as np

def preprocess_reference_image(input_path, output_path):
    img = Image.open(input_path)
    
    # 確保是RGBA格式
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 縮放到標準尺寸
    target_size = (32, 48)
    img_resized = img.resize(target_size, Image.NEAREST)
    
    # 清理背景
    data = np.array(img_resized)
    # 將接近白色的像素設為透明
    white_pixels = (data[:, :, 0] > 240) & (data[:, :, 1] > 240) & (data[:, :, 2] > 240)
    data[white_pixels] = [0, 0, 0, 0]
    
    result = Image.fromarray(data, 'RGBA')
    result.save(output_path, 'PNG')
    print(f"已處理參考圖片: {output_path}")

# 使用範例
preprocess_reference_image(
    "raw_character.png", 
    "data/raw_sprites/processed_character.png"
)
```

## 📊 參考範本品質檢查

### 自動檢查腳本

```python
# 創建 validate_references.py
def validate_reference_quality(image_path):
    img = Image.open(image_path)
    
    checks = {
        "正確尺寸": img.size in [(32, 48), (256, 384)],
        "透明背景": img.mode == 'RGBA',
        "像素風格": True,  # 需要更複雜的檢測
        "清晰邊緣": True   # 需要邊緣檢測
    }
    
    print(f"參考圖片檢查結果 - {image_path}")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())

# 檢查所有參考圖片
for img_file in Path("data/raw_sprites").glob("*.png"):
    validate_reference_quality(img_file)
```

## 🎨 最佳實踐建議

### 1. 參考圖片選擇
- ✅ 選擇高品質的楓之谷官方素材
- ✅ 確保角色動作清晰可見
- ✅ 避免過於複雜的背景
- ❌ 不要使用模糊或失真的圖片

### 2. 提示詞撰寫
- ✅ 使用具體的描述詞彙
- ✅ 包含裝備和服裝細節
- ✅ 指定動作和表情
- ❌ 避免抽象或模糊的描述

### 3. 風格一致性
- ✅ 保持相同的像素密度
- ✅ 使用一致的色彩風格
- ✅ 維持楓之谷的美術風格
- ❌ 不要混合不同風格的參考

## 🚀 使用參考範本生成

添加參考範本後，使用以下命令生成：

```bash
# 生成特定角色
python main.py --generate --character your_character

# 使用Web界面選擇參考
python web_ui.py

# 批量生成所有角色
python main.py --full
```

## ❓ 常見問題

**Q: 為什麼生成的角色與參考不相似？**
A: 檢查參考圖片品質、提示詞準確性，調整guidance_scale參數。

**Q: 可以使用真實照片作為參考嗎？**
A: 不建議，AI更適合學習像素藝術風格的參考。

**Q: 如何添加全新的角色類型？**
A: 1) 添加參考圖片到raw_sprites目錄；2) 在配置文件中添加character_templates；3) 重新運行生成流程。

**Q: 參考範本會影響所有角色嗎？**
A: 不會，每個角色使用自己的參考範本和提示詞，相互獨立。

---

💡 **提示**: 高品質的參考範本是獲得理想生成結果的關鍵。建議多準備幾個不同角度和動作的參考圖片！ 