#!/usr/bin/env python3
"""
楓之谷風格角色行走圖資料準備腳本
用於下載、處理和準備訓練/參考資料
"""

import os
import yaml
import requests
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import cv2
from typing import List, Tuple

console = Console()

class DataPreparation:
    def __init__(self, config_path: str = "configs/generation_config.yaml"):
        """初始化資料準備器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.raw_dir = Path("data/raw_sprites")
        self.processed_dir = Path("data/processed")
        self.reference_dir = Path("data/references")
        
        # 確保目錄存在
        for dir_path in [self.raw_dir, self.processed_dir, self.reference_dir]:
            dir_path.mkdir(exist_ok=True, parents=True)
    
    def download_sample_sprites(self):
        """下載範例楓之谷素材"""
        console.print("📥 開始下載範例楓之谷素材...", style="bold blue")
        
        # 範例素材URL（這裡使用假設的URL，實際應從合法來源獲取）
        sample_urls = [
            "https://example.com/maplestory/warrior_walk.png",
            "https://example.com/maplestory/archer_walk.png", 
            "https://example.com/maplestory/mage_walk.png"
        ]
        
        # 本地範例素材創建（用於演示）
        self.create_sample_sprites()
        console.print("✅ 範例素材準備完成", style="green")
    
    def create_sample_sprites(self):
        """創建範例素材用於演示"""
        sprite_size = tuple(self.config['image_settings']['original_sprite_size'])
        
        # 創建基本角色框架
        for char_type in ['warrior', 'archer', 'mage']:
            sprite_sheet = self.create_sample_walk_cycle(char_type, sprite_size)
            sprite_sheet.save(self.raw_dir / f"{char_type}_walk_cycle.png")
        
        console.print("📝 已創建範例角色行走圖", style="yellow")
    
    def create_sample_walk_cycle(self, char_type: str, sprite_size: Tuple[int, int]) -> Image.Image:
        """創建範例行走循環圖"""
        frames = 8
        sheet_width = sprite_size[0] * frames
        sheet_height = sprite_size[1]
        
        # 創建空白精靈表
        sprite_sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
        
        # 基本顏色配置
        colors = {
            'warrior': {'body': (255, 220, 177), 'armor': (100, 149, 237)},
            'archer': {'body': (255, 220, 177), 'armor': (34, 139, 34)},
            'mage': {'body': (255, 220, 177), 'armor': (138, 43, 226)}
        }
        
        for frame in range(frames):
            x_offset = frame * sprite_size[0]
            # 這裡可以添加更詳細的像素繪製邏輯
            # 為簡化，創建基本矩形作為範例
            char_img = Image.new('RGBA', sprite_size, colors[char_type]['body'])
            sprite_sheet.paste(char_img, (x_offset, 0))
        
        return sprite_sheet
    
    def upscale_sprites(self):
        """將原始32x48像素放大到256x384用於SD處理"""
        console.print("🔍 開始放大精靈圖至SD合適尺寸...", style="bold blue")
        
        upscale_factor = self.config['image_settings']['upscale_factor']
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("處理精靈圖...", total=None)
            
            for sprite_file in self.raw_dir.glob("*.png"):
                self.process_single_sprite(sprite_file, upscale_factor)
                progress.update(task, description=f"已處理 {sprite_file.name}")
        
        console.print("✅ 精靈圖放大完成", style="green")
    
    def process_single_sprite(self, sprite_path: Path, upscale_factor: int):
        """處理單個精靈圖"""
        img = Image.open(sprite_path)
        
        # 使用最近鄰插值放大以保持像素風格
        upscaled_img = img.resize(
            (img.width * upscale_factor, img.height * upscale_factor),
            Image.NEAREST
        )
        
        # 保存到processed目錄
        output_path = self.processed_dir / f"upscaled_{sprite_path.name}"
        upscaled_img.save(output_path, "PNG")
    
    def extract_frames(self):
        """從精靈表中提取單幀"""
        console.print("🎞️  提取單幀圖片...", style="bold blue")
        
        frames_dir = self.processed_dir / "frames"
        frames_dir.mkdir(exist_ok=True)
        
        sprite_size = self.config['image_settings']['original_sprite_size']
        upscale_factor = self.config['image_settings']['upscale_factor']
        frame_size = (sprite_size[0] * upscale_factor, sprite_size[1] * upscale_factor)
        
        for sprite_file in self.processed_dir.glob("upscaled_*.png"):
            self.extract_frames_from_sheet(sprite_file, frame_size, frames_dir)
        
        console.print("✅ 單幀提取完成", style="green")
    
    def extract_frames_from_sheet(self, sheet_path: Path, frame_size: Tuple[int, int], output_dir: Path):
        """從精靈表提取單幀"""
        sheet = Image.open(sheet_path)
        frame_width, frame_height = frame_size
        frames_count = sheet.width // frame_width
        
        char_name = sheet_path.stem.replace("upscaled_", "").replace("_walk_cycle", "")
        
        for i in range(frames_count):
            left = i * frame_width
            frame = sheet.crop((left, 0, left + frame_width, frame_height))
            
            frame_path = output_dir / f"{char_name}_frame_{i:02d}.png"
            frame.save(frame_path, "PNG")
    
    def create_pose_references(self):
        """創建姿勢參考文件（用於ControlNet）"""
        console.print("🤖 創建ControlNet姿勢參考...", style="bold blue")
        
        pose_dir = self.reference_dir / "poses"
        pose_dir.mkdir(exist_ok=True)
        
        # 創建基本行走姿勢的OpenPose格式JSON
        walk_poses = self.generate_walk_poses()
        
        for i, pose in enumerate(walk_poses):
            pose_file = pose_dir / f"walk_pose_{i:02d}.json"
            with open(pose_file, 'w') as f:
                yaml.dump(pose, f)
        
        console.print("✅ 姿勢參考創建完成", style="green")
    
    def generate_walk_poses(self) -> List[dict]:
        """生成行走姿勢資料"""
        # 簡化的行走姿勢關鍵點
        base_pose = {
            "keypoints": [
                {"name": "head", "x": 0.5, "y": 0.15},
                {"name": "neck", "x": 0.5, "y": 0.25},
                {"name": "torso", "x": 0.5, "y": 0.5},
                {"name": "left_shoulder", "x": 0.3, "y": 0.3},
                {"name": "right_shoulder", "x": 0.7, "y": 0.3},
                {"name": "left_hip", "x": 0.4, "y": 0.65},
                {"name": "right_hip", "x": 0.6, "y": 0.65},
            ]
        }
        
        poses = []
        frames = self.config['animation']['walk_cycle_frames']
        
        for i in range(frames):
            pose = base_pose.copy()
            # 簡單的行走動畫偏移
            walk_offset = np.sin(2 * np.pi * i / frames) * 0.1
            pose["frame"] = i
            pose["walk_offset"] = walk_offset
            poses.append(pose)
        
        return poses
    
    def validate_data(self):
        """驗證準備的資料"""
        console.print("🔍 驗證資料完整性...", style="bold blue")
        
        required_dirs = [self.raw_dir, self.processed_dir, self.reference_dir]
        for dir_path in required_dirs:
            if not dir_path.exists():
                console.print(f"❌ 缺少目錄: {dir_path}", style="red")
                return False
        
        # 檢查是否有處理後的圖片
        if not list(self.processed_dir.glob("upscaled_*.png")):
            console.print("❌ 缺少處理後的精靈圖", style="red")
            return False
        
        console.print("✅ 資料驗證通過", style="green")
        return True
    
    def run_all(self):
        """執行完整的資料準備流程"""
        console.print("🚀 開始楓之谷風格角色行走圖資料準備", style="bold magenta")
        
        try:
            self.download_sample_sprites()
            self.upscale_sprites()
            self.extract_frames()
            self.create_pose_references()
            
            if self.validate_data():
                console.print("🎉 資料準備完成！", style="bold green")
            else:
                console.print("⚠️  資料準備有問題，請檢查", style="yellow")
                
        except Exception as e:
            console.print(f"❌ 資料準備失敗: {e}", style="red")

def main():
    """主函數"""
    prep = DataPreparation()
    prep.run_all()

if __name__ == "__main__":
    main() 