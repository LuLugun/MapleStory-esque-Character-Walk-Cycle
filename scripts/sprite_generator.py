#!/usr/bin/env python3
"""
楓之谷風格角色行走圖生成器
使用Stable Diffusion + ControlNet生成一致性的角色行走動畫
"""

import os
import yaml
import torch
from pathlib import Path
from PIL import Image
import numpy as np
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from typing import List, Optional, Dict, Any

# Diffusers 相關導入
from diffusers import (
    StableDiffusionControlNetPipeline,
    ControlNetModel,
    DPMSolverMultistepScheduler,
    StableDiffusionPipeline
)
from diffusers.utils import load_image
from transformers import pipeline
import cv2

console = Console()

class SpriteGenerator:
    def __init__(self, config_path: str = "configs/generation_config.yaml"):
        """初始化精靈生成器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.output_dir = Path("output/frames")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        console.print(f"🔧 使用設備: {self.device}", style="blue")
        
        # 初始化模型
        self.pipe = None
        self.controlnet = None
        self._load_models()
    
    def _load_models(self):
        """載入Stable Diffusion和ControlNet模型"""
        console.print("📦 載入AI模型中...", style="bold yellow")
        
        try:
            # 載入ControlNet
            self.controlnet = ControlNetModel.from_pretrained(
                self.config['controlnet']['model'],
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            # 載入主要SD管線
            self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
                self.config['model_settings']['base_model'],
                controlnet=self.controlnet,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None,  # 關閉安全檢查器以節省記憶體
            )
            
            # 設定調度器
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )
            
            # 啟用記憶體優化
            if self.device == "cuda":
                self.pipe.enable_model_cpu_offload()
                self.pipe.enable_xformers_memory_efficient_attention()
            
            self.pipe = self.pipe.to(self.device)
            
            console.print("✅ 模型載入完成", style="green")
            
        except Exception as e:
            console.print(f"❌ 模型載入失敗: {e}", style="red")
            # 使用基礎模型作為後備
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """載入後備基礎模型"""
        console.print("🔄 載入基礎模型...", style="yellow")
        
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.config['model_settings']['base_model'],
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
        )
        self.pipe = self.pipe.to(self.device)
    
    def create_pose_conditioning(self, frame_idx: int) -> np.ndarray:
        """創建姿勢控制圖像"""
        # 創建基本的行走姿勢骨架
        img_size = (self.config['image_settings']['width'], 
                   self.config['image_settings']['height'])
        
        # 創建空白圖像
        pose_img = np.zeros((*img_size[::-1], 3), dtype=np.uint8)
        
        # 計算行走週期中的位置
        cycle_progress = frame_idx / self.config['animation']['walk_cycle_frames']
        
        # 基本人體比例（相對於圖像大小）
        center_x = img_size[0] // 2
        head_y = int(img_size[1] * 0.15)
        torso_y = int(img_size[1] * 0.5)
        hip_y = int(img_size[1] * 0.65)
        foot_y = int(img_size[1] * 0.9)
        
        # 行走動作的腿部偏移
        leg_offset = int(30 * np.sin(2 * np.pi * cycle_progress))
        
        # 繪製簡單的骨架
        # 頭部
        cv2.circle(pose_img, (center_x, head_y), 15, (255, 255, 255), 2)
        
        # 軀幹
        cv2.line(pose_img, (center_x, head_y + 15), (center_x, hip_y), (255, 255, 255), 3)
        
        # 手臂
        arm_offset = int(20 * np.cos(2 * np.pi * cycle_progress))
        cv2.line(pose_img, (center_x, torso_y), (center_x - 40 + arm_offset, torso_y + 30), (255, 255, 255), 3)
        cv2.line(pose_img, (center_x, torso_y), (center_x + 40 - arm_offset, torso_y + 30), (255, 255, 255), 3)
        
        # 腿部
        cv2.line(pose_img, (center_x, hip_y), (center_x - 15 + leg_offset, foot_y), (255, 255, 255), 3)
        cv2.line(pose_img, (center_x, hip_y), (center_x + 15 - leg_offset, foot_y), (255, 255, 255), 3)
        
        return pose_img
    
    def generate_character_frame(self, 
                               character_type: str, 
                               frame_idx: int, 
                               pose_image: Optional[np.ndarray] = None) -> Image.Image:
        """生成單幀角色圖像"""
        
        # 構建提示詞
        base_prompt = self.config['prompts']['base_positive']
        char_prompt = self.config['prompts']['character_templates'][character_type]['positive']
        full_prompt = f"{base_prompt}, {char_prompt}, frame {frame_idx}"
        
        negative_prompt = self.config['prompts']['base_negative']
        
        # 生成參數
        gen_params = {
            "prompt": full_prompt,
            "negative_prompt": negative_prompt,
            "width": self.config['image_settings']['width'],
            "height": self.config['image_settings']['height'],
            "num_inference_steps": self.config['generation_params']['num_inference_steps'],
            "guidance_scale": self.config['generation_params']['guidance_scale'],
            "generator": torch.Generator(device=self.device).manual_seed(42 + frame_idx),
        }
        
        # 如果有ControlNet和姿勢圖像
        if self.controlnet is not None and pose_image is not None:
            pose_pil = Image.fromarray(pose_image)
            gen_params["image"] = pose_pil
            gen_params["controlnet_conditioning_scale"] = self.config['controlnet']['conditioning_scale']
        
        try:
            # 生成圖像
            with torch.no_grad():
                result = self.pipe(**gen_params)
                image = result.images[0]
            
            return image
            
        except Exception as e:
            console.print(f"❌ 生成幀 {frame_idx} 失敗: {e}", style="red")
            # 返回空白圖像作為後備
            return Image.new('RGBA', 
                           (self.config['image_settings']['width'], 
                            self.config['image_settings']['height']), 
                           (255, 255, 255, 0))
    
    def generate_walk_cycle(self, character_type: str) -> List[Image.Image]:
        """生成完整的行走週期"""
        console.print(f"🎨 生成 {character_type} 角色行走週期...", style="bold blue")
        
        frames = []
        num_frames = self.config['animation']['walk_cycle_frames']
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task(f"生成 {character_type} 幀數", total=num_frames)
            
            for frame_idx in range(num_frames):
                # 創建姿勢控制
                pose_image = self.create_pose_conditioning(frame_idx)
                
                # 生成幀
                frame = self.generate_character_frame(character_type, frame_idx, pose_image)
                frames.append(frame)
                
                # 保存單幀
                frame_path = self.output_dir / f"{character_type}_frame_{frame_idx:02d}.png"
                frame.save(frame_path, "PNG")
                
                progress.update(task, advance=1, 
                              description=f"已生成 {character_type} 第 {frame_idx+1}/{num_frames} 幀")
        
        console.print(f"✅ {character_type} 行走週期生成完成", style="green")
        return frames
    
    def process_frame_for_pixel_art(self, image: Image.Image) -> Image.Image:
        """後處理圖像以增強像素藝術效果"""
        # 轉換為numpy陣列
        img_array = np.array(image)
        
        # 簡單的色彩量化
        # 減少顏色數量以獲得更像素化的效果
        img_array = img_array // 32 * 32
        
        # 轉回PIL圖像
        processed_img = Image.fromarray(img_array.astype(np.uint8))
        
        # 縮小後放大以創建像素效果
        original_size = processed_img.size
        small_size = (original_size[0] // 8, original_size[1] // 8)
        
        processed_img = processed_img.resize(small_size, Image.NEAREST)
        processed_img = processed_img.resize(original_size, Image.NEAREST)
        
        return processed_img
    
    def generate_single_character(self, character_type: str):
        """生成指定角色的行走週期"""
        console.print(f"🎯 開始生成 {character_type} 角色行走圖", style="bold magenta")
        
        # 檢查角色是否存在於配置中
        if character_type not in self.config['prompts']['character_templates']:
            console.print(f"❌ 角色 '{character_type}' 不存在於配置中", style="red")
            console.print("📋 可用角色:", style="cyan")
            for char in self.config['prompts']['character_templates'].keys():
                console.print(f"   • {char}", style="cyan")
            return
        
        try:
            frames = self.generate_walk_cycle(character_type)
            
            # 後處理增強像素藝術效果
            processed_frames = []
            for frame in frames:
                processed_frame = self.process_frame_for_pixel_art(frame)
                processed_frames.append(processed_frame)
            
            # 保存處理後的幀
            for i, frame in enumerate(processed_frames):
                frame_path = self.output_dir / f"{character_type}_processed_frame_{i:02d}.png"
                frame.save(frame_path, "PNG")
            
            console.print(f"✅ {character_type} 完成", style="green")
            
        except Exception as e:
            console.print(f"❌ {character_type} 生成失敗: {e}", style="red")
        
        console.print(f"🎉 {character_type} 角色生成完成！", style="bold green")
    
    def generate_all_characters(self):
        """生成所有角色類型的行走週期"""
        console.print("🚀 開始生成所有角色行走圖", style="bold magenta")
        
        character_types = list(self.config['prompts']['character_templates'].keys())
        
        for char_type in character_types:
            try:
                frames = self.generate_walk_cycle(char_type)
                
                # 後處理增強像素藝術效果
                processed_frames = []
                for frame in frames:
                    processed_frame = self.process_frame_for_pixel_art(frame)
                    processed_frames.append(processed_frame)
                
                # 保存處理後的幀
                for i, frame in enumerate(processed_frames):
                    frame_path = self.output_dir / f"{char_type}_processed_frame_{i:02d}.png"
                    frame.save(frame_path, "PNG")
                
                console.print(f"✅ {char_type} 完成", style="green")
                
            except Exception as e:
                console.print(f"❌ {char_type} 生成失敗: {e}", style="red")
        
        console.print("🎉 所有角色生成完成！", style="bold green")
    
    def cleanup(self):
        """清理GPU記憶體"""
        if self.pipe is not None:
            del self.pipe
        if self.controlnet is not None:
            del self.controlnet
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        console.print("🧹 記憶體清理完成", style="blue")

def main():
    """主函數"""
    generator = SpriteGenerator()
    
    try:
        generator.generate_all_characters()
    finally:
        generator.cleanup()

if __name__ == "__main__":
    main() 