#!/bin/bash

# 楓之谷風格角色行走圖製作工具啟動腳本

echo "🍁 楓之谷風格角色行走圖製作工具 🍁"
echo "======================================"

# 檢查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📋 檢測到Python版本: $python_version"

# 檢查是否為虛擬環境
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 正在使用虛擬環境: $VIRTUAL_ENV"
else
    echo "⚠️  建議使用虛擬環境"
    echo "   創建虛擬環境: python3 -m venv venv"
    echo "   啟動虛擬環境: source venv/bin/activate"
fi

# 檢查依賴是否安裝
echo "🔍 檢查依賴套件..."
if ! python3 -c "import torch, diffusers, PIL" 2>/dev/null; then
    echo "❌ 缺少必要依賴，正在安裝..."
    pip install -r requirements.txt
else
    echo "✅ 依賴套件已安裝"
fi

# 檢查GPU支援
if python3 -c "import torch; print('CUDA可用:', torch.cuda.is_available())" 2>/dev/null; then
    gpu_status=$(python3 -c "import torch; print('✅ GPU' if torch.cuda.is_available() else '⚠️  CPU')")
    echo "🔧 計算設備: $gpu_status"
else
    echo "🔧 計算設備: ⚠️  CPU (未檢測到GPU)"
fi

echo ""
echo "🚀 啟動選項:"
echo "1. Web界面 (推薦新手)"
echo "2. 命令行界面"
echo "3. 完整流程一鍵執行"
echo "4. 僅檢視結果"

read -p "請選擇 (1-4): " choice

case $choice in
    1)
        echo "🌐 啟動Web界面..."
        python3 web_ui.py
        ;;
    2)
        echo "💻 啟動命令行界面..."
        python3 main.py --help-detail
        ;;
    3)
        echo "⚡ 執行完整流程..."
        python3 main.py --full
        ;;
    4)
        echo "📊 顯示結果..."
        python3 main.py --results
        ;;
    *)
        echo "❌ 無效選擇，啟動Web界面..."
        python3 web_ui.py
        ;;
esac 