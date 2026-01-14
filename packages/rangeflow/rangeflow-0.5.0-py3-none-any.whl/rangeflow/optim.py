"""
RangeFlow Optimizers
====================
Advanced optimizers for robust and efficient training.

Includes:
1. GRIP: Gradient Robust Interval Propagation
2. Muon: Momentum Orthogonalized by Newton-Schulz
3. CertifiedLoss: Hull-Prop for certified training
"""

import torch
from torch.optim import Optimizer
import torch.nn as nn


# ==========================================
# GRIP OPTIMIZER
# ==========================================

class GRIP(Optimizer):
    """
    GRIP: Gradient Robust Interval Propagation (Turbo Edition)
    
    The ultimate optimizer for Interval Neural Networks.
    Combines 'Turbo' acceleration (L1 scaling) with 'Interval' braking.
    
    Algorithm:
        1. Momentum: Standard EMA of gradients.
        2. Scale: EMA of L1 Norm (|g|) -> Faster/Smoother than Adam's L2.
        3. Brake: Instantaneous Interval Width -> Stabilizes uncertainty.
        
    Update:
        w = w - lr * momentum / (smooth_l1_scale + interval_width + epsilon)
        
    Args:
        params: Model parameters
        lr: Learning rate (default: 1e-3)
        betas: Coefficients for (momentum, l1_scale) (default: 0.9, 0.99)
        weight_decay: Decoupled weight decay (default: 0)
        epsilon: Stability term (default: 1e-8)
    
    Example:
        >>> model = RobustCNN()
        >>> optimizer = GRIP(model.parameters(), lr=1e-3)
        >>> 
        >>> for data, target in train_loader:
        >>>     optimizer.zero_grad()
        >>>     loss = train_step(model, data, target)
        >>>     loss.backward()
        >>>     optimizer.step()
    """
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.99), weight_decay=0, epsilon=1e-8):
        if not 0.0 <= lr:
            raise ValueError(f"Invalid learning rate: {lr}")
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError(f"Invalid beta1: {betas[0]}")
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError(f"Invalid beta2: {betas[1]}")
        
        defaults = dict(lr=lr, betas=betas, weight_decay=weight_decay, epsilon=epsilon)
        super(GRIP, self).__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None):
        """Performs a single optimization step."""
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            beta1, beta2 = group['betas']
            
            for p in group['params']:
                if p.grad is None:
                    continue
                
                grad = p.grad
                if grad.is_sparse:
                    raise RuntimeError('GRIP does not support sparse gradients')

                state = self.state[p]

                # State initialization
                if len(state) == 0:
                    state['step'] = 0
                    state['exp_avg'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    state['exp_avg_abs'] = torch.zeros_like(p, memory_format=torch.preserve_format)

                exp_avg, exp_avg_abs = state['exp_avg'], state['exp_avg_abs']
                state['step'] += 1

                # 1. Update Momentum (m)
                exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)
                
                # 2. Update Smooth L1 Scale (d) - The "Turbo" Engine
                # Tracks the average MAGNITUDE of gradients.
                exp_avg_abs.mul_(beta2).add_(grad.abs(), alpha=1 - beta2)

                # 3. Get RangeFlow Uncertainty (The Brake)
                # If the parameter has an attached 'interval_width' attribute (populated by RangeFlow),
                # we use it. Otherwise, we assume 0 uncertainty (standard Turbo behavior).
                if hasattr(p, 'interval_width'):
                    uncertainty = p.interval_width
                else:
                    uncertainty = torch.zeros_like(grad)

                # 4. Bias Correction
                # Corrects for the fact that EMA starts at 0
                bias_correction1 = 1 - beta1 ** state['step']
                bias_correction2 = 1 - beta2 ** state['step']
                
                m_hat = exp_avg / bias_correction1
                d_hat = exp_avg_abs / bias_correction2

                # 5. The Update
                # Denominator = Smooth_Scale + Instant_Uncertainty + Epsilon
                denom = d_hat.add(uncertainty).add(group['epsilon'])
                
                # 6. Decoupled Weight Decay
                if group['weight_decay'] > 0:
                    p.mul_(1 - group['lr'] * group['weight_decay'])

                p.addcdiv_(m_hat, denom, value=-group['lr'])

        return loss


# ==========================================
# MUON OPTIMIZER
# ==========================================

