# vLLM Installation and ModuleNotFoundError Debugging Guide

## Overview

This guide provides a systematic approach to diagnosing and resolving `ModuleNotFoundError: No module named 'vllm'` when attempting to run the vLLM OpenAI API server.

## Error Context

**Common Error Message:**

```
ModuleNotFoundError: No module named 'vllm'
Process failed with exit code 1 when executing: python -m vllm.entrypoints.openai.api_server
```

## Systematic Debugging Workflow

### Step 1: Environment Diagnostics

#### 1.1 Check Python Environment Status

```bash
# Check Python version
python --version
python3 --version

# Expected Output: Python 3.8+ (vLLM requires Python 3.8 or higher)
```

```bash
# Check which Python executable is being used
which python
which python3

# Check if you're in a virtual environment
echo $VIRTUAL_ENV

# If empty, you're not in a virtual environment
```

#### 1.2 Virtual Environment Verification

```bash
# Check if conda is active
conda info --envs

# Check current conda environment
conda info | grep "active environment"

# Check pip location (should match your environment)
which pip
pip --version
```

**Expected Output Analysis:**

- If `VIRTUAL_ENV` is empty and you should be in a venv, activate it
- If conda shows "base" but you need a specific env, activate the correct one
- Pip location should match your Python environment path

### Step 2: Package Installation Verification

#### 2.1 Check Current Installations

```bash
# List all installed packages
pip list | grep -i vllm

# Check for potential vLLM installations
pip show vllm

# Check for conflicting packages
pip list | grep -E "(torch|cuda|nvidia)"
```

#### 2.2 Verify Python Path and Module Discovery

```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Try to import vllm directly
python -c "import vllm; print(vllm.__version__)"

# Check if vllm entrypoints exist
python -c "import vllm.entrypoints.openai.api_server"
```

**Expected Outputs:**

```bash
# If vLLM is properly installed:
$ pip show vllm
Name: vllm
Version: 0.6.0
Location: /path/to/your/env/lib/python3.x/site-packages

# If import succeeds:
$ python -c "import vllm; print(vllm.__version__)"
0.6.0
```

### Step 3: Environment Setup and Isolation

#### 3.1 Create Clean Environment

```bash
# Option A: Using venv
python -m venv vllm_env
source vllm_env/bin/activate  # On Windows: vllm_env\Scripts\activate

# Option B: Using conda
conda create -n vllm_env python=3.11
conda activate vllm_env

# Verify environment is active
which python
echo $VIRTUAL_ENV  # or conda info | grep "active environment"
```

#### 3.2 Environment Variables Check

```bash
# Check PATH
echo $PATH

# Check PYTHONPATH (should be empty or not conflicting)
echo $PYTHONPATH

# Check CUDA environment variables
echo $CUDA_HOME
echo $CUDA_PATH
nvcc --version  # Check CUDA compiler version
nvidia-smi     # Check GPU and CUDA runtime version
```

### Step 4: System Configuration Analysis

#### 4.1 GPU and CUDA Compatibility Check

```bash
# Check GPU availability
nvidia-smi

# Check CUDA version compatibility
nvcc --version
cat /usr/local/cuda/version.txt  # Alternative CUDA version check

# Check PyTorch CUDA compatibility
python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.version.cuda}')"
```

**vLLM CUDA Requirements:**

- CUDA 11.8+ or 12.1+
- Compatible GPU with compute capability 7.0+
- Sufficient GPU memory (typically 8GB+ for smaller models)

#### 4.2 System Dependencies

```bash
# Check for required system libraries
ldconfig -p | grep cuda
ldconfig -p | grep cublas
ldconfig -p | grep curand

# Check Python development headers
python -c "import sysconfig; print(sysconfig.get_path('include'))"
ls -la $(python -c "import sysconfig; print(sysconfig.get_path('include'))")
```

### Step 5: Installation Methods

#### 5.1 Standard Installation (Recommended)

```bash
# Upgrade pip first
pip install --upgrade pip

# Install vLLM with CUDA support
pip install vllm

# Verify installation
pip show vllm
python -c "import vllm; print('vLLM version:', vllm.__version__)"
```

