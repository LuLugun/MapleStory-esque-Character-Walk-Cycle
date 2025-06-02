#!/usr/bin/env python3
"""
楓之谷風格角色行走圖製作工具 Web介面
基於Gradio的用戶友好界面
"""

import gradio as gr
import os
import yaml
from pathlib import Path
from PIL import Image
import subprocess
import json
from typing import List, Tuple, Optional

# 導入自定義模組
from scripts.data_preparation import DataPreparation
from scripts.sprite_generator import SpriteGenerator
from scripts.sheet_composer import SpriteSheetComposer

class WebUI:
    def __init__(self):
        """初始化Web界面"""
        self.config_path = "configs/generation_config.yaml"
        self.load_config()
        
    def load_config(self):
        """載入配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            self.config = self.get_default_config()
    
    def get_default_config(self) -> dict:
        """獲取預設配置"""
        return {
            "prompts": {
                "character_templates": {
                    "warrior": {"positive": "armored warrior, sword, shield"},
                    "archer": {"positive": "archer, bow, quiver"},
                    "mage": {"positive": "mage, wizard hat, staff"}
                }
            },
            "animation": {"walk_cycle_frames": 8},
            "generation_params": {"guidance_scale": 7.5}
        }
    
    def run_data_preparation(self, progress=gr.Progress()) -> str:
        """執行資料準備"""
        try:
            progress(0.1, desc="初始化資料準備...")
            prep = DataPreparation()
            
            progress(0.3, desc="創建範例素材...")
            prep.create_sample_sprites()
            
            progress(0.6, desc="放大精靈圖...")
            prep.upscale_sprites()
            
            progress(0.8, desc="提取單幀...")
            prep.extract_frames()
            
            progress(0.9, desc="創建姿勢參考...")
            prep.create_pose_references()
            
            progress(1.0, desc="資料準備完成！")
            return "✅ 資料準備完成！可以開始生成角色了。"
            
        except Exception as e:
            return f"❌ 資料準備失敗: {str(e)}"
    
    def generate_characters(self, 
                          character_types: List[str],
                          guidance_scale: float,
                          num_frames: int,
                          progress=gr.Progress()) -> Tuple[str, List]:
        """生成角色行走圖"""
        try:
            # 更新配置
            self.config['generation_params']['guidance_scale'] = guidance_scale
            self.config['animation']['walk_cycle_frames'] = num_frames
            
            progress(0.1, desc="初始化AI模型...")
            generator = SpriteGenerator()
            
            generated_images = []
            total_chars = len(character_types)
            
            for i, char_type in enumerate(character_types):
                if char_type in self.config['prompts']['character_templates']:
                    progress((i + 0.5) / total_chars, desc=f"生成 {char_type} 角色...")
                    
                    # 生成單個角色
                    frames = generator.generate_walk_cycle(char_type)
                    
                    # 收集生成的圖片
                    frame_paths = []
                    for j, frame in enumerate(frames):
                        frame_path = f"output/frames/{char_type}_frame_{j:02d}.png"
                        frame.save(frame_path, "PNG")
                        frame_paths.append(frame_path)
                    
                    generated_images.extend(frame_paths)
            
            generator.cleanup()
            progress(1.0, desc="角色生成完成！")
            
            return "✅ 角色生成完成！", generated_images
            
        except Exception as e:
            return f"❌ 角色生成失敗: {str(e)}", []
    
    def compose_sprite_sheets(self, progress=gr.Progress()) -> Tuple[str, List]:
        """組合精靈表"""
        try:
            progress(0.1, desc="初始化精靈表組合器...")
            composer = SpriteSheetComposer()
            
            progress(0.3, desc="組合各角色精靈表...")
            composer.compose_all_sheets()
            
            progress(1.0, desc="精靈表組合完成！")
            
            # 收集生成的精靈表
            sprite_sheets = []
            sheets_dir = Path("output/sprite_sheets")
            if sheets_dir.exists():
                for sheet_file in sheets_dir.glob("*_sprite_sheet.png"):
                    if "annotated" not in sheet_file.name:
                        sprite_sheets.append(str(sheet_file))
            
            return "✅ 精靈表組合完成！", sprite_sheets
            
        except Exception as e:
            return f"❌ 精靈表組合失敗: {str(e)}", []
    
    def run_full_pipeline(self,
                         character_types: List[str],
                         guidance_scale: float,
                         num_frames: int,
                         progress=gr.Progress()) -> Tuple[str, List]:
        """執行完整流程"""
        try:
            # 步驟1: 資料準備
            progress(0.0, desc="步驟 1/3: 資料準備...")
            prep_result = self.run_data_preparation()
            if "❌" in prep_result:
                return prep_result, []
            
            # 步驟2: 生成角色
            progress(0.33, desc="步驟 2/3: 生成角色...")
            gen_result, gen_images = self.generate_characters(
                character_types, guidance_scale, num_frames
            )
            if "❌" in gen_result:
                return gen_result, []
            
            # 步驟3: 組合精靈表
            progress(0.66, desc="步驟 3/3: 組合精靈表...")
            comp_result, sprite_sheets = self.compose_sprite_sheets()
            if "❌" in comp_result:
                return comp_result, []
            
            progress(1.0, desc="完整流程完成！")
            return "🎉 完整流程執行完成！所有角色行走圖已生成。", sprite_sheets
            
        except Exception as e:
            return f"❌ 流程執行失敗: {str(e)}", []
    
    def get_character_list(self) -> List[str]:
        """獲取可用角色類型列表"""
        return list(self.config['prompts']['character_templates'].keys())
    
    def create_interface(self):
        """創建Gradio界面"""
        
        with gr.Blocks(
            title="🍁 楓之谷風格角色行走圖製作工具",
            theme=gr.themes.Soft()
        ) as interface:
            
            gr.Markdown("""
            # 🍁 楓之谷風格角色行走圖製作工具
            
            使用生成式AI快速製作像素藝術風格的角色行走動畫！
            
            ## 使用說明
            1. 選擇要生成的角色類型
            2. 調整生成參數
            3. 點擊「執行完整流程」開始生成
            4. 等待處理完成，查看結果
            """)
            
            with gr.Tab("🎨 完整流程"):
                with gr.Row():
                    with gr.Column():
                        character_selector = gr.CheckboxGroup(
                            choices=self.get_character_list(),
                            value=self.get_character_list(),
                            label="選擇角色類型",
                            info="選擇要生成的角色類型"
                        )
                        
                        guidance_scale = gr.Slider(
                            minimum=1.0,
                            maximum=20.0,
                            value=7.5,
                            step=0.5,
                            label="引導強度",
                            info="控制AI生成的創造性 (較低=更創新，較高=更符合提示詞)"
                        )
                        
                        num_frames = gr.Slider(
                            minimum=4,
                            maximum=16,
                            value=8,
                            step=1,
                            label="動畫幀數",
                            info="行走動畫的幀數"
                        )
                        
                        run_button = gr.Button(
                            "🚀 執行完整流程",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column():
                        status_output = gr.Textbox(
                            label="執行狀態",
                            placeholder="點擊按鈕開始生成..."
                        )
                        
                        result_gallery = gr.Gallery(
                            label="生成結果",
                            show_label=True,
                            elem_id="gallery",
                            columns=3,
                            rows=2,
                            height="auto"
                        )
            
            with gr.Tab("🔧 分步執行"):
                with gr.Row():
                    with gr.Column():
                        prep_button = gr.Button("📋 資料準備")
                        gen_button = gr.Button("🎨 生成角色")
                        comp_button = gr.Button("📑 組合精靈表")
                    
                    with gr.Column():
                        step_status = gr.Textbox(label="步驟狀態")
                        step_gallery = gr.Gallery(label="步驟結果")
            
            with gr.Tab("⚙️ 設定"):
                gr.Markdown("### 進階設定")
                
                with gr.Row():
                    with gr.Column():
                        sprite_width = gr.Number(
                            value=32,
                            label="精靈寬度 (像素)",
                            minimum=16,
                            maximum=128
                        )
                        
                        sprite_height = gr.Number(
                            value=48,
                            label="精靈高度 (像素)",
                            minimum=16,
                            maximum=128
                        )
                    
                    with gr.Column():
                        layout_choice = gr.Radio(
                            choices=["horizontal", "grid"],
                            value="horizontal",
                            label="精靈表布局"
                        )
                        
                        add_padding = gr.Slider(
                            minimum=0,
                            maximum=10,
                            value=2,
                            step=1,
                            label="間距 (像素)"
                        )
            
            with gr.Tab("📚 說明"):
                gr.Markdown("""
                ### 📖 詳細說明
                
                #### 🎯 工具功能
                - **資料準備**: 創建和處理訓練用的範例精靈圖
                - **AI生成**: 使用Stable Diffusion生成角色行走動畫幀
                - **精靈表組合**: 將單幀組合成遊戲可用的精靈表
                
                #### 🎨 支援的角色類型
                - **戰士 (Warrior)**: 重甲戰士，配劍盾
                - **弓箭手 (Archer)**: 輕裝射手，配弓箭
                - **法師 (Mage)**: 魔法師，配法杖
                
                #### ⚙️ 參數說明
                - **引導強度**: 控制生成圖片與提示詞的匹配程度
                - **動畫幀數**: 行走循環的幀數，通常8幀效果最佳
                - **精靈尺寸**: 最終輸出的像素尺寸
                
                #### 📁 輸出文件
                - `output/frames/`: 單幀圖片
                - `output/sprite_sheets/`: 最終精靈表
                - `*_metadata.json`: 動畫元數據
                
                #### ⚠️ 注意事項
                - 本工具僅供學習和個人研究使用
                - 楓之谷美術版權屬於Nexon公司
                - 請勿用於商業用途
                """)
            
            # 綁定事件
            run_button.click(
                fn=self.run_full_pipeline,
                inputs=[character_selector, guidance_scale, num_frames],
                outputs=[status_output, result_gallery]
            )
            
            prep_button.click(
                fn=self.run_data_preparation,
                outputs=[step_status]
            )
            
            gen_button.click(
                fn=self.generate_characters,
                inputs=[character_selector, guidance_scale, num_frames],
                outputs=[step_status, step_gallery]
            )
            
            comp_button.click(
                fn=self.compose_sprite_sheets,
                outputs=[step_status, step_gallery]
            )
        
        return interface

def main():
    """主函數"""
    ui = WebUI()
    interface = ui.create_interface()
    
    # 啟動界面
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_tips=True,
        show_error=True
    )

if __name__ == "__main__":
    main() 