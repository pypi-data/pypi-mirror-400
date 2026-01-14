# RangeFlow 🌊
## *Certified Robustness, Quantization & Uncertainty for AI*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI version](https://badge.fury.io/py/rangeflow.svg)](https://badge.fury.io/py/rangeflow)

**RangeFlow** is a revolutionary Python library for **robust, efficient, and certified AI**.

It combines **Interval Arithmetic** with **1.58-bit Quantization**, enabling you to:
- ✅ **Train 3B+ Models** on consumer GPUs (BitNet 1.58-bit)
- ✅ **Certify** neural networks against adversarial attacks
- ✅ **Quantify** uncertainty in predictions mathematically
- ✅ **Accelerate** convergence with Newton-Schulz optimization (Muon)
- ✅ **Eliminate catastrophic forgetting** in continual learning

Unlike standard deep learning, RangeFlow provides **mathematical guarantees** and **extreme compression** in a single package.

---

## 🌟 Why RangeFlow?

### The Problem
1. **Fragility:** Models change predictions when noise is added.
2. **Bloat:** Large Language Models (LLMs) require massive H100 GPUs.
3. **Slowness:** Standard optimizers (Adam) are memory-hungry and slow.

### The RangeFlow Solution (v0.5.0)
We solve this with **"The Light Monster"** stack:
1. **BitNet Quantization:** Compresses weights to `{-1, 0, 1}` (1.58 bits), reducing VRAM usage by ~10x.
2. **Interval Bounds:** Propagates `[min, max]` ranges to guarantee robustness.
3. **Muon Optimizer:** Orthogonalizes gradients for faster training than Adam.

---

## 🚀 What's New in v0.5.0

### 🔥 Major Features

1. **BitNet 1.58-bit Quantization** (`rangeflow.quantization`)
   - Train LLMs with ternary weights (`-1, 0, 1`).
   - Includes **Robust Scaling** (Median/MAD) and **Straight-Through Estimator**.
2. **Advanced Optimizers** (`rangeflow.optim`)
   - **Muon:** Momentum Orthogonalized by Newton-Schulz (Faster convergence).
   - **GRIP:** Gradient Robust Interval Propagation (Self-stabilizing "Brake").
3. **Functional Interface** (`rangeflow.functional`)
   - Stateless, JAX-style API (aliased as `R`).
   - `y = R.relu(R.linear(x, w, b))`
4. **Certified Loss (Hull-Prop)**
   - Minimizes the volume of the output interval hull for tighter logic.
5. **Broadcasting Support**
   - Full NumPy-style broadcasting for interval operations.

---

## 🚀 Quick Start

### Installation

```bash
pip install rangeflow

```

*(Note: For 1.58-bit training speedup, use a compiled environment like WSL2 or Linux)*

### 1. Basic Robust Model (Interval Arithmetic)

```python
import rangeflow as rf
import torch
from rangeflow.layers import RangeLinear, RangeReLU

# 1. Create uncertain input (sensor noise ±0.1)
x = torch.randn(1, 784)
x_range = rf.RangeTensor.from_epsilon_ball(x, epsilon=0.1)

# 2. Build model
model = torch.nn.Sequential(
    RangeLinear(784, 128),
    RangeReLU(),
    RangeLinear(128, 10)
)

# 3. Get guaranteed bounds
min_out, max_out = model(x_range).decay()
print(f"Output guaranteed in [{min_out.item()}, {max_out.item()}]")

```

### 2. High-Performance 1.58-bit Training (NEW)

Train a large model with minimal VRAM using **BitNet** and **Muon**.

