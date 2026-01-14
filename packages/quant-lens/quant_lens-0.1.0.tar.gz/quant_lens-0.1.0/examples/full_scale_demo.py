#!/usr/bin/env python3
"""
CORRECT Experimental Design: Isolating Bit Collapse Effect
============================================================

Hypothesis: Quantization causes sharper minima (bit collapse)

Experimental Design (Controlled):
1. FP32 Training from Scratch
2. Int8 Training from Scratch (same init)
3. Int8 SAM Training from Scratch (same init)

All three start from THE SAME random initialization and train identically
except for the quantization and optimizer.

This isolates the effect of quantization on loss geometry.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torchvision.models import resnet18
import numpy as np
import matplotlib.pyplot as plt
import gc
import os
import random
import copy

from quant_lens import QuantDiagnostic
from quant_lens.quantization import replace_linear_layers


# ==========================================
# CONFIGURATION
# ==========================================
class Config:
    SEED = 42
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
    SAVE_DIR = "bit_collapse_controlled"
    
    # Training - From Scratch
    TRAIN_BATCH_SIZE = 128
    EPOCHS = 50              # Train till convergence
    LR = 0.1                 # Standard ResNet learning rate
    MOMENTUM = 0.9
    WEIGHT_DECAY = 5e-4
    
    # LR Schedule
    LR_MILESTONES = [25, 40]  # Decay at these epochs
    LR_GAMMA = 0.1
    
    # SAM
    SAM_RHO = 0.05
    
    # Analysis
    ANALYSIS_BATCH_SIZE = 32
    ANALYSIS_SAMPLES = 512
    LANDSCAPE_STEPS = 50
    HESSIAN_ITERS = 30


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False  # Reproducibility over speed


# ==========================================
# SAM OPTIMIZER
# ==========================================
class SAM(torch.optim.Optimizer):
    def __init__(self, params, base_optimizer, rho=0.05, **kwargs):
        defaults = dict(rho=rho, **kwargs)
        super(SAM, self).__init__(params, defaults)
        self.base_optimizer = base_optimizer(self.param_groups, **kwargs)
        self.param_groups = self.base_optimizer.param_groups

    @torch.no_grad()
    def first_step(self, zero_grad=False):
        grad_norm = self._grad_norm()
        for group in self.param_groups:
            scale = group["rho"] / (grad_norm + 1e-12)
            for p in group["params"]:
                if p.grad is None:
                    continue
                self.state[p]["e_w"] = p.grad * scale
                p.add_(self.state[p]["e_w"])
        if zero_grad:
            self.zero_grad()

    @torch.no_grad()
    def second_step(self, zero_grad=False):
        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue
                p.sub_(self.state[p]["e_w"])
        self.base_optimizer.step()
        if zero_grad:
            self.zero_grad()

    def _grad_norm(self):
        stack = [
            p.grad.norm(p=2).to(p.device)
            for group in self.param_groups
            for p in group["params"]
            if p.grad is not None
        ]
        return torch.norm(torch.stack(stack), p=2)


# ==========================================
# DATA LOADING
# ==========================================
def get_loaders():
    # Standard CIFAR-10 augmentation
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ])
    
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ])
    
    trainset = torchvision.datasets.CIFAR10(
        root='./data', train=True, download=True, transform=transform_train
    )
    
    testset = torchvision.datasets.CIFAR10(
        root='./data', train=False, download=True, transform=transform_test
    )
    
    train_loader = torch.utils.data.DataLoader(
        trainset, batch_size=Config.TRAIN_BATCH_SIZE, shuffle=True,
        num_workers=2, pin_memory=True
    )
    
    test_loader = torch.utils.data.DataLoader(
        testset, batch_size=Config.ANALYSIS_BATCH_SIZE, shuffle=False,
        num_workers=2, pin_memory=True
    )
    
    # Analysis subset
    from torch.utils.data import Subset
    indices = torch.randperm(len(trainset))[:Config.ANALYSIS_SAMPLES]
    analysis_set = Subset(trainset, indices)
    analysis_loader = torch.utils.data.DataLoader(
        analysis_set, batch_size=Config.ANALYSIS_BATCH_SIZE, shuffle=False
    )
    
    return train_loader, test_loader, analysis_loader


# ==========================================
# TRAINING & EVALUATION
# ==========================================
def train_epoch(model, loader, optimizer, scheduler, use_sam=False):
    model.train()
    criterion = nn.CrossEntropyLoss()
    total_loss = 0.0
    correct = 0
    total = 0
    
    for inputs, targets in loader:
        inputs, targets = inputs.to(Config.DEVICE), targets.to(Config.DEVICE)
        
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        
        if use_sam:
            optimizer.first_step(zero_grad=True)
            criterion(model(inputs), targets).backward()
            optimizer.second_step(zero_grad=True)
        else:
            optimizer.step()
            optimizer.zero_grad()
        
        total_loss += loss.item()
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()
    
    scheduler.step()
    
    return total_loss / len(loader), 100. * correct / total


def evaluate(model, loader):
    model.eval()
    criterion = nn.CrossEntropyLoss()
    total_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for inputs, targets in loader:
            inputs, targets = inputs.to(Config.DEVICE), targets.to(Config.DEVICE)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
    
    return total_loss / len(loader), 100. * correct / total


# ==========================================
# ANALYSIS
# ==========================================
def analyze_model(model, analysis_loader, name):
    print(f"\n[quant-lens] Analyzing {name}...")
    diagnostic = QuantDiagnostic(model, analysis_loader, device=Config.DEVICE)
    metrics = diagnostic.run_analysis(
        landscape_steps=Config.LANDSCAPE_STEPS,
        hessian_iters=Config.HESSIAN_ITERS
    )
    
    sharpness = metrics['FP32']['sharpness']
    alphas, losses = diagnostic.traces['FP32']
    
    return {
        'sharpness': sharpness,
        'alphas': alphas,
        'losses': losses
    }


# ==========================================
# MAIN EXPERIMENT
# ==========================================
def run_controlled_experiment():
    set_seed(Config.SEED)
    os.makedirs(Config.SAVE_DIR, exist_ok=True)
    
    print("="*80)
    print("CONTROLLED BIT COLLAPSE EXPERIMENT")
    print("="*80)
    print("\nHypothesis: Quantization causes sharper minima")
    print("\nExperimental Design:")
    print("  1. Train FP32 model from scratch")
    print("  2. Train Int8 model from scratch (SAME initialization)")
    print("  3. Train Int8+SAM model from scratch (SAME initialization)")
    print("\nThis isolates the effect of quantization on loss geometry.")
    print("="*80)
    
    train_loader, test_loader, analysis_loader = get_loaders()
    results = {}
    
    # =====================================================
    # CREATE SHARED INITIAL STATE
    # =====================================================
    print("\n[Setup] Creating shared initial state...")
    set_seed(Config.SEED)
    
    # Create a fresh model and save its random initialization
    init_model = resnet18(num_classes=10)
    init_model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    init_model.maxpool = nn.Identity()  # Remove maxpool for CIFAR-10
    
    # Save the random initialization
    initial_state = copy.deepcopy(init_model.state_dict())
    print("✓ Shared initialization created")
    
    # =====================================================
    # PHASE 1: FP32 FROM SCRATCH
    # =====================================================
    print("\n" + "="*80)
    print("PHASE 1: FP32 TRAINING FROM SCRATCH")
    print("="*80)
    
    model_fp32 = resnet18(num_classes=10)
    model_fp32.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model_fp32.maxpool = nn.Identity()
    model_fp32.load_state_dict(initial_state)  # Load shared init
    model_fp32 = model_fp32.to(Config.DEVICE)
    
    optimizer_fp32 = optim.SGD(
        model_fp32.parameters(),
        lr=Config.LR,
        momentum=Config.MOMENTUM,
        weight_decay=Config.WEIGHT_DECAY
    )
    scheduler_fp32 = optim.lr_scheduler.MultiStepLR(
        optimizer_fp32, milestones=Config.LR_MILESTONES, gamma=Config.LR_GAMMA
    )
    
    print("Training FP32 model...")
    for epoch in range(Config.EPOCHS):
        train_loss, train_acc = train_epoch(
            model_fp32, train_loader, optimizer_fp32, scheduler_fp32, use_sam=False
        )
        
        if (epoch + 1) % 10 == 0 or epoch == Config.EPOCHS - 1:
            test_loss, test_acc = evaluate(model_fp32, test_loader)
            print(f"  Epoch {epoch+1}/{Config.EPOCHS}: "
                  f"Train Loss={train_loss:.4f}, Train Acc={train_acc:.2f}%, "
                  f"Test Acc={test_acc:.2f}%")
    
    # Final evaluation
    test_loss, test_acc = evaluate(model_fp32, test_loader)
    print(f"\nFinal FP32 Test Accuracy: {test_acc:.2f}%")
    
    results['fp32'] = analyze_model(model_fp32, analysis_loader, "FP32 From Scratch")
    results['fp32']['test_acc'] = test_acc
    
    del model_fp32, optimizer_fp32, scheduler_fp32
    torch.cuda.empty_cache()
    gc.collect()
    
    # =====================================================
    # PHASE 2: INT8 SGD FROM SCRATCH
    # =====================================================
    print("\n" + "="*80)
    print("PHASE 2: INT8 (SGD) TRAINING FROM SCRATCH")
    print("="*80)
    
    model_int8_sgd = resnet18(num_classes=10)
    model_int8_sgd.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model_int8_sgd.maxpool = nn.Identity()
    model_int8_sgd.load_state_dict(initial_state)  # Same init as FP32!
    
    # Apply quantization BEFORE training
    print("Applying 8-bit quantization...")
    model_int8_sgd = replace_linear_layers(model_int8_sgd, num_bits=8)
    model_int8_sgd = model_int8_sgd.to(Config.DEVICE)
    
    optimizer_int8_sgd = optim.SGD(
        model_int8_sgd.parameters(),
        lr=Config.LR,
        momentum=Config.MOMENTUM,
        weight_decay=Config.WEIGHT_DECAY
    )
    scheduler_int8_sgd = optim.lr_scheduler.MultiStepLR(
        optimizer_int8_sgd, milestones=Config.LR_MILESTONES, gamma=Config.LR_GAMMA
    )
    
    print("Training Int8 model (SGD)...")
    for epoch in range(Config.EPOCHS):
        train_loss, train_acc = train_epoch(
            model_int8_sgd, train_loader, optimizer_int8_sgd, 
            scheduler_int8_sgd, use_sam=False
        )
        
        if (epoch + 1) % 10 == 0 or epoch == Config.EPOCHS - 1:
            test_loss, test_acc = evaluate(model_int8_sgd, test_loader)
            print(f"  Epoch {epoch+1}/{Config.EPOCHS}: "
                  f"Train Loss={train_loss:.4f}, Train Acc={train_acc:.2f}%, "
                  f"Test Acc={test_acc:.2f}%")
    
    test_loss, test_acc = evaluate(model_int8_sgd, test_loader)
    print(f"\nFinal Int8 SGD Test Accuracy: {test_acc:.2f}%")
    
    results['int8_sgd'] = analyze_model(model_int8_sgd, analysis_loader, "Int8 SGD From Scratch")
    results['int8_sgd']['test_acc'] = test_acc
    
    del model_int8_sgd, optimizer_int8_sgd, scheduler_int8_sgd
    torch.cuda.empty_cache()
    gc.collect()
    
    # =====================================================
    # PHASE 3: INT8 SAM FROM SCRATCH
    # =====================================================
    print("\n" + "="*80)
    print("PHASE 3: INT8 (SAM) TRAINING FROM SCRATCH")
    print("="*80)
    
    model_int8_sam = resnet18(num_classes=10)
    model_int8_sam.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model_int8_sam.maxpool = nn.Identity()
    model_int8_sam.load_state_dict(initial_state)  # Same init!
    
    print("Applying 8-bit quantization...")
    model_int8_sam = replace_linear_layers(model_int8_sam, num_bits=8)
    model_int8_sam = model_int8_sam.to(Config.DEVICE)
    
    base_optimizer = optim.SGD
    optimizer_int8_sam = SAM(
        model_int8_sam.parameters(),
        base_optimizer,
        rho=Config.SAM_RHO,
        lr=Config.LR,
        momentum=Config.MOMENTUM,
        weight_decay=Config.WEIGHT_DECAY
    )
    scheduler_int8_sam = optim.lr_scheduler.MultiStepLR(
        optimizer_int8_sam.base_optimizer,
        milestones=Config.LR_MILESTONES,
        gamma=Config.LR_GAMMA
    )
    
    print("Training Int8 model (SAM)...")
    for epoch in range(Config.EPOCHS):
        train_loss, train_acc = train_epoch(
            model_int8_sam, train_loader, optimizer_int8_sam,
            scheduler_int8_sam, use_sam=True
        )
        
        if (epoch + 1) % 10 == 0 or epoch == Config.EPOCHS - 1:
            test_loss, test_acc = evaluate(model_int8_sam, test_loader)
            print(f"  Epoch {epoch+1}/{Config.EPOCHS}: "
                  f"Train Loss={train_loss:.4f}, Train Acc={train_acc:.2f}%, "
                  f"Test Acc={test_acc:.2f}%")
    
    test_loss, test_acc = evaluate(model_int8_sam, test_loader)
    print(f"\nFinal Int8 SAM Test Accuracy: {test_acc:.2f}%")
    
    results['int8_sam'] = analyze_model(model_int8_sam, analysis_loader, "Int8 SAM From Scratch")
    results['int8_sam']['test_acc'] = test_acc
    
    del model_int8_sam, optimizer_int8_sam, scheduler_int8_sam
    torch.cuda.empty_cache()
    gc.collect()
    
    # =====================================================
    # RESULTS & VISUALIZATION
    # =====================================================
    print("\n" + "="*80)
    print("EXPERIMENTAL RESULTS")
    print("="*80)
    
    print("\n📊 Test Accuracy:")
    print(f"  FP32:      {results['fp32']['test_acc']:.2f}%")
    print(f"  Int8 SGD:  {results['int8_sgd']['test_acc']:.2f}%")
    print(f"  Int8 SAM:  {results['int8_sam']['test_acc']:.2f}%")
    
    print("\n🔬 Sharpness (λ_max):")
    print(f"  FP32:      {results['fp32']['sharpness']:.4f}")
    print(f"  Int8 SGD:  {results['int8_sgd']['sharpness']:.4f}")
    print(f"  Int8 SAM:  {results['int8_sam']['sharpness']:.4f}")
    
    sgd_ratio = results['int8_sgd']['sharpness'] / results['fp32']['sharpness']
    sam_ratio = results['int8_sam']['sharpness'] / results['fp32']['sharpness']
    
    print(f"\n📈 Sharpness Ratios:")
    print(f"  Int8 SGD / FP32: {sgd_ratio:.2f}x")
    print(f"  Int8 SAM / FP32: {sam_ratio:.2f}x")
    
    # Hypothesis testing
    print("\n" + "="*80)
    print("HYPOTHESIS TESTING")
    print("="*80)
    
    print("\nH0: Quantization does NOT increase sharpness")
    print("H1: Quantization DOES increase sharpness (bit collapse)")
    
    if sgd_ratio > 1.2:
        print(f"\n✅ HYPOTHESIS CONFIRMED!")
        print(f"   Int8 SGD is {sgd_ratio:.2f}x sharper than FP32")
        print(f"   This demonstrates 'bit collapse' - quantization found a sharp minimum")
    else:
        print(f"\n❌ HYPOTHESIS REJECTED")
        print(f"   Int8 SGD sharpness ratio: {sgd_ratio:.2f}x (< 1.2x threshold)")
    
    if sam_ratio < sgd_ratio * 0.85:
        print(f"\n✅ SAM MITIGATION CONFIRMED!")
        print(f"   SAM reduced sharpness by {(1 - sam_ratio/sgd_ratio)*100:.1f}%")
    
    # Save results
    with open(f"{Config.SAVE_DIR}/results.txt", "w") as f:
        f.write("Controlled Bit Collapse Experiment\n")
        f.write("="*50 + "\n\n")
        f.write("Test Accuracy:\n")
        f.write(f"  FP32:      {results['fp32']['test_acc']:.2f}%\n")
        f.write(f"  Int8 SGD:  {results['int8_sgd']['test_acc']:.2f}%\n")
        f.write(f"  Int8 SAM:  {results['int8_sam']['test_acc']:.2f}%\n\n")
        f.write("Sharpness (λ_max):\n")
        f.write(f"  FP32:      {results['fp32']['sharpness']:.6f}\n")
        f.write(f"  Int8 SGD:  {results['int8_sgd']['sharpness']:.6f}\n")
        f.write(f"  Int8 SAM:  {results['int8_sam']['sharpness']:.6f}\n\n")
        f.write(f"Sharpness Ratios:\n")
        f.write(f"  SGD Ratio: {sgd_ratio:.4f}x\n")
        f.write(f"  SAM Ratio: {sam_ratio:.4f}x\n")
    
    # Visualization
    fig = plt.figure(figsize=(18, 6))
    
    # Plot 1: Loss Landscapes
    ax1 = plt.subplot(1, 3, 1)
    ax1.plot(results['fp32']['alphas'], results['fp32']['losses'],
             label='FP32', color='#2E86AB', linewidth=2.5, linestyle='--')
    ax1.plot(results['int8_sgd']['alphas'], results['int8_sgd']['losses'],
             label='Int8 SGD', color='#A23B72', linewidth=2.5)
    ax1.plot(results['int8_sam']['alphas'], results['int8_sam']['losses'],
             label='Int8 SAM', color='#06A77D', linewidth=2.5)
    ax1.axvline(x=0, color='black', linestyle='--', alpha=0.3)
    ax1.set_xlabel('α (Step Size)', fontsize=11)
    ax1.set_ylabel('Loss', fontsize=11)
    ax1.set_title('Loss Landscape', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Sharpness
    ax2 = plt.subplot(1, 3, 2)
    methods = ['FP32', 'Int8\nSGD', 'Int8\nSAM']
    sharpness_vals = [
        results['fp32']['sharpness'],
        results['int8_sgd']['sharpness'],
        results['int8_sam']['sharpness']
    ]
    colors = ['#2E86AB', '#A23B72', '#06A77D']
    bars = ax2.bar(methods, sharpness_vals, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax2.set_ylabel('Sharpness (λ_max)', fontsize=11)
    ax2.set_title('Hessian Eigenvalue', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, sharpness_vals):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 3: Test Accuracy
    ax3 = plt.subplot(1, 3, 3)
    acc_vals = [
        results['fp32']['test_acc'],
        results['int8_sgd']['test_acc'],
        results['int8_sam']['test_acc']
    ]
    bars = ax3.bar(methods, acc_vals, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax3.set_ylabel('Test Accuracy (%)', fontsize=11)
    ax3.set_title('Generalization', fontsize=12, fontweight='bold')
    ax3.set_ylim(min(acc_vals) - 5, 100)
    ax3.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, acc_vals):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    save_path = f"{Config.SAVE_DIR}/controlled_experiment.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualization saved to {save_path}")
    
    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE")
    print("="*80)


if __name__ == "__main__":
    run_controlled_experiment()
