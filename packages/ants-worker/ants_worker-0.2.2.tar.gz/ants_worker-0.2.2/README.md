# Ants Worker

Join the colony. Share your compute.

```bash
pip install ants-worker
ants-worker join
```

That's it. You're now part of the swarm.

## Commands

```bash
ants-worker join           # Register and start working
ants-worker join -t wild   # Run as wild kangaroo (default: tame)
ants-worker status         # Check connection and worker ID
ants-worker leave          # Unregister (delete ~/.ants/config.json)
ants-worker info           # System/GPU info
ants-worker benchmark      # Test performance
```

## Hardware Acceleration

### AMD Ryzen AI (NPU)

```bash
# Auto-detects Ryzen AI and optimizes
ants-worker join

# Check detected hardware
ants-worker info --detailed

# Force specific backend
ants-worker join -b amd_npu
ants-worker join -b amd_rocm
ants-worker join -b parallel_cpu --workers 16
```

### NVIDIA GPU

```bash
pip install ants-worker[cuda]
ants-worker join
```

### High Performance Binary

```bash
# Linux with NVIDIA GPU
git clone https://github.com/JeanLucPons/Kangaroo.git
cd Kangaroo && make gpu=1 && cd ..
export KANGAROO_BIN=$(pwd)/Kangaroo/kangaroo

ants-worker join
```

## Run in Background

### Screen/tmux

```bash
screen -S ants
ants-worker join
# Ctrl+A, D to detach
```

### Systemd (Linux)

```bash
sudo tee /etc/systemd/system/ants-worker.service << 'EOF'
[Unit]
Description=Ants Worker
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/ants-worker join
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now ants-worker
```

## FAQ

**Is this safe?**
Yes. You get a unique token that can only submit work results.

**Resources?**
Minimal bandwidth (~KB/min). CPU/GPU usage configurable. Stop with Ctrl+C.

**Where's my config?**
`~/.ants/config.json` - contains your token and worker ID.

**Tame vs Wild?**
Both needed. Run one of each for maximum contribution:
```bash
ants-worker join -t tame &
ants-worker join -t wild &
```

## Development

```bash
git clone https://github.com/ants-at-work/worker
cd worker
pip install -e ".[dev]"
pytest
```

## Links

- Website: https://ants-at-work.com
- Issues: https://github.com/ants-at-work/worker/issues