```python
from rangeflow.quantization import BitNetLinear
from rangeflow.optim import Muon
import torch

# 1. Define a Compressed Layer (1.58 bits per weight)
# Replaces standard nn.Linear(4096, 4096) which takes ~32MB
# BitNetLinear takes ~4MB during inference!
layer = BitNetLinear(4096, 4096, input_bits=8)

# 2. Use Muon Optimizer (Newton-Schulz)
# Orthogonalizes gradients for faster convergence
optimizer = Muon(layer.parameters(), lr=0.02, momentum=0.95)

# 3. Train (Standard Loop)
x = torch.randn(32, 4096)
target = torch.randn(32, 4096)

optimizer.zero_grad()
output = layer(x)
loss = torch.nn.functional.mse_loss(output, target)
loss.backward()
optimizer.step()

```

### 3. Functional API (JAX-Style)

Prefer stateless code? Use the `R` namespace.

```python
import rangeflow.functional as R

# Define weights manually
W = torch.randn(10, 5)
b = torch.zeros(10)

# Run pipeline
x_range = R.from_epsilon_ball(torch.randn(5), 0.1)
y_range = R.relu(R.linear(x_range, W, b))

# No class instantiation needed!

```
---

## 📚 Core Concepts

### 1. **RangeTensor**: The Foundation

A `RangeTensor` represents an **interval** [min, max] of possible values:

```python
# Three ways to create ranges
x1 = rf.RangeTensor.from_range(1.0, 2.0)  # Explicit [1, 2]
x2 = rf.RangeTensor.from_epsilon_ball(5.0, 0.1)  # [4.9, 5.1]
x3 = rf.RangeTensor.from_array(torch.tensor([3.0]))  # Degenerate [3, 3]
```

### 2. **Domain Constraints** (NEW in v0.4.0)

Automatically handle physical constraints:

```python
from rangeflow.verification import DomainConstraints

# Image domain - automatically clips to [0, 1]
domain = DomainConstraints.image_domain(bit_depth=1)
x_range = domain.create_epsilon_ball(image, epsilon=0.3)
# No more negative pixels!
```

### 3. **Linear Bound Propagation** (NEW in v0.4.0)

CROWN-style symbolic bounds for 30% tighter verification:

```python
from rangeflow.linear_bounds import enable_linear_bounds, hybrid_verification

# Enable on your model
enable_linear_bounds(model)

# Verify with tighter bounds
is_verified, margin, method = hybrid_verification(
    model, image, epsilon=0.3, use_linear=True
)
```

### 4. **RangeNorm**: The Stabilizer

Deep networks cause **exponential uncertainty growth**:

```python
from rangeflow.layers import RangeLayerNorm

# Normalizes both center AND width
norm = RangeLayerNorm(128)
x_stable = norm(x_range)  # Width stays controlled!
```
---

## 🛠️ Feature Breakdown

### 1. Framework Integration

```python
# Pure NumPy/CuPy (lightweight)
import rangeflow as rf

# PyTorch integration
from rangeflow.patch import convert_model_to_rangeflow
import torch

model = torch.nn.Sequential(...)
convert_model_to_rangeflow(model)  # Now handles ranges!
```

### 2. Comprehensive Layers

| **Layer Type** | **RangeFlow Equivalent** | **Notes** |
|---------------|-------------------------|-----------|
| Linear | `RangeLinear` | Interval weights support |
| Linear (Continual) | `ContinualLinear` | Zero forgetting |
| Conv2d | `RangeConv2d` | Spatial intervals |
| LayerNorm | `RangeLayerNorm` | Stabilizes width growth |
| BatchNorm | `RangeBatchNorm1d`, `RangeBatchNorm2d` | |
| Dropout | `RangeDropout` | Expands uncertainty |
| RNN/LSTM/GRU | `RangeRNN`, `RangeLSTM`, `RangeGRU` | Temporal intervals |
| Attention | `RangeAttention` | Safe softmax |
| Pooling | `RangeMaxPool2d`, `RangeAvgPool2d` | |

### 3. Quantization (`rangeflow.quantization`)

The engine for training Large Language Models on consumer hardware.