#### 5.2 Specific CUDA Version Installation

```bash
# For CUDA 11.8
pip install vllm --extra-index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install vllm --extra-index-url https://download.pytorch.org/whl/cu121

# For specific vLLM version
pip install vllm==0.6.0
```

#### 5.3 Development Installation

```bash
# Clone and install from source (if pip installation fails)
git clone https://github.com/vllm-project/vllm.git
cd vllm
pip install -e .

# Alternative: Install specific commit
pip install git+https://github.com/vllm-project/vllm.git@v0.6.0
```

#### 5.4 Alternative Installation Methods

```bash
# Using conda-forge (if available)
conda install -c conda-forge vllm

# Using Docker (containerized approach)
docker pull vllm/vllm-openai:latest
docker run --gpus all -p 8000:8000 vllm/vllm-openai:latest

# Pre-built wheels (check https://github.com/vllm-project/vllm/releases)
pip install https://github.com/vllm-project/vllm/releases/download/v0.6.0/vllm-0.6.0-py3-none-any.whl
```

### Step 6: Dependency Resolution

#### 6.1 Resolve Common Dependency Conflicts

```bash
# Check for conflicting PyTorch versions
pip list | grep torch

# Uninstall conflicting packages if needed
pip uninstall torch torchvision torchaudio -y

# Reinstall compatible versions
pip install torch==2.4.0 torchvision==0.19.0 --extra-index-url https://download.pytorch.org/whl/cu121

# Install vLLM after PyTorch
pip install vllm
```

#### 6.2 Handle Specific Package Conflicts

```bash
# Common conflicting packages and solutions
pip uninstall transformer-engine flash-attn -y  # Remove if causing conflicts

# Install with specific constraints
pip install vllm --no-deps  # Install without dependencies
pip install -r vllm_requirements.txt  # Install dependencies separately

# Check for duplicate installations
pip list --duplicates
```

### Step 7: Verification and Testing

#### 7.1 Basic Import Tests

```bash
# Test basic import
python -c "import vllm"

# Test specific modules
python -c "from vllm import LLM"
python -c "from vllm.entrypoints.openai.api_server import main"

# Test API server availability
python -c "import vllm.entrypoints.openai.api_server as api; print('API server module loaded')"
```

#### 7.2 Functional Testing

```bash
# Test vLLM CLI availability
vllm --help

# Test with a small model (CPU/GPU test)
python -c "
from vllm import LLM
llm = LLM(model='facebook/opt-125m', max_model_len=512)
print('Model loaded successfully')
"

# Test API server startup (dry run)
python -m vllm.entrypoints.openai.api_server --help
```

#### 7.3 API Server Launch Test

```bash
# Test API server with minimal configuration
python -m vllm.entrypoints.openai.api_server \
  --model facebook/opt-125m \
  --port 8000 \
  --max-model-len 512 \
  --disable-log-requests &

# Test API endpoint
curl http://localhost:8000/v1/models

# Stop test server
pkill -f "vllm.entrypoints.openai.api_server"
```

### Step 8: Advanced Troubleshooting

#### 8.1 Debug Import Paths

```bash
# Detailed Python path analysis
python -c "
import sys
import os
print('Python executable:', sys.executable)
print('Python version:', sys.version)
print('Python path:')
for p in sys.path:
    print(' ', p)

try:
    import vllm
    print('vLLM location:', vllm.__file__)
    print('vLLM version:', vllm.__version__)
except ImportError as e:
    print('Import error:', e)
"
```

#### 8.2 Check for Installation Corruption

```bash
# Reinstall vLLM cleanly
pip uninstall vllm -y
pip cache purge
pip install vllm --no-cache-dir --force-reinstall

# Check installation integrity
python -c "
import pkg_resources
try:
    pkg_resources.require('vllm')
    print('Package requirements satisfied')
except Exception as e:
    print('Package requirements error:', e)
"
```

#### 8.3 Platform-Specific Issues

**Linux-specific checks:**

