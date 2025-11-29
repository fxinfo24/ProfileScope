#!/bin/bash
# ProfileScope Desktop Application Launcher - Safe Mode
echo "🖥️  Starting ProfileScope Desktop Application (Safe Mode)..."

# Set environment variables to avoid conflicts
export QT_API=tkinter
export MPLBACKEND=TkAgg
export PYTORCH_ENABLE_MPS_FALLBACK=1

# Disable problematic features that might cause version checks
export DISABLE_ADVANCED_FEATURES=1

echo "🔧 Environment configured for maximum compatibility"
python3 bin/run.py --desktop