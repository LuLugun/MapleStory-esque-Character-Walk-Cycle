#!/usr/bin/env python3
"""
楓之谷風格角色行走圖製作工具演示腳本
展示基本功能和使用方法
"""

import os
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn

# 導入工具模組
from scripts.data_preparation import DataPreparation
from scripts.sprite_generator import SpriteGenerator
from scripts.sheet_composer import SpriteSheetComposer

console = Console()

def demo_banner():
    """顯示演示橫幅"""
    banner_text = """
🍁 楓之谷風格角色行走圖製作工具 - 演示模式 🍁

本演示將帶您體驗完整的AI生成流程：
📋 1. 資料準備 - 創建範例精靈圖
🎨 2. AI生成 - 使用Stable Diffusion生成角色
📑 3. 精靈表組合 - 製作最終遊戲素材

⚠️  注意: 這是演示版本，實際效果可能因硬體和模型而異
    """
    
    panel = Panel(
        banner_text,
        title="🎮 演示模式",
        border_style="magenta",
        padding=(1, 2)
    )
    console.print(panel)

def demo_data_preparation():
    """演示資料準備步驟"""
    console.print("\n" + "="*60, style="blue")
    console.print("📋 演示步驟 1: 資料準備", style="bold blue")
    console.print("="*60, style="blue")
    
    console.print("📝 正在創建範例資料...", style="yellow")
    
    # 創建資料準備器
    prep = DataPreparation()
    
    # 演示各個步驟
    steps = [
        ("創建範例精靈圖", prep.create_sample_sprites),
        ("放大圖片以適配AI模型", prep.upscale_sprites),
        ("提取單幀圖片", prep.extract_frames),
        ("創建姿勢參考", prep.create_pose_references)
    ]
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("資料準備中...", total=len(steps))
        
        for desc, func in steps:
            progress.update(task, description=desc)
            func()
            time.sleep(1)  # 演示延遲
            progress.advance(task)
    
    console.print("✅ 資料準備完成！", style="green")
    
    # 顯示生成的文件
    data_files = list(Path("data/processed").glob("*.png"))
    console.print(f"📁 生成了 {len(data_files)} 個處理檔案", style="cyan")

def demo_character_generation():
    """演示角色生成步驟（簡化版）"""
    console.print("\n" + "="*60, style="blue")
    console.print("🎨 演示步驟 2: AI角色生成", style="bold blue")
    console.print("="*60, style="blue")
    
    console.print("🤖 正在初始化AI模型...", style="yellow")
    console.print("💡 演示模式: 使用簡化生成流程", style="cyan")
    
    # 模擬生成過程
    characters = ["warrior", "archer", "mage"]
    frames_per_char = 8
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("生成角色中...", total=len(characters) * frames_per_char)
        
        for char in characters:
            for frame in range(frames_per_char):
                progress.update(task, description=f"生成 {char} 第 {frame+1} 幀")
                time.sleep(0.5)  # 模擬生成時間
                progress.advance(task)
                
                # 創建演示用的空白圖片
                demo_create_demo_frame(char, frame)
    
    console.print("✅ 角色生成完成！", style="green")
    console.print("📁 生成的幀圖已保存到 output/frames/", style="cyan")