class Muon(Optimizer):
    """
    Muon: Momentum Orthogonalized by Newton-Schulz
    
    Key Innovation: Orthogonalizes gradients before applying momentum.
    This prevents gradient interference and accelerates convergence.
    
    Mathematical Foundation:
    -----------------------
    Standard momentum: m_t = β*m_{t-1} + g_t
    
    Muon momentum: 
    1. Orthogonalize: G_orth = NewtonSchulz(g_t)  where G_orth^T G_orth = I
    2. Momentum: m_t = β*m_{t-1} + G_orth
    
    Newton-Schulz Iteration:
    -----------------------
    For matrix G, we want to find G_orth such that G_orth^T G_orth = I
    
    Iteration: G_{k+1} = G_k * (3I - G_k^T G_k) / 2
    Converges to orthogonal matrix in ~5 iterations
    
    Why This Works:
    --------------
    Standard gradients can point in conflicting directions across layers.
    Orthogonalization ensures gradients are "independent", reducing interference.
    
    Args:
        params: Model parameters
        lr: Learning rate (default: 1e-3)
        momentum: Momentum coefficient (default: 0.9)
        nesterov: Whether to use Nesterov momentum (default: True)
        ns_steps: Newton-Schulz iterations (default: 5)
    
    Example:
        >>> model = TransformerModel()
        >>> optimizer = Muon(model.parameters(), lr=1e-3, momentum=0.95)
        >>> 
        >>> for batch in train_loader:
        >>>     optimizer.zero_grad()
        >>>     loss = compute_loss(model, batch)
        >>>     loss.backward()
        >>>     optimizer.step()
    """
    
    def __init__(self, params, lr=1e-3, momentum=0.9, nesterov=True, 
                 ns_steps=5, weight_decay=0, eps=1e-8):
        if not 0.0 <= lr:
            raise ValueError(f"Invalid learning rate: {lr}")
        if not 0.0 <= momentum < 1.0:
            raise ValueError(f"Invalid momentum: {momentum}")
        
        defaults = dict(
            lr=lr, 
            momentum=momentum, 
            nesterov=nesterov,
            ns_steps=ns_steps,
            weight_decay=weight_decay,
            eps=eps
        )
        super(Muon, self).__init__(params, defaults)
    
    @staticmethod
    def newton_schulz_orthogonalize(G, steps=5):
        """
        Newton-Schulz orthogonalization.
        
        Converges to matrix G_orth where G_orth^T @ G_orth = I
        
        Algorithm:
        ---------
        G_0 = G / ||G||_F  (Frobenius norm normalization)
        G_{k+1} = G_k @ (3I - G_k^T @ G_k) / 2
        
        Args:
            G: Input matrix (must be 2D)
            steps: Number of iterations (5 is usually sufficient)
        
        Returns:
            G_orth: Orthogonalized matrix
        """
        if G.dim() != 2:
            # Can only orthogonalize 2D tensors
            return G
        
        # Normalize by Frobenius norm
        G_norm = G / (G.norm() + 1e-8)
        
        # Newton-Schulz iteration
        G_k = G_norm
        I = torch.eye(G.shape[1], device=G.device, dtype=G.dtype)
        
        for _ in range(steps):
            # G_{k+1} = G_k * (3I - G_k^T * G_k) / 2
            G_k_T_G_k = G_k.T @ G_k
            G_k = G_k @ (3 * I - G_k_T_G_k) / 2
        
        return G_k
    
    @torch.no_grad()
    def step(self, closure=None):
        """Performs a single optimization step with orthogonalization."""
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()
        
        for group in self.param_groups:
            momentum = group['momentum']
            ns_steps = group['ns_steps']
            
            for p in group['params']:
                if p.grad is None:
                    continue
                
                grad = p.grad
                
                state = self.state[p]
                
                # State initialization
                if len(state) == 0:
                    state['momentum_buffer'] = torch.zeros_like(p)
                
                buf = state['momentum_buffer']
                
                # Orthogonalize gradient (only for 2D tensors)
                if grad.dim() == 2:
                    # This is a weight matrix - apply Newton-Schulz
                    grad_orth = self.newton_schulz_orthogonalize(grad, steps=ns_steps)
                else:
                    # This is a bias/norm parameter - skip orthogonalization
                    grad_orth = grad
                
                # Momentum update
                buf.mul_(momentum).add_(grad_orth)
                
                # Nesterov momentum
                if group['nesterov']:
                    update = grad_orth + momentum * buf
                else:
                    update = buf
                
                # Weight decay
                if group['weight_decay'] > 0:
                    p.mul_(1 - group['lr'] * group['weight_decay'])
                
                # Parameter update
                p.add_(update, alpha=-group['lr'])
        
        return loss


# ==========================================
# CERTIFIED LOSS (Hull-Prop)
# ==========================================

