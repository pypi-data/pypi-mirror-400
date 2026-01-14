#!/bin/bash
#
# Install ASR Enhancer with Local LLM
# ===================================
#
# This script installs all dependencies including local LLM models (no API calls).
#

set -e

echo "🚀 Installing ASR Enhancer with Local LLM..."
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d'.' -f1,2)
echo "✓ Python version: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" != "3.11" ]] && [[ "$PYTHON_VERSION" != "3.12" ]]; then
    echo "⚠️  Warning: Python 3.11 or 3.12 recommended for faster-whisper"
fi

echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🤖 Downloading local LLM model (mt5-small, ~300MB)..."
python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("google/mt5-small")

print("Loading model...")
model = AutoModelForSeq2SeqLM.from_pretrained(
    "google/mt5-small",
    torch_dtype=torch.float32,
    low_cpu_mem_usage=True,
)

print("✅ Model downloaded and cached!")
print(f"   Model size: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M parameters")
EOF

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Start the server:"
echo "      python -m asr_enhancer.api.main --cpu --keys \"sk-asr-2024-prod-key-002-abc123\""
echo ""
echo "   2. Test with a request:"
echo "      curl -X POST http://localhost:8000/api/v2/enhance \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"audio_path\": \"/path/to/audio.mp3\", \"primary_text\": \"हेलो सर\", \"audio_duration\": 5.0}'"
echo ""
echo "🎉 Local LLM (mt5-small) will be pre-loaded on startup!"
echo "   No API keys or internet required for inference."
echo ""
