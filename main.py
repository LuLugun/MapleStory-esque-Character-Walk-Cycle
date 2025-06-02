#!/usr/bin/env python3
"""
楓之谷風格角色行走圖製作主程式
整合完整的AI生成流程
"""

import argparse
import sys
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# 導入自定義模組
from scripts.data_preparation import DataPreparation
from scripts.sprite_generator import SpriteGenerator
from scripts.sheet_composer import SpriteSheetComposer

console = Console()

def show_banner():
    """顯示程式標題"""
    banner = Text()
    banner.append("🍁 楓之谷風格角色行走圖製作工具 🍁\n", style="bold magenta")
    banner.append("使用生成式AI快速製作像素藝術角色動畫", style="cyan")
    
    panel = Panel(
        banner,
        title="MapleStory Style Sprite Generator",
        border_style="green",
        padding=(1, 2)
    )
    console.print(panel)

def setup_character_reference(reference_image: str, character_name: str):
    """設置角色參考圖片"""
    reference_path = Path(reference_image)
    if not reference_path.exists():
        console.print(f"❌ 參考圖片不存在: {reference_image}", style="red")
        return False
    
    # 確保目錄存在
    sprites_dir = Path("data/raw_sprites")
    sprites_dir.mkdir(parents=True, exist_ok=True)
    
    # 複製參考圖片到正確位置
    target_path = sprites_dir / f"{character_name}_reference.png"
    shutil.copy2(reference_path, target_path)
    
    console.print(f"✅ 參考圖片已設置: {target_path}", style="green")
    return True

def run_full_pipeline(character_name: str = None, reference_image: str = None):
    """執行完整的製作流程"""
    console.print("🚀 開始完整的角色行走圖製作流程", style="bold blue")
    
    # 如果指定了參考圖片，先設置
    if reference_image and character_name:
        if not setup_character_reference(reference_image, character_name):
            return False
    
    try:
        # 步驟1: 資料準備
        console.print("\n" + "="*50, style="yellow")
        console.print("📋 步驟 1/3: 資料準備", style="bold yellow")
        console.print("="*50, style="yellow")
        
        prep = DataPreparation()
        prep.run_all()
        
        # 步驟2: AI生成角色
        console.print("\n" + "="*50, style="yellow")
        console.print("🎨 步驟 2/3: AI角色生成", style="bold yellow")
        console.print("="*50, style="yellow")
        
        generator = SpriteGenerator()
        try:
            if character_name:
                # 生成指定角色
                generator.generate_single_character(character_name)
            else:
                # 生成所有角色
                generator.generate_all_characters()
        finally:
            generator.cleanup()
        
        # 步驟3: 組合精靈表
        console.print("\n" + "="*50, style="yellow")
        console.print("📑 步驟 3/3: 精靈表組合", style="bold yellow")
        console.print("="*50, style="yellow")
        
        composer = SpriteSheetComposer()
        if character_name:
            composer.compose_character_sheet(character_name)
        else:
            composer.compose_all_sheets()
        
        # 完成
        console.print("\n" + "="*50, style="green")
        console.print("🎉 完整流程執行完成！", style="bold green")
        console.print("="*50, style="green")
        
        # 顯示結果
        show_results()
        
    except Exception as e:
        console.print(f"\n❌ 流程執行失敗: {e}", style="red")
        return False
    
    return True

def run_data_prep_only():
    """僅執行資料準備"""
    console.print("📋 執行資料準備流程", style="bold blue")
    prep = DataPreparation()
    prep.run_all()

def run_generation_only(character_name: str = None, reference_image: str = None):
    """僅執行AI生成"""
    console.print("🎨 執行AI生成流程", style="bold blue")
    
    # 如果指定了參考圖片，先設置
    if reference_image and character_name:
        if not setup_character_reference(reference_image, character_name):
            return False
    
    generator = SpriteGenerator()
    try:
        if character_name:
            # 生成指定角色
            console.print(f"🎯 生成角色: {character_name}", style="cyan")
            generator.generate_single_character(character_name)
        else:
            # 生成所有角色
            generator.generate_all_characters()
    finally:
        generator.cleanup()