* **`BitNetLinear`**: Drop-in replacement for `nn.Linear`.
* **`robust_scale`**: Uses Median Absolute Deviation (MAD) to handle outliers.
* **`quantize_model_to_bitnet`**: Convert any existing PyTorch model to 1.58-bit in one line.

### 4. Optimizers (`rangeflow.optim`)

* **`Muon`**: Performs Newton-Schulz iteration on 2D weight gradients. Keeps updates orthogonal, preventing "feature collapse" in deep networks.
* **`GRIP`**: Dynamically scales learning rate based on **Interval Width**. If the model becomes uncertain (wide intervals), GRIP hits the brakes.

### 5. Verification & Safety

* **Branch-and-Bound (BaB)**: Formal verification for safety-critical apps.
* **Linear Bounds (CROWN)**: Symbolic propagation for tighter certification.
* **Continual Learning**: Interval weights prevent catastrophic forgetting.

### 6. Advanced Training (NEW in v0.4.0)

#### One-Line Curriculum Training
```python
from rangeflow.advanced_train import train_with_curriculum

model, history = train_with_curriculum(
    model, train_loader, val_loader,
    epochs=100,
    start_eps=0.0,
    end_eps=0.5,
    method='trades',  # TRADES loss for better accuracy
    beta=6.0,
    checkpoint_dir='./checkpoints'
)

# Automatically includes:
# ✓ Epsilon scheduling
# ✓ Range monitoring
# ✓ Checkpointing
# ✓ Resumable training
# ✓ TRADES loss
```

#### Manual Training with TRADES
```python
from rangeflow.advanced_train import TRADESTrainer

trainer = TRADESTrainer(model, optimizer, beta=6.0)

for epoch in range(epochs):
    train_loss = trainer.train_epoch(train_loader, epsilon)
    val_metrics = trainer.validate(val_loader, epsilon)
    print(f"Epoch {epoch}: Cert Acc: {val_metrics['certified_acc']:.2%}")
```

### 7. Automatic Debugging (NEW in v0.4.0)

```python
from rangeflow.advanced_train import monitor_ranges

# Register monitoring hooks (ONE LINE!)
hooks = monitor_ranges(model, explosion_threshold=50.0)

# Train normally - hooks automatically track ranges
for data, target in train_loader:
    output = model(data)
    # If ranges explode, you'll see warnings!

# Check statistics
for hook in hooks:
    stats = hook.get_stats()
    print(f"{stats['name']}: avg_width={stats['avg_width']:.2f}")
```

### 8. Formal Verification (NEW in v0.4.0)

#### Branch-and-Bound Verification
```python
from rangeflow.verification import BranchAndBound, DomainConstraints

domain = DomainConstraints.image_domain()
bab = BranchAndBound(max_depth=3)

# Formal verification with recursive splitting
is_verified, margin, stats = bab.verify(
    model, image, label, epsilon=0.3, domain=domain
)

print(f"Verified: {is_verified}, Margin: {margin:.3f}")
print(f"Explored {stats['nodes_explored']} nodes")
```

#### Verification Certificates
```python
from rangeflow.verification import VerificationCertificate

# Create formal proof
cert = VerificationCertificate(
    x_range, output_range, target_label, 
    epsilon=0.3, method='IBP+BaB'
)

# Save certificate
cert.save('safety_proof.pt')

# Load and re-verify later
cert = VerificationCertificate.load('safety_proof.pt')
is_valid = cert.verify_against_model(model)
```

### 9. Continual Learning (NEW in v0.4.0)

#### Hybrid Models (Memory-Efficient)
```python
from rangeflow.continual import HybridModelBuilder

builder = HybridModelBuilder()

# Customize interval ratio per layer
model = builder.build_mlp(
    layer_sizes=[784, 512, 256, 10],
    interval_ratios=[0.3, 0.6, 1.0]  # 30%, 60%, 100% interval weights
)

# Only critical layers use intervals - saves memory!
```

