#!/usr/bin/env python3
"""
精靈表組合器
將生成的單幀圖片組合成最終的Sprite Sheet
"""

import os
import yaml
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from typing import List, Tuple, Optional
import json

console = Console()

class SpriteSheetComposer:
    def __init__(self, config_path: str = "configs/generation_config.yaml"):
        """初始化精靈表組合器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.frames_dir = Path("output/frames")
        self.output_dir = Path("output/sprite_sheets")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # 精靈表設定
        self.sprite_size = tuple(self.config['image_settings']['original_sprite_size'])
        self.padding = self.config['postprocess']['add_padding']
        self.layout = self.config['postprocess']['sprite_sheet_layout']
    
    def collect_character_frames(self, character_type: str) -> List[Path]:
        """收集指定角色的所有幀"""
        pattern = f"{character_type}_processed_frame_*.png"
        frames = sorted(list(self.frames_dir.glob(pattern)))
        
        if not frames:
            # 如果沒有處理過的幀，使用原始幀
            pattern = f"{character_type}_frame_*.png"
            frames = sorted(list(self.frames_dir.glob(pattern)))
        
        console.print(f"📋 收集到 {character_type} 的 {len(frames)} 幀", style="blue")
        return frames
    
    def resize_frame_to_target(self, image: Image.Image) -> Image.Image:
        """將幀縮放到目標像素尺寸"""
        target_size = (
            self.sprite_size[0] * self.config['image_settings']['upscale_factor'],
            self.sprite_size[1] * self.config['image_settings']['upscale_factor']
        )
        
        # 使用最近鄰插值保持像素風格
        resized = image.resize(target_size, Image.NEAREST)
        
        # 最終縮放到目標精靈尺寸
        final_resized = resized.resize(self.sprite_size, Image.NEAREST)
        
        return final_resized
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """移除背景（簡單版本）"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 將白色背景轉為透明
        data = np.array(image)
        
        # 找到接近白色的像素
        white_pixels = (data[:, :, 0] > 240) & (data[:, :, 1] > 240) & (data[:, :, 2] > 240)
        data[white_pixels] = [0, 0, 0, 0]  # 設為透明
        
        return Image.fromarray(data, 'RGBA')
    
    def create_horizontal_sprite_sheet(self, frames: List[Image.Image], character_type: str) -> Image.Image:
        """創建水平排列的精靈表"""
        frame_count = len(frames)
        
        # 計算精靈表尺寸
        sheet_width = (self.sprite_size[0] + self.padding) * frame_count - self.padding
        sheet_height = self.sprite_size[1]
        
        # 創建透明背景的精靈表
        sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
        
        console.print(f"📐 創建 {character_type} 精靈表尺寸: {sheet_width}x{sheet_height}", style="blue")
        
        # 逐幀放置
        for i, frame in enumerate(frames):
            x_pos = i * (self.sprite_size[0] + self.padding)
            sprite_sheet.paste(frame, (x_pos, 0), frame if frame.mode == 'RGBA' else None)
        
        return sprite_sheet
    
    def create_grid_sprite_sheet(self, frames: List[Image.Image], character_type: str, 
                               cols: int = 4) -> Image.Image:
        """創建網格排列的精靈表"""
        frame_count = len(frames)
        rows = (frame_count + cols - 1) // cols  # 向上取整
        
        # 計算精靈表尺寸
        sheet_width = (self.sprite_size[0] + self.padding) * cols - self.padding
        sheet_height = (self.sprite_size[1] + self.padding) * rows - self.padding
        
        # 創建透明背景的精靈表
        sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
        
        console.print(f"📐 創建 {character_type} 網格精靈表: {cols}x{rows}, {sheet_width}x{sheet_height}", style="blue")
        
        # 逐幀放置
        for i, frame in enumerate(frames):
            row = i // cols
            col = i % cols
            
            x_pos = col * (self.sprite_size[0] + self.padding)
            y_pos = row * (self.sprite_size[1] + self.padding)
            
            sprite_sheet.paste(frame, (x_pos, y_pos), frame if frame.mode == 'RGBA' else None)
        
        return sprite_sheet
    
    def add_metadata_overlay(self, sprite_sheet: Image.Image, character_type: str, 
                           frame_count: int) -> Image.Image:
        """在精靈表上添加元數據覆蓋"""
        # 創建一個副本來添加標註
        annotated_sheet = sprite_sheet.copy()
        draw = ImageDraw.Draw(annotated_sheet)
        
        # 嘗試載入字體，失敗則使用默認字體
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        # 添加標題
        title = f"{character_type.title()} Walk Cycle ({frame_count} frames)"
        draw.text((5, sprite_sheet.height - 20), title, fill=(255, 255, 255, 255), font=font)
        
        # 添加幀編號
        if self.layout == "horizontal":
            for i in range(frame_count):
                x_pos = i * (self.sprite_size[0] + self.padding) + 2
                draw.text((x_pos, 2), str(i), fill=(255, 255, 255, 255), font=font)
        
        return annotated_sheet
    
    def generate_sprite_metadata(self, character_type: str, frame_count: int) -> dict:
        """生成精靈表元數據"""
        metadata = {
            "character_type": character_type,
            "frame_count": frame_count,
            "frame_size": self.sprite_size,
            "layout": self.layout,
            "padding": self.padding,
            "animation": {
                "fps": self.config['animation']['fps'],
                "loop": True,
                "total_duration": frame_count / self.config['animation']['fps']
            },
            "frames": []
        }
        
        # 添加每幀的位置信息
        for i in range(frame_count):
            if self.layout == "horizontal":
                x = i * (self.sprite_size[0] + self.padding)
                y = 0
            else:  # grid layout
                cols = 4
                x = (i % cols) * (self.sprite_size[0] + self.padding)
                y = (i // cols) * (self.sprite_size[1] + self.padding)
            
            frame_info = {
                "frame": i,
                "x": x,
                "y": y,
                "width": self.sprite_size[0],
                "height": self.sprite_size[1]
            }
            metadata["frames"].append(frame_info)
        
        return metadata
    
    def compose_character_sheet(self, character_type: str):
        """組合指定角色的精靈表"""
        console.print(f"📑 組合 {character_type} 精靈表...", style="bold blue")
        
        # 收集幀文件
        frame_paths = self.collect_character_frames(character_type)
        if not frame_paths:
            console.print(f"❌ 未找到 {character_type} 的幀文件", style="red")
            return
        
        # 載入和處理幀
        frames = []
        for frame_path in frame_paths:
            image = Image.open(frame_path)
            
            # 背景移除
            if self.config['postprocess']['background_removal']:
                image = self.remove_background(image)
            
            # 縮放到目標尺寸
            image = self.resize_frame_to_target(image)
            frames.append(image)
        
        # 創建精靈表
        if self.layout == "horizontal":
            sprite_sheet = self.create_horizontal_sprite_sheet(frames, character_type)
        else:
            sprite_sheet = self.create_grid_sprite_sheet(frames, character_type)
        
        # 保存原始精靈表
        output_path = self.output_dir / f"{character_type}_sprite_sheet.png"
        sprite_sheet.save(output_path, "PNG")
        
        # 創建帶標註的版本
        annotated_sheet = self.add_metadata_overlay(sprite_sheet, character_type, len(frames))
        annotated_path = self.output_dir / f"{character_type}_sprite_sheet_annotated.png"
        annotated_sheet.save(annotated_path, "PNG")
        
        # 生成元數據JSON
        metadata = self.generate_sprite_metadata(character_type, len(frames))
        metadata_path = self.output_dir / f"{character_type}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        console.print(f"✅ {character_type} 精靈表組合完成", style="green")
        console.print(f"📄 輸出文件:", style="blue")
        console.print(f"   - 精靈表: {output_path}", style="cyan")
        console.print(f"   - 標註版: {annotated_path}", style="cyan")
        console.print(f"   - 元數據: {metadata_path}", style="cyan")
    
    def create_master_sheet(self):
        """創建包含所有角色的主精靈表"""
        console.print("🎯 創建主精靈表...", style="bold magenta")
        
        character_types = list(self.config['prompts']['character_templates'].keys())
        all_sheets = []
        
        # 載入所有角色的精靈表
        for char_type in character_types:
            sheet_path = self.output_dir / f"{char_type}_sprite_sheet.png"
            if sheet_path.exists():
                sheet = Image.open(sheet_path)
                all_sheets.append((char_type, sheet))
        
        if not all_sheets:
            console.print("❌ 沒有找到任何精靈表", style="red")
            return
        
        # 計算主表尺寸
        max_width = max(sheet.width for _, sheet in all_sheets)
        total_height = sum(sheet.height + self.padding for _, sheet in all_sheets) - self.padding
        
        # 創建主精靈表
        master_sheet = Image.new('RGBA', (max_width, total_height), (0, 0, 0, 0))
        
        # 放置每個角色的精靈表
        y_offset = 0
        for char_type, sheet in all_sheets:
            master_sheet.paste(sheet, (0, y_offset), sheet)
            y_offset += sheet.height + self.padding
        
        # 保存主精靈表
        master_path = self.output_dir / "master_sprite_sheet.png"
        master_sheet.save(master_path, "PNG")
        
        console.print(f"✅ 主精靈表創建完成: {master_path}", style="green")
    
    def compose_all_sheets(self):
        """組合所有角色的精靈表"""
        console.print("🚀 開始組合所有精靈表", style="bold magenta")
        
        character_types = list(self.config['prompts']['character_templates'].keys())
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("組合精靈表", total=len(character_types) + 1)
            
            for char_type in character_types:
                self.compose_character_sheet(char_type)
                progress.update(task, advance=1, description=f"已完成 {char_type}")
            
            # 創建主精靈表
            self.create_master_sheet()
            progress.update(task, advance=1, description="主精靈表完成")
        
        console.print("🎉 所有精靈表組合完成！", style="bold green")
        
        # 輸出總結
        self.print_summary()
    
    def print_summary(self):
        """輸出處理總結"""
        console.print("\n📊 處理總結:", style="bold yellow")
        
        # 統計輸出文件
        sheet_files = list(self.output_dir.glob("*_sprite_sheet.png"))
        metadata_files = list(self.output_dir.glob("*_metadata.json"))
        
        console.print(f"✨ 生成的精靈表: {len(sheet_files)} 個", style="green")
        console.print(f"📋 元數據文件: {len(metadata_files)} 個", style="green")
        
        # 列出所有輸出文件
        console.print("\n📁 輸出文件清單:", style="bold cyan")
        for file in sorted(self.output_dir.glob("*")):
            console.print(f"   {file.name}", style="cyan")

def main():
    """主函數"""
    composer = SpriteSheetComposer()
    composer.compose_all_sheets()

if __name__ == "__main__":
    main() 