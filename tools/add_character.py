#!/usr/bin/env python3
"""
添加自定義角色參考範本工具
支援圖片處理和配置更新
"""

import os
import sys
import yaml
import shutil
from pathlib import Path
from PIL import Image
import numpy as np
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

console = Console()

class CharacterAdder:
    def __init__(self):
        """初始化角色添加器"""
        self.config_path = Path("configs/generation_config.yaml")
        self.sprites_dir = Path("data/raw_sprites")
        self.references_dir = Path("data/references")
        
        # 確保目錄存在
        self.sprites_dir.mkdir(parents=True, exist_ok=True)
        self.references_dir.mkdir(parents=True, exist_ok=True)
        
        self.load_config()
    
    def load_config(self):
        """載入現有配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            console.print("❌ 配置文件不存在，請先運行 main.py", style="red")
            sys.exit(1)
    
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, 
                     allow_unicode=True, sort_keys=False)
        console.print("✅ 配置文件已更新", style="green")
    
    def preprocess_image(self, input_path: str, char_name: str) -> str:
        """預處理參考圖片"""
        console.print(f"🔧 處理圖片: {input_path}", style="blue")
        
        try:
            img = Image.open(input_path)
            
            # 轉換為RGBA
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 檢查尺寸
            if img.size not in [(32, 48), (256, 384)]:
                console.print(f"⚠️  圖片尺寸 {img.size} 不標準，將縮放到 32x48", style="yellow")
                img = img.resize((32, 48), Image.NEAREST)
            
            # 背景處理選項
            if Confirm.ask("是否要移除白色背景？"):
                data = np.array(img)
                # 將接近白色的像素設為透明
                white_threshold = 240
                white_pixels = (
                    (data[:, :, 0] > white_threshold) & 
                    (data[:, :, 1] > white_threshold) & 
                    (data[:, :, 2] > white_threshold)
                )
                data[white_pixels] = [0, 0, 0, 0]
                img = Image.fromarray(data, 'RGBA')
            
            # 保存處理後的圖片
            output_path = self.sprites_dir / f"{char_name}_reference.png"
            img.save(output_path, 'PNG')
            
            console.print(f"✅ 圖片已保存到: {output_path}", style="green")
            return str(output_path)
            
        except Exception as e:
            console.print(f"❌ 圖片處理失敗: {e}", style="red")
            return None
    
    def add_character_template(self, char_name: str, positive_prompt: str, 
                             style: str, negative_prompt: str = ""):
        """添加角色模板到配置"""
        if 'prompts' not in self.config:
            self.config['prompts'] = {}
        if 'character_templates' not in self.config['prompts']:
            self.config['prompts']['character_templates'] = {}
        
        char_config = {
            'positive': positive_prompt,
            'style': style
        }
        
        if negative_prompt:
            char_config['negative'] = negative_prompt
        
        self.config['prompts']['character_templates'][char_name] = char_config
        console.print(f"✅ 角色模板 '{char_name}' 已添加", style="green")
    
    def list_existing_characters(self):
        """列出現有角色"""
        templates = self.config.get('prompts', {}).get('character_templates', {})
        
        if templates:
            console.print("\n📋 現有角色模板:", style="bold blue")
            for name, config in templates.items():
                console.print(f"  • {name}: {config.get('positive', 'N/A')}", style="cyan")
        else:
            console.print("📋 目前沒有角色模板", style="yellow")
    
    def interactive_add_character(self):
        """互動式添加角色"""
        console.print(Panel.fit(
            "🎨 添加自定義角色參考範本",
            title="角色添加工具",
            border_style="magenta"
        ))
        
        # 列出現有角色
        self.list_existing_characters()
        
        # 獲取角色名稱
        char_name = Prompt.ask("\n輸入角色名稱 (英文，不含空格)")
        
        # 檢查是否已存在
        existing_templates = self.config.get('prompts', {}).get('character_templates', {})
        if char_name in existing_templates:
            if not Confirm.ask(f"角色 '{char_name}' 已存在，是否覆蓋？"):
                console.print("操作已取消", style="yellow")
                return
        
        # 圖片處理選項
        add_image = Confirm.ask("是否要添加參考圖片？")
        image_path = None
        
        if add_image:
            image_path = Prompt.ask("輸入圖片路徑")
            if not Path(image_path).exists():
                console.print("❌ 圖片文件不存在", style="red")
                return
            
            processed_path = self.preprocess_image(image_path, char_name)
            if not processed_path:
                return
        
        # 獲取提示詞信息
        console.print("\n📝 配置角色提示詞:", style="bold blue")
        
        positive_prompt = Prompt.ask(
            "正向提示詞 (描述角色外觀、裝備等)",
            default="pixel art character, side view, walking animation"
        )
        
        style = Prompt.ask(
            "風格描述",
            default="pixel art game character"
        )
        
        negative_prompt = Prompt.ask(
            "負向提示詞 (要避免的特徵，可選)",
            default=""
        )
        
        # 添加角色模板
        self.add_character_template(char_name, positive_prompt, style, negative_prompt)
        
        # 保存配置
        self.save_config()
        
        # 顯示結果
        console.print(f"\n🎉 角色 '{char_name}' 已成功添加！", style="bold green")
        
        if image_path:
            console.print(f"📷 參考圖片: {processed_path}", style="cyan")
        
        console.print(f"📝 提示詞: {positive_prompt}", style="cyan")
        console.print(f"🎨 風格: {style}", style="cyan")
        
        if negative_prompt:
            console.print(f"🚫 負向提示詞: {negative_prompt}", style="cyan")
        
        # 使用建議
        console.print(f"\n💡 使用方法:", style="bold yellow")
        console.print(f"   python main.py --generate", style="blue")
        console.print(f"   python web_ui.py", style="blue")
    
    def batch_add_from_directory(self, directory_path: str):
        """從目錄批量添加角色"""
        dir_path = Path(directory_path)
        if not dir_path.exists():
            console.print("❌ 目錄不存在", style="red")
            return
        
        image_files = list(dir_path.glob("*.png")) + list(dir_path.glob("*.jpg"))
        
        if not image_files:
            console.print("❌ 目錄中沒有找到圖片文件", style="red")
            return
        
        console.print(f"📁 找到 {len(image_files)} 個圖片文件", style="blue")
        
        for img_file in image_files:
            char_name = img_file.stem.lower().replace(" ", "_")
            
            console.print(f"\n處理: {img_file.name}", style="cyan")
            
            # 處理圖片
            processed_path = self.preprocess_image(str(img_file), char_name)
            if not processed_path:
                continue
            
            # 簡單的提示詞生成
            positive_prompt = f"pixel art character, {char_name} style, walking animation"
            style = "pixel art game character"
            
            # 添加模板
            self.add_character_template(char_name, positive_prompt, style)
            
            console.print(f"✅ {char_name} 已添加", style="green")
        
        # 保存配置
        self.save_config()
        console.print(f"\n🎉 批量添加完成，共處理 {len(image_files)} 個角色", style="bold green")

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="添加自定義角色參考範本")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="互動式添加角色")
    parser.add_argument("--batch", "-b", type=str, 
                       help="從目錄批量添加角色")
    parser.add_argument("--list", "-l", action="store_true", 
                       help="列出現有角色")
    
    args = parser.parse_args()
    
    adder = CharacterAdder()
    
    if args.list:
        adder.list_existing_characters()
    elif args.batch:
        adder.batch_add_from_directory(args.batch)
    elif args.interactive:
        adder.interactive_add_character()
    else:
        # 默認執行互動模式
        adder.interactive_add_character()

if __name__ == "__main__":
    main() 