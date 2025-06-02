#!/usr/bin/env python3
"""
像素藝術品質優化器
專門用於改善AI生成的像素藝術品質
"""

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from pathlib import Path
from rich.console import Console
import cv2

console = Console()

class PixelArtOptimizer:
    def __init__(self):
        """初始化像素藝術優化器"""
        self.console = console
    
    def enhance_pixel_art_quality(self, image: Image.Image, 
                                target_size: tuple = (32, 48)) -> Image.Image:
        """增強像素藝術品質"""
        
        # 1. 色彩增強
        enhanced_image = self.enhance_colors(image)
        
        # 2. 邊緣銳化
        sharpened_image = self.sharpen_edges(enhanced_image)
        
        # 3. 色彩量化（減少色彩數量）
        quantized_image = self.quantize_colors(sharpened_image)
        
        # 4. 縮放到目標尺寸
        resized_image = self.resize_pixel_perfect(quantized_image, target_size)
        
        # 5. 背景處理
        final_image = self.process_background(resized_image)
        
        return final_image
    
    def enhance_colors(self, image: Image.Image) -> Image.Image:
        """色彩增強"""
        # 增加對比度
        contrast_enhancer = ImageEnhance.Contrast(image)
        enhanced = contrast_enhancer.enhance(1.3)
        
        # 增加飽和度
        color_enhancer = ImageEnhance.Color(enhanced)
        enhanced = color_enhancer.enhance(1.2)
        
        return enhanced
    
    def sharpen_edges(self, image: Image.Image) -> Image.Image:
        """邊緣銳化"""
        # 使用unsharp mask濾鏡
        sharpened = image.filter(ImageFilter.UnsharpMask(
            radius=1.0, percent=150, threshold=3
        ))
        return sharpened
    
    def quantize_colors(self, image: Image.Image, colors: int = 32) -> Image.Image:
        """色彩量化，減少色彩數量以獲得像素風格"""
        # 轉換為P模式並量化
        quantized = image.convert('P', palette=Image.ADAPTIVE, colors=colors)
        # 轉回RGBA以保持透明度
        return quantized.convert('RGBA')
    
    def resize_pixel_perfect(self, image: Image.Image, 
                           target_size: tuple) -> Image.Image:
        """像素完美縮放"""
        # 使用最近鄰插值進行縮放
        resized = image.resize(target_size, Image.NEAREST)
        return resized
    
    def process_background(self, image: Image.Image) -> Image.Image:
        """背景處理，移除不必要的背景並保持透明"""
        # 轉換為numpy陣列
        img_array = np.array(image)
        
        # 如果圖像沒有alpha通道，添加一個
        if img_array.shape[2] == 3:
            alpha = np.ones((img_array.shape[0], img_array.shape[1], 1), dtype=np.uint8) * 255
            img_array = np.concatenate([img_array, alpha], axis=2)
        
        # 檢測接近白色的像素並設為透明
        white_threshold = 240
        white_pixels = (
            (img_array[:, :, 0] > white_threshold) & 
            (img_array[:, :, 1] > white_threshold) & 
            (img_array[:, :, 2] > white_threshold)
        )
        img_array[white_pixels, 3] = 0  # 設為透明
        
        return Image.fromarray(img_array, 'RGBA')
    
    def create_reference_guided_prompt(self, character_name: str, 
                                     reference_path: str = None) -> str:
        """基於參考圖片創建更精確的提示詞"""
        
        base_prompt = f"high quality pixel art, {character_name}, maplestory style"
        
        # 如果有參考圖片，分析其特徵
        if reference_path and Path(reference_path).exists():
            try:
                ref_img = Image.open(reference_path)
                colors = self.analyze_color_palette(ref_img)
                clothing = self.analyze_clothing_style(ref_img)
                
                enhanced_prompt = f"{base_prompt}, {colors}, {clothing}, detailed pixel sprite"
                return enhanced_prompt
                
            except Exception as e:
                console.print(f"⚠️ 無法分析參考圖片: {e}", style="yellow")
        
        return base_prompt
    
    def analyze_color_palette(self, image: Image.Image) -> str:
        """分析圖片主要色彩"""
        # 簡化版本：檢測主要顏色
        img_array = np.array(image.resize((32, 32)))
        
        # 計算主要顏色
        colors = []
        if np.mean(img_array[:, :, 0]) > 150:  # 紅色系
            colors.append("red tones")
        if np.mean(img_array[:, :, 1]) > 100:  # 綠色系
            colors.append("brown tones")
        if np.mean(img_array[:, :, 2]) < 100:  # 深色
            colors.append("dark colors")
        
        return ", ".join(colors) if colors else "balanced colors"
    
    def analyze_clothing_style(self, image: Image.Image) -> str:
        """分析服裝風格"""
        # 簡化版本：基於圖片特徵推測風格
        return "casual outfit, dress style"
    
    def batch_optimize_frames(self, input_dir: str, output_dir: str, 
                            character_name: str):
        """批量優化幀圖片"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        # 找到所有角色的幀文件
        frame_files = list(input_path.glob(f"{character_name}_frame_*.png"))
        
        console.print(f"🎨 開始優化 {len(frame_files)} 張 {character_name} 幀圖片", style="blue")
        
        for frame_file in frame_files:
            try:
                # 載入原始圖片
                original = Image.open(frame_file)
                
                # 優化處理
                optimized = self.enhance_pixel_art_quality(original)
                
                # 保存優化後的圖片
                output_file = output_path / f"{character_name}_optimized_{frame_file.name}"
                optimized.save(output_file, "PNG")
                
                console.print(f"✅ 優化完成: {output_file.name}", style="green")
                
            except Exception as e:
                console.print(f"❌ 優化失敗 {frame_file.name}: {e}", style="red")
        
        console.print(f"🎉 {character_name} 幀優化完成！", style="bold green")

def main():
    """主函數：優化已生成的圖片"""
    optimizer = PixelArtOptimizer()
    
    # 優化Kelly角色的幀
    optimizer.batch_optimize_frames(
        input_dir="output/frames",
        output_dir="output/optimized_frames", 
        character_name="kelly"
    )

if __name__ == "__main__":
    main() 