def demo_create_demo_frame(character: str, frame_idx: int):
    """創建演示用的幀圖"""
    from PIL import Image, ImageDraw, ImageFont
    
    # 創建簡單的演示圖片
    img = Image.new('RGBA', (256, 384), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 繪製簡單的角色輪廓
    colors = {
        'warrior': (100, 149, 237),
        'archer': (34, 139, 34),
        'mage': (138, 43, 226)
    }
    
    color = colors.get(character, (128, 128, 128))
    
    # 繪製基本形狀
    # 頭部
    draw.ellipse([110, 30, 146, 66], fill=color)
    # 身體
    draw.rectangle([118, 66, 138, 150], fill=color)
    # 腿部（根據幀數調整位置模擬行走）
    offset = int(10 * (frame_idx % 4 - 2))
    draw.rectangle([115 + offset, 150, 125 + offset, 200], fill=color)
    draw.rectangle([131 - offset, 150, 141 - offset, 200], fill=color)
    
    # 添加文字標籤
    try:
        font = ImageFont.load_default()
        draw.text((10, 10), f"{character} #{frame_idx}", fill=(255, 255, 255), font=font)
    except:
        pass
    
    # 保存圖片
    output_dir = Path("output/frames")
    output_dir.mkdir(exist_ok=True, parents=True)
    img.save(output_dir / f"{character}_frame_{frame_idx:02d}.png", "PNG")

def demo_sprite_sheet_composition():
    """演示精靈表組合步驟"""
    console.print("\n" + "="*60, style="blue")
    console.print("📑 演示步驟 3: 精靈表組合", style="bold blue")
    console.print("="*60, style="blue")
    
    console.print("🔧 正在組合精靈表...", style="yellow")
    
    # 創建精靈表組合器
    composer = SpriteSheetComposer()
    
    # 組合所有角色的精靈表
    characters = ["warrior", "archer", "mage"]
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("組合精靈表中...", total=len(characters) + 1)
        
        for char in characters:
            progress.update(task, description=f"組合 {char} 精靈表")
            composer.compose_character_sheet(char)
            time.sleep(1)
            progress.advance(task)
        
        # 創建主精靈表
        progress.update(task, description="創建主精靈表")
        composer.create_master_sheet()
        progress.advance(task)
    
    console.print("✅ 精靈表組合完成！", style="green")
    
    # 顯示輸出結果
    show_demo_results()

def show_demo_results():
    """顯示演示結果"""
    console.print("\n📊 演示結果總覽:", style="bold cyan")
    
    output_dir = Path("output")
    
    # 統計文件
    if (output_dir / "frames").exists():
        frame_count = len(list((output_dir / "frames").glob("*.png")))
        console.print(f"🎞️  生成幀圖: {frame_count} 張", style="green")
    
    if (output_dir / "sprite_sheets").exists():
        sheet_count = len(list((output_dir / "sprite_sheets").glob("*_sprite_sheet.png")))
        metadata_count = len(list((output_dir / "sprite_sheets").glob("*_metadata.json")))
        console.print(f"📑 精靈表: {sheet_count} 個", style="green")
        console.print(f"📋 元數據: {metadata_count} 個", style="green")
    
    console.print("\n📁 輸出文件位置:", style="bold blue")
    console.print("   • 單幀圖片: output/frames/", style="cyan")
    console.print("   • 精靈表: output/sprite_sheets/", style="cyan")
    console.print("   • 元數據: output/sprite_sheets/*_metadata.json", style="cyan")

def demo_cleanup():
    """演示清理"""
    console.print("\n🧹 演示完成，正在清理資源...", style="yellow")
    time.sleep(1)
    console.print("✅ 清理完成", style="green")

def run_full_demo():
    """執行完整演示"""
    demo_banner()
    
    # 詢問用戶是否繼續
    console.print("\n是否開始演示？ (y/n): ", style="bold yellow", end="")
    
    try:
        choice = input().lower()
        if choice not in ['y', 'yes', '是', '']:
            console.print("演示已取消", style="red")
            return
    except KeyboardInterrupt:
        console.print("\n演示已中斷", style="red")
        return
    
    try:
        # 執行演示步驟
        demo_data_preparation()
        demo_character_generation()
        demo_sprite_sheet_composition()
        
        # 顯示完成信息
        console.print("\n" + "="*60, style="green")
        console.print("🎉 演示完成！", style="bold green")
        console.print("="*60, style="green")
        
        console.print("""
📚 下一步:
1. 安裝完整依賴: pip install -r requirements.txt
2. 運行真實生成: python main.py --full
3. 啟動Web界面: python web_ui.py
4. 查看詳細說明: python main.py --help-detail

💡 提示: 實際生成需要GPU支援和完整的AI模型
        """, style="blue")
        
    except KeyboardInterrupt:
        console.print("\n演示已中斷", style="yellow")
    except Exception as e:
        console.print(f"\n演示過程中發生錯誤: {e}", style="red")
    finally:
        demo_cleanup()

if __name__ == "__main__":
    run_full_demo() 