class CertifiedLoss(nn.Module):
    """
    The 'Box-Prop' Loss Function (Hull-Gradient Descent).
    
    Optimizes for two simultaneous goals:
    1. Shift: The center/worst-case prediction must be correct (Accuracy).
    2. Squeeze: The output interval width must be minimized (Precision).
    
    Mathematical Foundation:
    -----------------------
    Standard training: Minimize CrossEntropy(f(x), y)
    
    Certified training: Minimize both:
    - Robust accuracy: CrossEntropy(f([x-ε, x+ε]), y)  [Shift the hull]
    - Tight bounds: Mean(Width(f([x-ε, x+ε])))  [Squeeze the hull]
    
    Formula:
        L = α * CrossEntropy(Robust_Logits, Target) + β * Mean(Width)
    
    Why This Works:
    --------------
    - α term: Forces correct predictions even under perturbations
    - β term: Prevents uncertainty explosion (keeps bounds tight)
    
    Together, they create a "hull" that:
    1. Contains the correct prediction (shifted right)
    2. Is as narrow as possible (squeezed)
    
    Args:
        alpha: Weight for the Robust Accuracy term (default: 1.0)
        beta: Weight for the Squeeze (Width penalty) term (default: 0.1)
    
    Example:
        >>> loss_fn = CertifiedLoss(alpha=1.0, beta=0.1)
        >>> 
        >>> x_range = RangeTensor.from_epsilon_ball(x, epsilon=0.3)
        >>> y_range = model(x_range)
        >>> loss = loss_fn(y_range, target)
        >>> loss.backward()
    """
    def __init__(self, alpha=1.0, beta=0.1):
        super().__init__()
        self.alpha = alpha 
        self.beta = beta   

    def forward(self, y_range, target):
        """
        Compute certified loss.
        
        Args:
            y_range: Output RangeTensor from the model (batch, num_classes)
            target: Ground truth labels (batch,)
        
        Returns:
            Scalar loss combining robust accuracy and width penalty
        """
        # 1. Decompose into bounds
        # l = Lower Bound (Optimistic), u = Upper Bound (Pessimistic)
        l, u = y_range.decay()
        
        # 2. The Robust Signal (Shift)
        # We use the center to guide optimization
        center = (l + u) / 2.0
        
        # Handle backend compatibility
        if not isinstance(center, torch.Tensor):
            raise NotImplementedError("CertifiedLoss requires PyTorch backend")
        
        # Standard cross-entropy on center
        loss_robust = torch.nn.functional.cross_entropy(center, target)
        
        # 3. The Squeeze Signal (Width penalty)
        width = u - l
        loss_width = width.mean()
        
        # 4. Total "Hull-Gradient" Loss
        return (self.alpha * loss_robust) + (self.beta * loss_width)


# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def attach_interval_width_hook(model):
    """
    Attach hooks to track interval widths for GRIP optimizer.
    
    This enables the "brake" mechanism in GRIP by populating
    the interval_width attribute on parameters during backprop.
    
    Args:
        model: RangeFlow model
    
    Example:
        >>> model = RobustCNN()
        >>> attach_interval_width_hook(model)
        >>> optimizer = GRIP(model.parameters())
        >>> # Now GRIP will use interval widths automatically
    """
    from .core import RangeTensor
    
    def width_hook(module, input, output):
        """Hook to extract width from RangeTensor outputs"""
        if isinstance(output, RangeTensor):
            width = output.width()
            
            # Attach width to module parameters
            for param in module.parameters():
                if param.requires_grad:
                    param.interval_width = width.mean()
    
    # Register hooks on all modules
    for module in model.modules():
        if hasattr(module, 'forward'):
            module.register_forward_hook(width_hook)
    
    print("✓ Interval width hooks attached for GRIP optimizer")


def compare_optimizers(model_class, train_loader, val_loader, epochs=10):
    """
    Compare GRIP, Muon, and Adam on the same task.
    
    Args:
        model_class: Model constructor
        train_loader: Training data
        val_loader: Validation data
        epochs: Number of epochs
    
    Returns:
        Dict with comparison results
    """
    import copy
    
    optimizers_to_test = {
        'Adam': lambda params: torch.optim.Adam(params, lr=1e-3),
        'GRIP': lambda params: GRIP(params, lr=1e-3),
        'Muon': lambda params: Muon(params, lr=1e-3, momentum=0.95)
    }
    
    results = {}
    
    for name, opt_fn in optimizers_to_test.items():
        print(f"\nTraining with {name}...")
        
        model = model_class()
        optimizer = opt_fn(model.parameters())
        
        train_losses = []
        val_accs = []
        
        for epoch in range(epochs):
            # Train
            model.train()
            epoch_loss = 0.0
            for data, target in train_loader:
                optimizer.zero_grad()
                output = model(data)
                if hasattr(output, 'avg'):
                    output = output.avg()
                loss = torch.nn.functional.cross_entropy(output, target)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
            
            train_losses.append(epoch_loss / len(train_loader))
            
            # Validate
            model.eval()
            correct = 0
            total = 0
            with torch.no_grad():
                for data, target in val_loader:
                    output = model(data)
                    if hasattr(output, 'avg'):
                        output = output.avg()
                    pred = output.argmax(dim=1)
                    correct += pred.eq(target).sum().item()
                    total += target.size(0)
            
            val_accs.append(correct / total)
            print(f"  Epoch {epoch+1}: Loss={train_losses[-1]:.4f}, Acc={val_accs[-1]:.2%}")
        
        results[name] = {
            'train_losses': train_losses,
            'val_accs': val_accs,
            'final_acc': val_accs[-1]
        }
    
    # Print summary
    print("\n" + "="*50)
    print("OPTIMIZER COMPARISON SUMMARY")
    print("="*50)
    for name, res in results.items():
        print(f"{name:10s}: Final Acc = {res['final_acc']:.2%}")
    
    return results


# Export all public APIs
__all__ = [
    'GRIP',
    'Muon',
    'CertifiedLoss',
    'attach_interval_width_hook',
    'compare_optimizers'
]