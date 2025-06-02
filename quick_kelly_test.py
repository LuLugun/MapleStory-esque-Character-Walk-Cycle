#!/usr/bin/env python3
"""
快速Kelly角色高品質生成測試
"""

import yaml
from pathlib import Path
from rich.console import Console
from scripts.pixel_art_optimizer import PixelArtOptimizer

console = Console()

def create_optimized_kelly_config():
    """創建針對Kelly優化的配置"""
    
    # 基於Kelly參考圖片的精確描述
    kelly_config = {
        'model_settings': {
            'base_model': "runwayml/stable-diffusion-v1-5",
            'scheduler': "DPMSolverMultistepScheduler"
        },
        'image_settings': {
            'width': 256,
            'height': 384,
            'original_sprite_size': [32, 48]
        },
        'generation_params': {
            'num_inference_steps': 30,
            'guidance_scale': 15.0,
            'negative_prompt_guidance_scale': 2.0
        },
        'prompts': {
            'base_positive': "masterpiece, best quality, pixel art, maplestory style character, 2d game sprite, side view walking pose, transparent background, clean sharp pixels, detailed sprite art",
            'base_negative': "blurry, low quality, 3d render, realistic, photographic, smooth gradients, antialiasing, jpeg artifacts, watermark, text, signature, malformed, distorted, extra limbs, missing limbs",
            'character_templates': {
                'kelly': {
                    'positive': "cute anime girl, shoulder-length brown hair, red hair ribbon bow, brown casual knee-length dress, red mary jane shoes, friendly smile expression, standing pose, kawaii style, chibi proportions, maplestory character design",
                    'style': "cute anime character, pixel art"
                }
            }
        },
        'controlnet': {
            'enabled': False,  # 暫時關閉ControlNet以簡化生成
            'conditioning_scale': 0.5
        }
    }
    
    return kelly_config

def generate_kelly_test():
    """生成Kelly測試角色"""
    console.print("🎯 開始Kelly高品質測試生成", style="bold magenta")
    
    try:
        # 創建優化配置
        config = create_optimized_kelly_config()
        
        # 保存配置
        config_path = Path("configs/kelly_test_config.yaml")
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        console.print("✅ Kelly測試配置已創建", style="green")
        
        # 使用新配置生成
        console.print("🎨 使用優化配置重新生成Kelly...", style="blue")
        
        # 這裡可以調用優化後的生成器
        return True
        
    except Exception as e:
        console.print(f"❌ Kelly測試生成失敗: {e}", style="red")
        return False

def manual_kelly_optimization():
    """手動Kelly圖片優化"""
    console.print("🔧 開始手動Kelly圖片優化", style="bold blue")
    
    optimizer = PixelArtOptimizer()
    
    # 檢查是否有Kelly的參考圖片
    kelly_ref = Path("data/raw_sprites/Kelly.png")
    if kelly_ref.exists():
        try:
            from PIL import Image
            
            # 載入參考圖片
            ref_image = Image.open(kelly_ref)
            console.print(f"📷 載入Kelly參考圖片: {kelly_ref}", style="cyan")
            
            # 創建多個變化版本
            for i in range(3):
                # 應用不同的優化設定
                if i == 0:
                    # 版本1：直接縮放
                    optimized = optimizer.resize_pixel_perfect(ref_image, (128, 192))
                elif i == 1:
                    # 版本2：增強色彩
                    enhanced = optimizer.enhance_colors(ref_image)
                    optimized = optimizer.resize_pixel_perfect(enhanced, (128, 192))
                else:
                    # 版本3：完整優化
                    optimized = optimizer.enhance_pixel_art_quality(ref_image, (128, 192))
                
                # 保存結果
                output_path = Path(f"output/kelly_manual_v{i+1}.png")
                output_path.parent.mkdir(exist_ok=True, parents=True)
                optimized.save(output_path, "PNG")
                
                console.print(f"✅ Kelly手動優化版本{i+1}完成: {output_path}", style="green")
            
            return True
            
        except Exception as e:
            console.print(f"❌ Kelly手動優化失敗: {e}", style="red")
            return False
    else:
        console.print("❌ 找不到Kelly參考圖片", style="red")
        return False

def show_improvement_suggestions():
    """顯示改進建議"""
    suggestions = """
🎯 Kelly角色生成品質改進建議:

1. 📷 參考圖片方面:
   • 確保Kelly.png是清晰的32×48像素圖片
   • 背景應該是透明的
   • 角色應該面向右側（標準楓之谷方向）

2. 🎨 提示詞優化:
   • 更具體的描述Kelly的服裝細節
   • 加入"pixel perfect"和"maplestory style"關鍵詞
   • 使用負向提示詞排除不需要的特徵

3. ⚙️ 生成參數調整:
   • 增加推理步驟數 (30-50步)
   • 提高guidance_scale (12-15)
   • 調整解析度為256×384

4. 🔧 後處理改進:
   • 使用專門的像素藝術濾鏡
   • 色彩量化處理
   • 邊緣銳化

5. 🚀 快速改進方案:
   • 運行手動優化: python quick_kelly_test.py
   • 使用優化配置重新生成
   • 批量處理現有圖片
    """
    
    console.print(suggestions, style="blue")

def main():
    """主函數"""
    console.print("🍁 Kelly角色品質改進工具", style="bold magenta")
    
    # 顯示改進建議
    show_improvement_suggestions()
    
    # 執行手動優化
    console.print("\n" + "="*50, style="yellow")
    if manual_kelly_optimization():
        console.print("🎉 Kelly手動優化完成！請查看 output/ 目錄", style="bold green")
    
    # 生成測試配置
    console.print("\n" + "="*50, style="yellow")
    if generate_kelly_test():
        console.print("🎉 Kelly測試配置已準備！", style="bold green")

if __name__ == "__main__":
    main() 