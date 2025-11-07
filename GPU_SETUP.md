# GPU Setup Guide for LLM Service

This guide explains how to enable GPU acceleration for the Ollama LLM service used in the job post analyzer.

## TL;DR

**The service works out of the box with CPU** - GPU is optional for faster processing.

- **With CPU**: ~2-3 seconds per job post (works on any machine, no setup)
- **With GPU**: ~0.5-1 second per job post (3-5x faster, requires NVIDIA GPU)

**For ~100 job posts per day, CPU mode is perfectly adequate.**

---

## Automatic Detection

The Docker container **automatically detects** if a GPU is available:

- ✅ If GPU found → Uses GPU acceleration
- ✅ If no GPU → Falls back to CPU (no errors)

Check the logs to see what's being used:
```bash
docker compose logs llm-consumer | grep -i gpu
```

---

## Option 1: Run with CPU (Default - No Setup Needed)

Simply run:
```bash
docker compose up -d
```

The service will work fine with CPU, just slightly slower.

---

## Option 2: Enable GPU Acceleration (NVIDIA GPUs only)

### Prerequisites

1. **NVIDIA GPU** (not AMD/Intel)
2. **NVIDIA drivers** installed on host
3. **Docker Compose** v2.3+

### Step 1: Verify GPU Works

```bash
nvidia-smi
```

If this command works and shows your GPU, you're ready to proceed.

If it fails, install NVIDIA drivers first:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nvidia-driver-535  # or latest version
sudo reboot
```

### Step 2: Install NVIDIA Container Toolkit

```bash
# Configure repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Step 3: Test GPU in Docker

```bash
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
```

If you see your GPU info, you're all set!

### Step 4: Run with GPU

```bash
# Use GPU-enabled compose file
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

### Step 5: Verify GPU Usage

```bash
# Check logs for GPU detection
docker compose logs llm-consumer | head -20

# Monitor GPU usage in real-time
watch -n 1 nvidia-smi
```

You should see:
- Log message: "GPU detected! Ollama will use GPU acceleration."
- GPU memory usage in `nvidia-smi` when processing jobs

---

## Performance Comparison

| Hardware | Speed per Post | Monthly Volume | Recommendation |
|----------|---------------|----------------|----------------|
| **CPU only** | 2-3 sec | ~100-200 posts/day | Fine for testing |
| **GPU (RTX 3060)** | 0.5-1 sec | ~500-1000 posts/day | Recommended |
| **GPU (RTX 4090)** | 0.3-0.5 sec | 1000+ posts/day | Best performance |

---

## Troubleshooting

### "GPU detected" but still slow?

Check if Ollama is actually using GPU:
```bash
docker exec llm-consumer nvidia-smi
```

### "No GPU detected" but I have one?

Check if NVIDIA runtime is available:
```bash
docker info | grep -i nvidia
```

If empty, reinstall nvidia-container-toolkit (Step 2 above).

### Out of GPU memory?

Reduce model size in `.env`:
```bash
# Instead of llama3.1:8b (requires 8GB VRAM)
OLLAMA_MODEL=llama3.1:3b  # Only needs 3GB VRAM
```

Or increase Docker memory limits in `docker-compose.gpu.yml`.

---

## AMD/Intel GPU Support

Currently, Ollama primarily supports NVIDIA GPUs. For AMD GPUs:

1. Use ROCm-enabled containers (advanced setup)
2. Or stick with CPU mode (works great)

---

---

## Switching Between CPU and GPU Mode

**To use CPU mode (default):**
```bash
docker compose up -d
```

**To use GPU mode:**
```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

**To switch from GPU back to CPU:**
```bash
docker compose down
docker compose up -d
```

The system will automatically detect which mode it's running in and use the appropriate hardware.

---

## Still Have Questions?

The default CPU mode works perfectly fine for most use cases. GPU is optional optimization.

**Recommended approach:**
1. ✅ Start with CPU mode (zero setup)
2. ✅ Let it run and process your job posts
3. ✅ Monitor performance with `docker compose logs -f llm-consumer`
4. ⚡ If too slow, add GPU support following steps above
5. 🚀 Enjoy 3-5x faster processing!

**For ~100 job posts per day, CPU mode is totally adequate.**