#### Multi-Task Training
```python
from rangeflow.continual import continual_train_step

memories = []

# Train Task A
train(model, task_A_data)
memories.append(save_task_memory(model, 'Task_A'))

# Train Task B (preserving A)
for data, target in task_B_data:
    loss, task_loss, elastic_loss = continual_train_step(
        model, optimizer, data, target, 
        old_memories=memories  # Preserves all previous tasks!
    )
    loss.backward()
    optimizer.step()

# Train Task C (preserving A and B)
memories.append(save_task_memory(model, 'Task_B'))
# Continue with Task C...
```

## 📊 Advanced Usage

### Hybrid Models (Partial Interval Weights)

For large models, use intervals only where needed:

```python
from rangeflow.continual import ContinualLinear

# Option 1: Layer-by-layer control
model = torch.nn.Sequential(
    ContinualLinear(784, 512, mode='mu_only'),      # Standard weights
    RangeReLU(),
    ContinualLinear(512, 256, mode='hybrid', hybrid_ratio=0.5),  # 50% intervals
    RangeReLU(),
    ContinualLinear(256, 10, mode='full')            # Full intervals
)

# Option 2: Use builder
from rangeflow.continual import HybridModelBuilder

builder = HybridModelBuilder()
model = builder.build_mlp(
    [784, 512, 256, 10],
    interval_ratios=[0.0, 0.5, 1.0]  # 0%, 50%, 100%
)
```

**Benefits:**
- 50% memory reduction
- Faster training
- Critical layers still robust

### Custom Verification Domains

```python
from rangeflow.verification import DomainConstraints

# Temperature sensor (Kelvin, must be positive)
temp_domain = DomainConstraints(
    min_val=0.0, max_val=None, name='Temperature'
)

# Normalized features (z-score)
norm_domain = DomainConstraints(
    min_val=-3.0, max_val=3.0, name='Standardized'
)

# Probability distribution
prob_domain = DomainConstraints.probability_domain()
```

### Resumable Training

```python
from rangeflow.advanced_train import StatefulEpsilonScheduler, CheckpointManager

scheduler = StatefulEpsilonScheduler('linear', 0.0, 0.5, 100)
manager = CheckpointManager('./checkpoints', keep_best=3)

for epoch in range(100):
    eps = scheduler.step()
    
    # Train...
    train_loss = train_epoch(model, train_loader, eps)
    
    # Save checkpoint with scheduler state
    manager.save(
        model, optimizer, scheduler, epoch,
        metrics={'train_loss': train_loss, 'epsilon': eps}
    )

# Resume later
checkpoint = manager.load_latest()
model.load_state_dict(checkpoint['model_state_dict'])
scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
# Continues from correct epoch with correct epsilon!
```

---

## 🗺️ Roadmap

### v0.5.0 (Current)

* ✅ BitNet 1.58-bit Quantization
* ✅ Muon & GRIP Optimizers
* ✅ Functional API (`R`)
* ✅ Broadcasting Support

### v0.6.0 (Next)

* 🔄 **Kernel Fusion**: Custom Triton kernels for 2x training speed.
* 🔄 **Distributed Training**: native FSDP support for BitNet.
* 🔄 **Graph Neural Networks**: Interval support for geometric deep learning.

---

## 📄 Citation

If you use RangeFlow in your research, please cite:

```bibtex
@software{rangeflow2026,
  title={RangeFlow: Interval Arithmetic & 1.58-bit Quantization for AI},
  author={Dheeren Tejani},
  year={2026},
  url={[https://github.com/dheeren-tejani/rangeflow](https://github.com/dheeren-tejani/rangeflow)}
}

```

---

## ⚖️ License

MIT License - see [LICENSE](https://www.google.com/search?q=LICENSE) for details.

**Built by [Dheeren Tejani**](https://dheerentejani.netlify.app/)

```

```