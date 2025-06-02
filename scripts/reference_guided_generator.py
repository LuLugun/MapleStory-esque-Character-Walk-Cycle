#!/usr/bin/env python3
"""
參考圖片指導生成器
使用img2img和Reference ControlNet確保生成的角色與參考圖片一致
"""

import os
import yaml
import torch
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from typing import List, Optional

# Diffusers 相關導入
from diffusers import (
    StableDiffusionImg2ImgPipeline,
    StableDiffusionControlNetPipeline,
    ControlNetModel,
    DPMSolverMultistepScheduler
)
from controlnet_aux import OpenposeDetector
import cv2

console = Console()

class ReferenceGuidedGenerator:
    def __init__(self, config_path: str = "configs/generation_config.yaml"):
        """初始化參考圖片指導生成器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if torch.backends.mps.is_available():
            self.device = "mps"
        
        self.output_dir = Path("output/reference_guided")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        console.print(f"🔧 使用設備: {self.device}", style="blue")
        
        # 初始化模型
        self.img2img_pipe = None
        self.reference_path = None
        self._load_models()
    
    def _load_models(self):
        """載入img2img模型"""
        console.print("📦 載入img2img模型中...", style="bold yellow")
        
        try:
            # 載入img2img管線
            self.img2img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
                self.config['model_settings']['base_model'],
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None,
            )
            
            # 設定調度器
            self.img2img_pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.img2img_pipe.scheduler.config
            )
            
            # 啟用記憶體優化
            if self.device == "cuda":
                self.img2img_pipe.enable_model_cpu_offload()
                self.img2img_pipe.enable_xformers_memory_efficient_attention()
            
            self.img2img_pipe = self.img2img_pipe.to(self.device)
            
            console.print("✅ img2img模型載入完成", style="green")
            
        except Exception as e:
            console.print(f"❌ 模型載入失敗: {e}", style="red")
    
    def load_reference_image(self, reference_path: str) -> Image.Image:
        """載入並預處理參考圖片"""
        self.reference_path = reference_path
        
        if not Path(reference_path).exists():
            raise FileNotFoundError(f"參考圖片不存在: {reference_path}")
        
        # 載入參考圖片
        ref_image = Image.open(reference_path)
        
        # 確保是RGBA格式
        if ref_image.mode != 'RGBA':
            ref_image = ref_image.convert('RGBA')
        
        console.print(f"✅ 載入參考圖片: {reference_path}", style="green")
        console.print(f"📐 原始尺寸: {ref_image.size}", style="cyan")
        
        return ref_image
    
    def prepare_reference_for_generation(self, ref_image: Image.Image, 
                                       target_size: tuple = (256, 384)) -> Image.Image:
        """準備參考圖片用於生成"""
        
        # 放大到目標尺寸（使用最近鄰插值保持像素風格）
        upscaled = ref_image.resize(target_size, Image.NEAREST)
        
        # 輕微模糊以避免過度擬合
        blurred = upscaled.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # 降低透明度以減少直接複製
        if blurred.mode == 'RGBA':
            # 將alpha通道稍微降低
            alpha = np.array(blurred)[:, :, 3]
            alpha = (alpha * 0.8).astype(np.uint8)
            blurred_array = np.array(blurred)
            blurred_array[:, :, 3] = alpha
            blurred = Image.fromarray(blurred_array, 'RGBA')
        
        return blurred
    
    def create_walking_variations(self, base_ref: Image.Image, frame_count: int = 8) -> List[Image.Image]:
        """基於參考圖片創建行走動畫變化"""
        variations = []
        
        for i in range(frame_count):
            # 計算行走週期進度
            cycle_progress = i / frame_count
            
            # 創建輕微的姿勢變化
            modified_ref = self.apply_walking_transform(base_ref, cycle_progress)
            variations.append(modified_ref)
        
        return variations
    
    def apply_walking_transform(self, image: Image.Image, progress: float) -> Image.Image:
        """應用行走動畫變換"""
        # 轉換為numpy陣列
        img_array = np.array(image)
        h, w = img_array.shape[:2]
        
        # 計算輕微的左右搖擺
        sway = int(2 * np.sin(2 * np.pi * progress))
        
        # 創建變換矩陣（輕微搖擺）
        if sway != 0:
            # 輕微水平移動
            shifted = np.roll(img_array, sway, axis=1)
            return Image.fromarray(shifted, image.mode)
        
        return image
    
    def generate_frame_from_reference(self, 
                                    reference_img: Image.Image,
                                    frame_idx: int,
                                    character_name: str) -> Image.Image:
        """基於參考圖片生成單幀"""
        
        # 構建提示詞
        char_config = self.config['prompts']['character_templates'].get(character_name, {})
        base_prompt = self.config['prompts']['base_positive']
        char_prompt = char_config.get('positive', '')
        
        # 創建更強調一致性的提示詞
        full_prompt = f"{base_prompt}, {char_prompt}, walking animation frame {frame_idx}, consistent character design, same outfit, same hairstyle"
        negative_prompt = f"{self.config['prompts']['base_negative']}, different character, changed outfit, different hairstyle"
        
        # img2img生成參數
        gen_params = {
            "prompt": full_prompt,
            "negative_prompt": negative_prompt,
            "image": reference_img,
            "strength": 0.3,  # 較低的strength保持參考圖片特徵
            "num_inference_steps": self.config['generation_params']['num_inference_steps'],
            "guidance_scale": self.config['generation_params']['guidance_scale'],
            "generator": torch.Generator(device=self.device).manual_seed(42 + frame_idx),
        }
        
        try:
            # 生成圖像
            with torch.no_grad():
                result = self.img2img_pipe(**gen_params)
                generated_image = result.images[0]
            
            return generated_image
            
        except Exception as e:
            console.print(f"❌ 生成幀 {frame_idx} 失敗: {e}", style="red")
            # 返回參考圖片作為後備
            return reference_img
    
    def generate_kelly_walking_cycle(self, reference_path: str) -> List[Image.Image]:
        """專門為Kelly生成行走週期"""
        console.print("🎯 開始基於參考圖片生成Kelly行走週期", style="bold magenta")
        
        # 載入參考圖片
        ref_image = self.load_reference_image(reference_path)
        
        # 準備生成用的參考圖片
        target_size = (self.config['image_settings']['width'], 
                      self.config['image_settings']['height'])
        prepared_ref = self.prepare_reference_for_generation(ref_image, target_size)
        
        # 創建行走變化
        walking_refs = self.create_walking_variations(prepared_ref, 8)
        
        frames = []
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("生成Kelly行走幀", total=len(walking_refs))
            
            for i, ref_variant in enumerate(walking_refs):
                # 生成基於參考的幀
                frame = self.generate_frame_from_reference(ref_variant, i, "kelly")
                frames.append(frame)
                
                # 保存幀
                frame_path = self.output_dir / f"kelly_ref_frame_{i:02d}.png"
                frame.save(frame_path, "PNG")
                
                progress.update(task, advance=1,
                              description=f"Kelly參考生成 第 {i+1}/{len(walking_refs)} 幀")
        
        console.print("✅ Kelly參考指導生成完成", style="green")
        return frames
    
    def create_simple_reference_copy(self, reference_path: str, output_count: int = 8):
        """創建簡單的參考圖片複製版本（作為對比）"""
        console.print("📋 創建參考圖片變化版本", style="blue")
        
        ref_image = self.load_reference_image(reference_path)
        
        for i in range(output_count):
            # 創建輕微變化
            if i == 0:
                # 原始版本
                output_img = ref_image
            elif i < 4:
                # 輕微增強版本
                enhancer = ImageEnhance.Contrast(ref_image)
                output_img = enhancer.enhance(1.1 + i * 0.05)
            else:
                # 輕微色調變化
                enhancer = ImageEnhance.Color(ref_image)
                output_img = enhancer.enhance(1.1 + (i-4) * 0.03)
            
            # 放大到標準尺寸
            target_size = (self.config['image_settings']['width'], 
                          self.config['image_settings']['height'])
            upscaled = output_img.resize(target_size, Image.NEAREST)
            
            # 保存
            output_path = self.output_dir / f"kelly_simple_copy_{i:02d}.png"
            upscaled.save(output_path, "PNG")
            
            console.print(f"✅ 保存變化版本: {output_path.name}", style="green")
    
    def cleanup(self):
        """清理記憶體"""
        if self.img2img_pipe is not None:
            del self.img2img_pipe
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        console.print("🧹 記憶體清理完成", style="blue")

def main():
    """主函數"""
    generator = ReferenceGuidedGenerator()
    
    try:
        # Kelly參考圖片路徑
        kelly_ref_path = "data/raw_sprites/Kelly.png"
        
        if Path(kelly_ref_path).exists():
            # 方法1: 創建簡單複製版本
            generator.create_simple_reference_copy(kelly_ref_path)
            
            # 方法2: AI指導生成
            generator.generate_kelly_walking_cycle(kelly_ref_path)
            
            console.print("\n🎉 Kelly參考指導生成完成！", style="bold green")
            console.print("📁 請查看 output/reference_guided/ 目錄", style="cyan")
        else:
            console.print(f"❌ 找不到Kelly參考圖片: {kelly_ref_path}", style="red")
    
    finally:
        generator.cleanup()

if __name__ == "__main__":
    main() 