def run_composition_only(character_name: str = None):
    """僅執行精靈表組合"""
    console.print("📑 執行精靈表組合流程", style="bold blue")
    composer = SpriteSheetComposer()
    if character_name:
        composer.compose_character_sheet(character_name)
    else:
        composer.compose_all_sheets()

def show_results():
    """顯示生成結果"""
    console.print("\n📊 生成結果:", style="bold cyan")
    
    # 檢查輸出目錄
    output_dir = Path("output")
    if not output_dir.exists():
        console.print("❌ 輸出目錄不存在", style="red")
        return
    
    # 統計文件
    frames_dir = output_dir / "frames"
    sheets_dir = output_dir / "sprite_sheets"
    
    if frames_dir.exists():
        frame_count = len(list(frames_dir.glob("*.png")))
        console.print(f"🎞️  生成幀數: {frame_count}", style="green")
    
    if sheets_dir.exists():
        sheet_count = len(list(sheets_dir.glob("*_sprite_sheet.png")))
        metadata_count = len(list(sheets_dir.glob("*_metadata.json")))
        console.print(f"📑 精靈表: {sheet_count} 個", style="green")
        console.print(f"📋 元數據: {metadata_count} 個", style="green")
        
        # 列出精靈表文件
        console.print("\n📁 生成的精靈表:", style="bold cyan")
        for sheet_file in sorted(sheets_dir.glob("*_sprite_sheet.png")):
            if "annotated" not in sheet_file.name:
                console.print(f"   ✨ {sheet_file.name}", style="cyan")

def show_help():
    """顯示幫助信息"""
    help_text = """
🔧 使用方法:

1. 完整流程 (推薦):
   python main.py --full

2. 使用參考圖片生成指定角色:
   python main.py --full --reference path/to/image.png --character kelly
   python main.py --generate --reference Kelly.png --character kelly

3. 分步執行:
   python main.py --data-prep     # 僅資料準備
   python main.py --generate      # 僅AI生成
   python main.py --compose       # 僅精靈表組合

4. 指定角色操作:
   python main.py --generate --character kelly     # 僅生成kelly角色
   python main.py --compose --character kelly      # 僅組合kelly的精靈表

5. 其他選項:
   python main.py --help          # 顯示此幫助
   python main.py --results       # 顯示當前結果

🎯 參考圖片使用建議:
   • 圖片格式: PNG (支援透明背景)
   • 建議尺寸: 32×48 或 256×384 像素
   • 風格: 像素藝術，楓之谷風格
   • 角色朝向: 側視圖

📚 更多信息請查看 README.md
    """
    console.print(help_text, style="blue")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="楓之谷風格角色行走圖製作工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--full", action="store_true", 
                       help="執行完整流程 (資料準備 -> AI生成 -> 精靈表組合)")
    parser.add_argument("--data-prep", action="store_true", 
                       help="僅執行資料準備")
    parser.add_argument("--generate", action="store_true", 
                       help="僅執行AI生成")
    parser.add_argument("--compose", action="store_true", 
                       help="僅執行精靈表組合")
    parser.add_argument("--results", action="store_true", 
                       help="顯示當前結果")
    parser.add_argument("--help-detail", action="store_true", 
                       help="顯示詳細幫助")
    
    # 新增參數：指定參考圖片和角色名稱
    parser.add_argument("--reference", "-r", type=str,
                       help="指定參考圖片路徑")
    parser.add_argument("--character", "-c", type=str,
                       help="指定要生成的角色名稱")
    
    args = parser.parse_args()
    
    # 顯示標題
    show_banner()
    
    # 參數驗證
    if args.reference and not args.character:
        console.print("❌ 使用 --reference 時必須同時指定 --character", style="red")
        return
    
    # 如果沒有參數，顯示幫助
    if len(sys.argv) == 1:
        console.print("💡 請使用 --help 查看使用方法", style="yellow")
        show_help()
        return
    
    # 執行對應功能
    if args.help_detail:
        show_help()
    elif args.full:
        run_full_pipeline(args.character, args.reference)
    elif args.data_prep:
        run_data_prep_only()
    elif args.generate:
        run_generation_only(args.character, args.reference)
    elif args.compose:
        run_composition_only(args.character)
    elif args.results:
        show_results()
    else:
        console.print("❌ 未知的選項，請使用 --help 查看使用方法", style="red")

if __name__ == "__main__":
    main() 