```bash
# Check glibc version (vLLM requires glibc 2.17+)
ldd --version

# Check available shared libraries
ldconfig -v | grep -E "(cuda|cublas)"

# Check for conflicting Python installations
ls -la /usr/bin/python*
ls -la /usr/local/bin/python*
```

**macOS-specific checks:**

```bash
# Note: vLLM has limited macOS support, mainly CPU-only
# Check for Homebrew Python conflicts
brew list | grep python
which -a python3

# Install CPU-only version if needed
pip install vllm-cpu-only  # If available
```

**Windows-specific checks:**

```bash
# Check Visual C++ runtime
where cl  # Should show MSVC compiler if available

# Windows often requires pre-built wheels
pip install vllm --find-links https://download.pytorch.org/whl/torch_stable.html
```

### Step 9: Alternative Solutions

#### 9.1 Docker-based Solution

```bash
# Use official vLLM Docker image
docker pull vllm/vllm-openai:latest

# Run with GPU support
docker run --gpus all \
  -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:latest \
  --model facebook/opt-6.7b

# Test the API
curl http://localhost:8000/v1/models
```

#### 9.2 Conda Environment Solution

```bash
# Create conda environment with specific Python version
conda create -n vllm python=3.11 -y
conda activate vllm

# Install CUDA toolkit through conda
conda install cuda-toolkit -c conda-forge

# Install PyTorch with CUDA
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia

# Install vLLM
pip install vllm
```

#### 9.3 Source Installation for Edge Cases

```bash
# Clone repository
git clone https://github.com/vllm-project/vllm.git
cd vllm

# Install build dependencies
pip install -e ".[build]"

# Build and install
python setup.py build_ext --inplace
pip install -e .
```

### Step 10: Common Error Solutions

#### 10.1 "No module named 'vllm'" after installation

```bash
# Solution 1: Check Python interpreter
python -m pip show vllm  # Should show package info
python3 -m pip show vllm  # Try with python3

# Solution 2: Reinstall in correct environment
pip uninstall vllm
pip install vllm

# Solution 3: Check for multiple Python installations
python -c "import site; print(site.getsitepackages())"
```

#### 10.2 "CUDA out of memory" or GPU issues

```bash
# Check GPU memory
nvidia-smi

# Install CPU-only version for testing
pip install vllm --extra-index-url https://download.pytorch.org/whl/cpu

# Reduce model size for testing
python -c "
from vllm import LLM
llm = LLM(model='facebook/opt-125m', gpu_memory_utilization=0.5)
"
```

#### 10.3 "Permission denied" or write access issues

```bash
# Install with user flag
pip install --user vllm

# Check permissions
ls -la $(python -c "import site; print(site.getsitepackages()[0])")

# Use virtual environment to avoid permission issues
python -m venv vllm_env
source vllm_env/bin/activate
pip install vllm
```

### Final Verification Checklist

✅ **Environment Check:**

- [ ] Correct Python version (3.8+)
- [ ] Virtual environment activated
- [ ] No conflicting Python installations

✅ **Package Installation:**

- [ ] `pip show vllm` shows package details
- [ ] `python -c "import vllm"` succeeds
- [ ] `python -m vllm.entrypoints.openai.api_server --help` works

✅ **System Dependencies:**

- [ ] CUDA toolkit installed (for GPU usage)
- [ ] Compatible GPU drivers
- [ ] Sufficient system memory

✅ **Functional Test:**

- [ ] Can import vLLM modules
- [ ] Can instantiate LLM class
- [ ] Can run API server

### Quick Fix Commands Summary

```bash
# Quick diagnostic
python --version && pip show vllm && python -c "import vllm"

# Quick reinstall
pip uninstall vllm -y && pip install vllm --no-cache-dir

# Quick test
python -c "from vllm import LLM; print('vLLM working')"

# Quick API test
python -m vllm.entrypoints.openai.api_server --model facebook/opt-125m --port 8000 &
curl http://localhost:8000/v1/models
pkill -f api_server
```

This systematic approach should resolve most vLLM installation and import issues. If problems persist, consider using the Docker-based solution or consulting the [vLLM GitHub issues](https://github.com/vllm-project/vllm/issues) for specific error patterns.
