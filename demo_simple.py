#!/usr/bin/env python3
"""
楓之谷風格角色行走圖製作工具簡化演示腳本
展示基本功能和使用方法（無需AI模型）
"""

import os
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
import yaml

# 嘗試導入rich，如果沒有則使用基本print
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn
    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False

def print_rich(text, style=None):
    """兼容的打印函數"""
    if HAS_RICH and console:
        console.print(text, style=style)
    else:
        print(text)

def demo_banner():
    """顯示演示橫幅"""
    banner_text = """
🍁 楓之谷風格角色行走圖製作工具 - 簡化演示模式 🍁

本演示將帶您體驗完整的AI生成流程：
📋 1. 資料準備 - 創建範例精靈圖
🎨 2. AI生成模擬 - 創建示例角色幀
📑 3. 精靈表組合 - 製作最終遊戲素材

⚠️  注意: 這是簡化演示版本，無需AI模型依賴
    """
    
    if HAS_RICH and console:
        panel = Panel(
            banner_text,
            title="🎮 簡化演示模式",
            border_style="magenta",
            padding=(1, 2)
        )
        console.print(panel)
    else:
        print("=" * 60)
        print(banner_text)
        print("=" * 60)

def ensure_directories():
    """確保必要的目錄存在"""
    dirs = [
        "data/raw_sprites",
        "data/processed", 
        "data/processed/frames",
        "data/references/poses",
        "output/frames",
        "output/sprite_sheets"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def demo_data_preparation():
    """演示資料準備步驟"""
    print_rich("\n" + "="*60, "blue")
    print_rich("📋 演示步驟 1: 資料準備", "bold blue")
    print_rich("="*60, "blue")
    
    print_rich("📝 正在創建範例資料...", "yellow")
    
    # 確保目錄存在
    ensure_directories()
    
    # 演示各個步驟
    steps = [
        "創建範例精靈圖",
        "放大圖片以適配AI模型", 
        "提取單幀圖片",
        "創建姿勢參考"
    ]
    
    for i, step in enumerate(steps):
        print_rich(f"⏳ {step}...", "cyan")
        time.sleep(1)  # 模擬處理時間
        
        # 實際創建一些示例文件
        if i == 0:  # 創建範例精靈圖
            create_sample_sprites()
        elif i == 1:  # 放大圖片
            upscale_sample_sprites()
        elif i == 2:  # 提取單幀
            extract_sample_frames()
        elif i == 3:  # 創建姿勢參考
            create_pose_references()
    
    print_rich("✅ 資料準備完成！", "green")
    
    # 顯示生成的文件
    data_files = list(Path("data/processed").glob("*.png"))
    print_rich(f"📁 生成了 {len(data_files)} 個處理檔案", "cyan")

def create_sample_sprites():
    """創建範例精靈圖"""
    characters = ["warrior", "archer", "mage"]
    colors = {
        'warrior': (100, 149, 237),
        'archer': (34, 139, 34), 
        'mage': (138, 43, 226)
    }
    
    for char_type in characters:
        # 創建8幀的行走動畫
        sheet_width = 32 * 8  # 8幀，每幀32像素寬
        sheet_height = 48
        
        sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
        
        for frame in range(8):
            # 創建簡單的角色輪廓
            frame_img = Image.new('RGBA', (32, 48), (0, 0, 0, 0))
            draw = ImageDraw.Draw(frame_img)
            
            color = colors[char_type]
            
            # 基本人形
            # 頭部
            draw.ellipse([12, 4, 20, 12], fill=color)
            # 身體
            draw.rectangle([14, 12, 18, 28], fill=color)
            # 腿部（根據幀數調整模擬行走）
            offset = int(2 * (frame % 4 - 2))
            draw.rectangle([13 + offset, 28, 15 + offset, 40], fill=color)
            draw.rectangle([17 - offset, 28, 19 - offset, 40], fill=color)
            
            # 貼到精靈表上
            sprite_sheet.paste(frame_img, (frame * 32, 0))
        
        # 保存精靈表
        sprite_sheet.save(f"data/raw_sprites/{char_type}_walk_cycle.png")

def upscale_sample_sprites():
    """放大範例精靈圖"""
    for sprite_file in Path("data/raw_sprites").glob("*.png"):
        img = Image.open(sprite_file)
        # 放大8倍 (32x48 -> 256x384)
        upscaled = img.resize((img.width * 8, img.height * 8), Image.NEAREST)
        upscaled.save(f"data/processed/upscaled_{sprite_file.name}")

def extract_sample_frames():
    """提取單幀圖片"""
    frames_dir = Path("data/processed/frames")
    frames_dir.mkdir(exist_ok=True)
    
    for sprite_file in Path("data/processed").glob("upscaled_*.png"):
        sheet = Image.open(sprite_file)
        frame_width = 256  # 放大後的寬度
        frame_height = 384  # 放大後的高度
        frames_count = sheet.width // frame_width
        
        char_name = sprite_file.stem.replace("upscaled_", "").replace("_walk_cycle", "")
        
        for i in range(frames_count):
            left = i * frame_width
            frame = sheet.crop((left, 0, left + frame_width, frame_height))
            frame.save(frames_dir / f"{char_name}_frame_{i:02d}.png")

def create_pose_references():
    """創建姿勢參考文件"""
    pose_dir = Path("data/references/poses")
    pose_dir.mkdir(exist_ok=True)
    
    # 創建基本的行走姿勢JSON
    for i in range(8):
        pose_data = {
            "frame": i,
            "keypoints": [
                {"name": "head", "x": 0.5, "y": 0.15},
                {"name": "torso", "x": 0.5, "y": 0.5},
                {"name": "left_leg", "x": 0.4, "y": 0.8},
                {"name": "right_leg", "x": 0.6, "y": 0.8}
            ],
            "walk_phase": i / 8.0
        }
        
        with open(pose_dir / f"walk_pose_{i:02d}.json", 'w') as f:
            json.dump(pose_data, f, indent=2)

def demo_character_generation():
    """演示角色生成步驟（簡化版）"""
    print_rich("\n" + "="*60, "blue")
    print_rich("🎨 演示步驟 2: AI角色生成模擬", "bold blue")
    print_rich("="*60, "blue")
    
    print_rich("🤖 模擬AI模型初始化...", "yellow")
    print_rich("💡 演示模式: 創建示例角色幀", "cyan")
    
    characters = ["warrior", "archer", "mage"]
    frames_per_char = 8
    
    total_frames = len(characters) * frames_per_char
    
    for i, char in enumerate(characters):
        print_rich(f"🎨 生成 {char} 角色...", "blue")
        
        for frame in range(frames_per_char):
            print_rich(f"  ⏳ 生成第 {frame+1}/{frames_per_char} 幀", "cyan")
            time.sleep(0.3)  # 模擬生成時間
            
            # 創建演示用的幀圖
            create_demo_frame(char, frame)
            
        print_rich(f"  ✅ {char} 完成", "green")
    
    print_rich("✅ 角色生成完成！", "green")
    print_rich("📁 生成的幀圖已保存到 output/frames/", "cyan")

def create_demo_frame(character: str, frame_idx: int):
    """創建演示用的幀圖"""
    # 創建較大的演示圖片
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
    offset = int(15 * (frame_idx % 4 - 2))
    draw.rectangle([115 + offset, 150, 125 + offset, 200], fill=color)
    draw.rectangle([131 - offset, 150, 141 - offset, 200], fill=color)
    
    # 添加角色標識
    try:
        font = ImageFont.load_default()
        draw.text((10, 10), f"{character.title()} #{frame_idx}", fill=(255, 255, 255), font=font)
    except:
        pass
    
    # 保存圖片
    output_dir = Path("output/frames")
    output_dir.mkdir(exist_ok=True, parents=True)
    img.save(output_dir / f"{character}_frame_{frame_idx:02d}.png", "PNG")
    
    # 同時創建處理後的版本
    img.save(output_dir / f"{character}_processed_frame_{frame_idx:02d}.png", "PNG")

def demo_sprite_sheet_composition():
    """演示精靈表組合步驟"""
    print_rich("\n" + "="*60, "blue")
    print_rich("📑 演示步驟 3: 精靈表組合", "bold blue")
    print_rich("="*60, "blue")
    
    print_rich("🔧 正在組合精靈表...", "yellow")
    
    characters = ["warrior", "archer", "mage"]
    
    for char in characters:
        print_rich(f"📑 組合 {char} 精靈表...", "cyan")
        compose_character_sheet(char)
        time.sleep(1)
        print_rich(f"  ✅ {char} 精靈表完成", "green")
    
    # 創建主精靈表
    print_rich("🎯 創建主精靈表...", "yellow")
    create_master_sheet()
    
    print_rich("✅ 精靈表組合完成！", "green")
    show_demo_results()

def compose_character_sheet(character_type: str):
    """組合角色精靈表"""
    frames_dir = Path("output/frames")
    output_dir = Path("output/sprite_sheets")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # 收集幀圖
    pattern = f"{character_type}_processed_frame_*.png"
    frames = sorted(list(frames_dir.glob(pattern)))
    
    if not frames:
        pattern = f"{character_type}_frame_*.png"
        frames = sorted(list(frames_dir.glob(pattern)))
    
    if not frames:
        return
    
    # 創建水平精靈表
    sprite_size = (32, 48)  # 目標尺寸
    padding = 2
    
    sheet_width = (sprite_size[0] + padding) * len(frames) - padding
    sheet_height = sprite_size[1]
    
    sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    
    for i, frame_path in enumerate(frames):
        frame = Image.open(frame_path)
        # 縮放到目標尺寸
        frame_resized = frame.resize(sprite_size, Image.NEAREST)
        
        x_pos = i * (sprite_size[0] + padding)
        sprite_sheet.paste(frame_resized, (x_pos, 0))
    
    # 保存精靈表
    output_path = output_dir / f"{character_type}_sprite_sheet.png"
    sprite_sheet.save(output_path, "PNG")
    
    # 創建帶標註的版本
    annotated_sheet = sprite_sheet.copy()
    draw = ImageDraw.Draw(annotated_sheet)
    
    try:
        font = ImageFont.load_default()
        title = f"{character_type.title()} Walk Cycle ({len(frames)} frames)"
        draw.text((5, sheet_height - 15), title, fill=(255, 255, 255), font=font)
        
        # 添加幀編號
        for i in range(len(frames)):
            x_pos = i * (sprite_size[0] + padding) + 2
            draw.text((x_pos, 2), str(i), fill=(255, 255, 255), font=font)
    except:
        pass
    
    annotated_path = output_dir / f"{character_type}_sprite_sheet_annotated.png"
    annotated_sheet.save(annotated_path, "PNG")
    
    # 生成元數據
    metadata = {
        "character_type": character_type,
        "frame_count": len(frames),
        "frame_size": sprite_size,
        "layout": "horizontal",
        "padding": padding,
        "animation": {
            "fps": 8,
            "loop": True,
            "total_duration": len(frames) / 8
        },
        "frames": []
    }
    
    for i in range(len(frames)):
        frame_info = {
            "frame": i,
            "x": i * (sprite_size[0] + padding),
            "y": 0,
            "width": sprite_size[0],
            "height": sprite_size[1]
        }
        metadata["frames"].append(frame_info)
    
    metadata_path = output_dir / f"{character_type}_metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def create_master_sheet():
    """創建主精靈表"""
    output_dir = Path("output/sprite_sheets")
    characters = ["warrior", "archer", "mage"]
    
    all_sheets = []
    for char_type in characters:
        sheet_path = output_dir / f"{char_type}_sprite_sheet.png"
        if sheet_path.exists():
            sheet = Image.open(sheet_path)
            all_sheets.append((char_type, sheet))
    
    if not all_sheets:
        return
    
    # 計算主表尺寸
    max_width = max(sheet.width for _, sheet in all_sheets)
    total_height = sum(sheet.height + 2 for _, sheet in all_sheets) - 2
    
    # 創建主精靈表
    master_sheet = Image.new('RGBA', (max_width, total_height), (0, 0, 0, 0))
    
    # 放置每個角色的精靈表
    y_offset = 0
    for char_type, sheet in all_sheets:
        master_sheet.paste(sheet, (0, y_offset))
        y_offset += sheet.height + 2
    
    # 保存主精靈表
    master_path = output_dir / "master_sprite_sheet.png"
    master_sheet.save(master_path, "PNG")

def show_demo_results():
    """顯示演示結果"""
    print_rich("\n📊 演示結果總覽:", "bold cyan")
    
    output_dir = Path("output")
    
    # 統計文件
    if (output_dir / "frames").exists():
        frame_count = len(list((output_dir / "frames").glob("*.png")))
        print_rich(f"🎞️  生成幀圖: {frame_count} 張", "green")
    
    if (output_dir / "sprite_sheets").exists():
        sheet_count = len(list((output_dir / "sprite_sheets").glob("*_sprite_sheet.png")))
        metadata_count = len(list((output_dir / "sprite_sheets").glob("*_metadata.json")))
        print_rich(f"📑 精靈表: {sheet_count} 個", "green")
        print_rich(f"📋 元數據: {metadata_count} 個", "green")
    
    print_rich("\n📁 輸出文件位置:", "bold blue")
    print_rich("   • 單幀圖片: output/frames/", "cyan")
    print_rich("   • 精靈表: output/sprite_sheets/", "cyan")
    print_rich("   • 元數據: output/sprite_sheets/*_metadata.json", "cyan")

def demo_cleanup():
    """演示清理"""
    print_rich("\n🧹 演示完成，正在清理資源...", "yellow")
    time.sleep(1)
    print_rich("✅ 清理完成", "green")

def run_full_demo():
    """執行完整演示"""
    demo_banner()
    
    # 詢問用戶是否繼續
    print_rich("\n是否開始演示？ (y/n): ", "bold yellow")
    
    try:
        choice = input().lower()
        if choice not in ['y', 'yes', '是', '']:
            print_rich("演示已取消", "red")
            return
    except KeyboardInterrupt:
        print_rich("\n演示已中斷", "red")
        return
    
    try:
        # 執行演示步驟
        demo_data_preparation()
        demo_character_generation()
        demo_sprite_sheet_composition()
        
        # 顯示完成信息
        print_rich("\n" + "="*60, "green")
        print_rich("🎉 演示完成！", "bold green")
        print_rich("="*60, "green")
        
        print_rich("""
📚 下一步:
1. 安裝完整依賴: pip install -r requirements.txt
2. 運行真實生成: python main.py --full
3. 啟動Web界面: python web_ui.py
4. 查看詳細說明: python main.py --help-detail

💡 提示: 實際生成需要GPU支援和完整的AI模型
        """, "blue")
        
    except KeyboardInterrupt:
        print_rich("\n演示已中斷", "yellow")
    except Exception as e:
        print_rich(f"\n演示過程中發生錯誤: {e}", "red")
        import traceback
        traceback.print_exc()
    finally:
        demo_cleanup()

if __name__ == "__main__":
    run_full_demo() 