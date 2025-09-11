# Modal Deployment Dependency Troubleshooting Guide

## Overview

This guide provides comprehensive strategies for resolving Python package dependency conflicts in Modal deployments, particularly for machine learning frameworks and complex dependency chains.

## Table of Contents

1. [Understanding Dependency Conflicts](#understanding-dependency-conflicts)
2. [Step-by-Step Resolution Strategies](#step-by-step-resolution-strategies)
3. [Identifying Compatible Package Versions](#identifying-compatible-package-versions)
4. [Handling Specific ML Framework Conflicts](#handling-specific-ml-framework-conflicts)
5. [Updating Legacy Image Builder Configurations](#updating-legacy-image-builder-configurations)
6. [Best Practices for Complex ML Dependencies](#best-practices-for-complex-ml-dependencies)
7. [Testing Package Compatibility](#testing-package-compatibility)
8. [Flexible Version Management](#flexible-version-management)
9. [Isolating and Resolving Conflicts](#isolating-and-resolving-conflicts)
10. [Maintaining Reproducible Builds](#maintaining-reproducible-builds)

## Understanding Dependency Conflicts

### Common Conflict Types

1. **Version Incompatibilities**: Different packages requiring conflicting versions of the same dependency
2. **Transitive Dependencies**: Indirect dependencies causing conflicts
3. **Platform-Specific Issues**: CUDA versions, architecture mismatches
4. **Build System Conflicts**: Different packages using incompatible build tools

### Warning Signs

```bash
# Common error patterns
ERROR: pip's dependency resolver does not currently consider all the packages
ERROR: Cannot install package-a and package-b because these package versions have conflicting dependencies
ModuleNotFoundError: No module named 'package_name'
ImportError: cannot import name 'function_name' from 'module'
```

## Step-by-Step Resolution Strategies

### 1. Dependency Analysis Workflow

```python
# Create a dependency analysis script
import subprocess
import json

def analyze_dependencies(packages):
    """Analyze package dependencies and conflicts"""
    conflicts = []

    for package in packages:
        try:
            result = subprocess.run(
                ["pip", "show", package],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ {package}: {result.stdout}")
            else:
                conflicts.append(package)
        except Exception as e:
            conflicts.append((package, str(e)))

    return conflicts

# Usage
packages = ["vllm", "torch", "flashinfer-python", "huggingface_hub"]
conflicts = analyze_dependencies(packages)
```

### 2. Systematic Resolution Process

1. **Isolate the Problem**

   ```bash
   # Test packages individually
   modal run test_package.py::test_vllm_only
   modal run test_package.py::test_torch_only
   modal run test_package.py::test_combined
   ```

2. **Check Version Compatibility Matrix**

   ```python
   # Create compatibility matrix
   COMPATIBILITY_MATRIX = {
       "vllm": {
           "0.10.1.1": {
               "torch": ["2.7.1", "2.6.0"],
               "flashinfer-python": ["0.2.8"],
               "python": ["3.10", "3.11", "3.12"]
           }
       },
       "torch": {
           "2.7.1": {
               "python": ["3.10", "3.11", "3.12"],
               "cuda": ["12.1", "12.4", "12.8"]
           }
       }
   }
   ```

3. **Progressive Installation Strategy**
   ```python
   # Install packages in dependency order
   vllm_image = (
       modal.Image.from_registry("nvidia/cuda:12.8.0-devel-ubuntu22.04", add_python="3.12")
       # Step 1: Core dependencies first
       .pip_install("torch==2.7.1")
       # Step 2: Framework-specific packages
       .pip_install("flashinfer-python==0.2.8")
       # Step 3: High-level packages
       .pip_install("vllm==0.10.1.1")
       # Step 4: Additional tools
       .pip_install("huggingface_hub[hf_transfer]==0.34.4")
   )
   ```

## Identifying Compatible Package Versions

### 1. Automated Version Discovery

```python
import requests
import json
from packaging import version

def find_compatible_versions(package_name, python_version="3.12"):
    """Find compatible package versions"""

    # Query PyPI API
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    data = response.json()

    compatible_versions = []
    for version_str, details in data["releases"].items():
        for file_info in details:
            if file_info.get("python_version") == python_version:
                compatible_versions.append(version_str)

    return sorted(compatible_versions, key=version.parse, reverse=True)

# Usage
torch_versions = find_compatible_versions("torch")
vllm_versions = find_compatible_versions("vllm")
```

### 2. Dependency Tree Analysis

```python
def analyze_dependency_tree(package_name):
    """Analyze package dependency tree"""
    import pkg_resources

    try:
        dist = pkg_resources.get_distribution(package_name)
        dependencies = [str(req) for req in dist.requires()]

        tree = {
            "package": package_name,
            "version": dist.version,
            "dependencies": dependencies,
            "conflicts": []
        }

        return tree
    except pkg_resources.DistributionNotFound:
        return {"error": f"Package {package_name} not found"}

# Create dependency map
packages = ["vllm", "torch", "flashinfer-python"]
dependency_map = {pkg: analyze_dependency_tree(pkg) for pkg in packages}
```

### 3. Version Constraint Generator

```python
def generate_version_constraints(packages, compatibility_matrix):
    """Generate optimal version constraints"""

    constraints = {}

    for package, versions in packages.items():
        # Find intersection of compatible versions
        compatible = set(versions)

        for other_package, other_versions in packages.items():
            if package != other_package:
                # Check compatibility matrix
                if package in compatibility_matrix:
                    compatible &= set(compatibility_matrix[package].get(other_package, []))

        if compatible:
            # Use most recent compatible version
            constraints[package] = max(compatible, key=version.parse)
        else:
            constraints[package] = "CONFLICT_DETECTED"

    return constraints
```

## Handling Specific ML Framework Conflicts

### 1. PyTorch + CUDA Compatibility

```python
# CUDA-aware PyTorch installation
def get_cuda_compatible_torch():
    """Get CUDA-compatible PyTorch version"""

    cuda_versions = {
        "12.8": "torch==2.7.1+cu128",
        "12.4": "torch==2.6.0+cu124",
        "11.8": "torch==2.5.0+cu118"
    }

    return cuda_versions

# Modal image with CUDA-specific PyTorch
vllm_image = (
    modal.Image.from_registry("nvidia/cuda:12.8.0-devel-ubuntu22.04", add_python="3.12")
    .pip_install(
        "--index-url", "https://download.pytorch.org/whl/cu128",
        "torch==2.7.1+cu128"
    )
    .pip_install("vllm==0.10.1.1")
)
```

### 2. VLLM + FlashInfer Compatibility

```python
# Specific compatibility handling for VLLM and FlashInfer
VLLM_FLASHINFER_MATRIX = {
    "vllm==0.10.1.1": "flashinfer-python==0.2.8",
    "vllm==0.9.0": "flashinfer-python==0.2.6",
    "vllm==0.8.0": "flashinfer-python==0.2.4"
}

def get_compatible_flashinfer(vllm_version):
    """Get compatible FlashInfer version for VLLM"""
    return VLLM_FLASHINFER_MATRIX.get(vllm_version, "flashinfer-python>=0.2.8")
```

### 3. Hugging Face Hub Compatibility

```python
# Handle HF Hub with different extras
def install_hf_hub_compatible(torch_version):
    """Install HF Hub with appropriate extras"""

    if version.parse(torch_version) >= version.parse("2.0.0"):
        return "huggingface_hub[hf_transfer]==0.34.4"
    else:
        return "huggingface_hub==0.34.4"  # Without hf_transfer for older torch
```

## Updating Legacy Image Builder Configurations

### 1. Migration from Old to New API

```python
# OLD API (deprecated)
old_image = (
    modal.Image.debian_slim()
    .apt_install("git")
    .uv_pip_install("torch")  # ❌ uv_pip_install doesn't exist
    .run_commands("pip install special-package")
)

# NEW API (current)
new_image = (
    modal.Image.debian_slim()
    .apt_install("git")
    .pip_install("torch")  # ✅ Use pip_install
    .run_commands("pip install special-package")
)
```

### 2. Base Image Selection Strategy

```python
def select_optimal_base_image(requirements):
    """Select optimal base image based on requirements"""

    base_images = {
        "cuda_ml": "nvidia/cuda:12.8.0-devel-ubuntu22.04",
        "cpu_ml": "python:3.12-slim",
        "minimal": "alpine:latest"
    }

    if "gpu" in requirements or "cuda" in requirements:
        return base_images["cuda_ml"]
    elif any(ml_lib in requirements for ml_lib in ["torch", "tensorflow", "jax"]):
        return base_images["cpu_ml"]
    else:
        return base_images["minimal"]

# Usage
requirements = ["torch", "vllm", "gpu"]
base_image = select_optimal_base_image(requirements)
```

### 3. Multi-Stage Build Pattern

```python
# Multi-stage build for complex dependencies
def create_multi_stage_image():
    """Create image using multi-stage build pattern"""

    # Stage 1: Build dependencies
    build_image = (
        modal.Image.from_registry("nvidia/cuda:12.8.0-devel-ubuntu22.04")
        .apt_install("build-essential", "cmake", "git")
        .pip_install("wheel", "setuptools")
    )

    # Stage 2: Install core ML packages
    ml_image = (
        build_image
        .pip_install("torch==2.7.1")
        .pip_install("flashinfer-python==0.2.8")
    )

    # Stage 3: Install application packages
    final_image = (
        ml_image
        .pip_install("vllm==0.10.1.1")
        .pip_install("huggingface_hub[hf_transfer]==0.34.4")
    )

    return final_image
```

## Best Practices for Complex ML Dependencies

### 1. Dependency Layering Strategy

```python
class DependencyLayer:
    """Manage dependencies in layers"""

    def __init__(self):
        self.layers = {
            "system": [],      # System packages
            "core": [],        # Core ML frameworks
            "extensions": [],  # Framework extensions
            "application": []  # Application-specific
        }

    def add_dependency(self, layer, package, version=None):
        """Add dependency to specific layer"""
        if version:
            self.layers[layer].append(f"{package}=={version}")
        else:
            self.layers[layer].append(package)

    def build_image(self, base_image):
        """Build image with layered dependencies"""
        image = base_image

        for layer_name, packages in self.layers.items():
            if packages:
                print(f"Installing {layer_name} layer: {packages}")
                image = image.pip_install(*packages)

        return image

# Usage
deps = DependencyLayer()
deps.add_dependency("core", "torch", "2.7.1")
deps.add_dependency("extensions", "flashinfer-python", "0.2.8")
deps.add_dependency("application", "vllm", "0.10.1.1")

base = modal.Image.from_registry("nvidia/cuda:12.8.0-devel-ubuntu22.04", add_python="3.12")
final_image = deps.build_image(base)
```

### 2. Environment Variables for Flexibility

```python
# Use environment variables for version management
def create_configurable_image():
    """Create image with configurable versions"""

    versions = {
        "TORCH_VERSION": "2.7.1",
        "VLLM_VERSION": "0.10.1.1",
        "FLASHINFER_VERSION": "0.2.8",
        "PYTHON_VERSION": "3.12"
    }

    image = (
        modal.Image.from_registry(
            f"nvidia/cuda:12.8.0-devel-ubuntu22.04",
            add_python=versions["PYTHON_VERSION"]
        )
        .env(versions)  # Pass versions as env vars
        .pip_install(f"torch=={versions['TORCH_VERSION']}")
        .pip_install(f"flashinfer-python=={versions['FLASHINFER_VERSION']}")
        .pip_install(f"vllm=={versions['VLLM_VERSION']}")
    )

    return image
```

### 3. Conditional Installation Logic

```python
def conditional_install_image():
    """Install packages conditionally based on requirements"""

    image = modal.Image.from_registry("nvidia/cuda:12.8.0-devel-ubuntu22.04", add_python="3.12")

    # Install core packages
    image = image.pip_install("torch==2.7.1")

    # Conditional installations
    if os.getenv("ENABLE_FLASHINFER", "true").lower() == "true":
        image = image.pip_install("flashinfer-python==0.2.8")

    if os.getenv("ENABLE_QUANTIZATION", "false").lower() == "true":
        image = image.pip_install("bitsandbytes", "auto-gptq")

    # Always install VLLM last
    image = image.pip_install("vllm==0.10.1.1")

    return image
```

## Testing Package Compatibility

### 1. Automated Compatibility Testing

```python
# test_compatibility.py
import modal
import subprocess
import sys

def test_package_imports():
    """Test that all packages can be imported successfully"""

    packages_to_test = [
        "torch",
        "vllm",
        "flashinfer",
        "huggingface_hub"
    ]

    results = {}

    for package in packages_to_test:
        try:
            __import__(package)
            results[package] = "✅ SUCCESS"
        except ImportError as e:
            results[package] = f"❌ FAILED: {e}"
        except Exception as e:
            results[package] = f"⚠️  WARNING: {e}"

    return results

def test_functionality():
    """Test basic functionality of packages"""

    tests = {}

    # Test PyTorch
    try:
        import torch
        x = torch.randn(2, 3)
        tests["torch_basic"] = "✅ PyTorch basic operations work"

        if torch.cuda.is_available():
            tests["torch_cuda"] = f"✅ CUDA available: {torch.cuda.get_device_name()}"
        else:
            tests["torch_cuda"] = "⚠️  CUDA not available"
    except Exception as e:
        tests["torch"] = f"❌ PyTorch test failed: {e}"

    # Test VLLM
    try:
        from vllm import LLM
        tests["vllm_import"] = "✅ VLLM import successful"
    except Exception as e:
        tests["vllm"] = f"❌ VLLM test failed: {e}"

    return tests

# Modal test function
app = modal.App("dependency-test")

@app.function(image=your_test_image)
def run_compatibility_tests():
    """Run compatibility tests in Modal environment"""

    import_results = test_package_imports()
    functionality_results = test_functionality()

    print("=== Import Tests ===")
    for package, result in import_results.items():
        print(f"{package}: {result}")

    print("\n=== Functionality Tests ===")
    for test, result in functionality_results.items():
        print(f"{test}: {result}")

    return {
        "imports": import_results,
        "functionality": functionality_results
    }
```

### 2. Version Validation Script

```python
# validate_versions.py
def validate_package_versions():
    """Validate that installed package versions match requirements"""

    import pkg_resources

    required_versions = {
        "torch": "2.7.1",
        "vllm": "0.10.1.1",
        "flashinfer-python": "0.2.8",
        "huggingface-hub": "0.34.4"
    }

    validation_results = {}

    for package, expected_version in required_versions.items():
        try:
            installed_version = pkg_resources.get_distribution(package).version
            if installed_version == expected_version:
                validation_results[package] = f"✅ {installed_version} (matches expected)"
            else:
                validation_results[package] = f"⚠️  {installed_version} (expected {expected_version})"
        except pkg_resources.DistributionNotFound:
            validation_results[package] = f"❌ Not installed (expected {expected_version})"

    return validation_results

@app.function(image=your_image)
def validate_deployment():
    """Validate package versions in deployment environment"""
    return validate_package_versions()
```

### 3. Performance Benchmarking

```python
# benchmark_performance.py
import time
import torch

def benchmark_torch_operations():
    """Benchmark PyTorch operations to ensure performance"""

    # CPU benchmark
    start_time = time.time()
    x = torch.randn(1000, 1000)
    y = torch.randn(1000, 1000)
    z = torch.mm(x, y)
    cpu_time = time.time() - start_time

    results = {"cpu_matmul_1000x1000": f"{cpu_time:.4f}s"}

    # GPU benchmark (if available)
    if torch.cuda.is_available():
        device = torch.device("cuda")
        x_gpu = x.to(device)
        y_gpu = y.to(device)

        # Warm up
        torch.mm(x_gpu, y_gpu)
        torch.cuda.synchronize()

        start_time = time.time()
        z_gpu = torch.mm(x_gpu, y_gpu)
        torch.cuda.synchronize()
        gpu_time = time.time() - start_time

        results["gpu_matmul_1000x1000"] = f"{gpu_time:.4f}s"
        results["speedup"] = f"{cpu_time/gpu_time:.2f}x"

    return results

@app.function(image=your_image, gpu="T4")
def run_performance_benchmark():
    """Run performance benchmarks"""
    return benchmark_torch_operations()
```

## Flexible Version Management

### 1. Version Range Strategies

```python
# version_ranges.py
from packaging import version, specifiers

class VersionManager:
    """Manage flexible version ranges"""

    def __init__(self):
        self.version_specs = {}

    def add_constraint(self, package, constraint):
        """Add version constraint for package"""
        self.version_specs[package] = specifiers.SpecifierSet(constraint)

    def is_compatible(self, package, version_str):
        """Check if version is compatible with constraints"""
        if package not in self.version_specs:
            return True

        return version.parse(version_str) in self.version_specs[package]

    def find_best_version(self, package, available_versions):
        """Find best compatible version"""
        compatible_versions = [
            v for v in available_versions
            if self.is_compatible(package, v)
        ]

        if not compatible_versions:
            return None

        return max(compatible_versions, key=version.parse)

# Usage example
vm = VersionManager()
vm.add_constraint("torch", ">=2.0.0,<3.0.0")
vm.add_constraint("vllm", ">=0.8.0,<=0.10.1.1")

# Check compatibility
torch_versions = ["1.13.0", "2.0.0", "2.7.1", "3.0.0"]
best_torch = vm.find_best_version("torch", torch_versions)
print(f"Best torch version: {best_torch}")
```

### 2. Lock File Generation

```python
# generate_lock_file.py
import json
import pkg_resources
from datetime import datetime

def generate_dependency_lock():
    """Generate dependency lock file"""

    installed_packages = {}

    for dist in pkg_resources.working_set:
        package_info = {
            "version": dist.version,
            "location": dist.location,
            "dependencies": [str(req) for req in dist.requires()],
            "extras": list(dist.extras)
        }
        installed_packages[dist.project_name] = package_info

    lock_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "python_version": sys.version,
        "packages": installed_packages
    }

    return lock_data

def save_lock_file(lock_data, filename="modal-dependencies.lock"):
    """Save lock file"""
    with open(filename, 'w') as f:
        json.dump(lock_data, f, indent=2, sort_keys=True)

@app.function(image=your_image)
def create_deployment_lock():
    """Create lock file for current deployment"""
    lock_data = generate_dependency_lock()
    save_lock_file(lock_data)
    return lock_data
```

### 3. Environment-Specific Configurations

```python
# environment_configs.py
import os
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"

class EnvironmentConfig:
    """Environment-specific dependency configurations"""

    CONFIGS = {
        Environment.DEVELOPMENT: {
            "torch": ">=2.6.0",
            "vllm": ">=0.9.0",
            "flashinfer-python": ">=0.2.6",
            "debug_packages": ["pytest", "debugpy"]
        },
        Environment.STAGING: {
            "torch": "2.7.1",
            "vllm": "0.10.1.1",
            "flashinfer-python": "0.2.8",
            "debug_packages": []
        },
        Environment.PRODUCTION: {
            "torch": "2.7.1",
            "vllm": "0.10.1.1",
            "flashinfer-python": "0.2.8",
            "debug_packages": []
        }
    }

    @classmethod
    def get_config(cls, env: Environment):
        """Get configuration for environment"""
        return cls.CONFIGS.get(env, cls.CONFIGS[Environment.PRODUCTION])

    @classmethod
    def build_image_for_env(cls, env: Environment):
        """Build image for specific environment"""
        config = cls.get_config(env)

        image = modal.Image.from_registry("nvidia/cuda:12.8.0-devel-ubuntu22.04", add_python="3.12")

        # Install core packages
        for package, version_spec in config.items():
            if package != "debug_packages":
                if ">=" in version_spec or "==" in version_spec:
                    image = image.pip_install(f"{package}{version_spec}")
                else:
                    image = image.pip_install(f"{package}=={version_spec}")

        # Install debug packages for non-production
        if env != Environment.PRODUCTION and config.get("debug_packages"):
            image = image.pip_install(*config["debug_packages"])

        return image

# Usage
env = Environment.PRODUCTION if os.getenv("MODAL_ENV") == "prod" else Environment.DEVELOPMENT
production_image = EnvironmentConfig.build_image_for_env(env)
```

## Isolating and Resolving Conflicts

### 1. Binary Search for Conflicts

```python
# conflict_isolation.py
def binary_search_conflict(packages):
    """Use binary search to isolate conflicting packages"""

    def test_package_subset(package_subset):
        """Test if a subset of packages can be installed together"""
        try:
            test_image = (
                modal.Image.from_registry("nvidia/cuda:12.8.0-devel-ubuntu22.04", add_python="3.12")
                .pip_install(*package_subset)
            )
            # Try to build the image
            return True, None
        except Exception as e:
            return False, str(e)

    # Binary search implementation
    def find_conflict(package_list, left=0, right=None):
        if right is None:
            right = len(package_list)

        if right - left <= 1:
            return package_list[left:right]

        mid = (left + right) // 2
        left_subset = package_list[left:mid]
        right_subset = package_list[mid:right]

        left_works, left_error = test_package_subset(left_subset)
        right_works, right_error = test_package_subset(right_subset)

        if not left_works:
            return find_conflict(package_list, left, mid)
        elif not right_works:
            return find_conflict(package_list, mid, right)
        else:
            # Conflict is between the two subsets
            combined_works, combined_error = test_package_subset(left_subset + right_subset)
            if not combined_works:
                return {"left": left_subset, "right": right_subset, "error": combined_error}
            else:
                return None

    return find_conflict(packages)

# Usage
problematic_packages = [
    "torch==2.7.1",
    "vllm==0.10.1.1",
    "flashinfer-python==0.2.8",
    "huggingface_hub[hf_transfer]==0.34.4"
]

conflict_result = binary_search_conflict(problematic_packages)
print(f"Conflict detected: {conflict_result}")
```

### 2. Dependency Graph Analysis

```python
# dependency_graph.py
import networkx as nx
import matplotlib.pyplot as plt

class DependencyGraph:
    """Analyze package dependencies as a graph"""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_package(self, package, dependencies):
        """Add package and its dependencies to graph"""
        self.graph.add_node(package)
        for dep in dependencies:
            self.graph.add_edge(package, dep)

    def find_cycles(self):
        """Find circular dependencies"""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except nx.NetworkXNoCycle:
            return []

    def find_conflicts(self, version_constraints):
        """Find version conflicts in dependency graph"""
        conflicts = []

        for node in self.graph.nodes():
            # Get all paths to this node
            predecessors = list(self.graph.predecessors(node))

            if len(predecessors) > 1:
                # Multiple packages depend on this - check version conflicts
                required_versions = []
                for pred in predecessors:
                    if pred in version_constraints:
                        required_versions.append(version_constraints[pred].get(node))

                # Check if versions are compatible
                unique_versions = set(filter(None, required_versions))
                if len(unique_versions) > 1:
                    conflicts.append({
                        "package": node,
                        "conflicting_requirements": dict(zip(predecessors, required_versions))
                    })

        return conflicts

    def visualize(self, filename="dependency_graph.png"):
        """Visualize dependency graph"""
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue',
                node_size=500, arrowsize=20)
        plt.title("Package Dependency Graph")
        plt.savefig(filename)
        plt.close()

# Usage
dg = DependencyGraph()
dg.add_package("vllm", ["torch", "flashinfer-python"])
dg.add_package("torch", ["numpy"])
dg.add_package("flashinfer-python", ["torch"])

cycles = dg.find_cycles()
print(f"Circular dependencies: {cycles}")
```

### 3. Progressive Installation Testing

```python
# progressive_testing.py
def progressive_install_test(packages):
    """Test packages by installing them progressively"""

    results = []
    successful_packages = []

    for i, package in enumerate(packages):
        test_packages = successful_packages + [package]

        try:
            # Test installation
            test_image = (
                modal.Image.from_registry("nvidia/cuda:12.8.0-devel-ubuntu22.04", add_python="3.12")
                .pip_install(*test_packages)
            )

            # If successful, add to successful list
            successful_packages.append(package)
            results.append({
                "step": i + 1,
                "package": package,
                "status": "✅ SUCCESS",
                "cumulative": test_packages.copy()
            })

        except Exception as e:
            results.append({
                "step": i + 1,
                "package": package,
                "status": f"❌ FAILED: {str(e)}",
                "cumulative": test_packages.copy()
            })

            # Try to find alternative version
            alternative = find_alternative_version(package, successful_packages)
            if alternative:
                successful_packages.append(alternative)
                results.append({
                    "step": i + 1,
                    "package": alternative,
                    "status": f"✅ SUCCESS (alternative)",
                    "cumulative": successful_packages.copy()
                })

    return results

def find_alternative_version(package, existing_packages):
    """Find alternative version that's compatible with existing packages"""
    # Implementation would query PyPI for compatible versions
    # This is a simplified version
    package_name = package.split("==")[0]

    alternative_versions = {
        "vllm": ["0.10.1", "0.10.0", "0.9.0"],
        "torch": ["2.6.0", "2.5.0", "2.4.0"],
        "flashinfer-python": ["0.2.7", "0.2.6", "0.2.5"]
    }

    if package_name in alternative_versions:
        for version in alternative_versions[package_name]:
            candidate = f"{package_name}=={version}"
            # Test compatibility (simplified)
            return candidate

    return None
```

## Maintaining Reproducible Builds

### 1. Deterministic Image Building

```python
# reproducible_builds.py
import hashlib
import json
from datetime import datetime

class ReproducibleImageBuilder:
    """Build deterministic, reproducible Modal images"""

    def __init__(self):
        self.build_spec = {
            "base_image": None,
            "python_version": None,
            "packages": [],
            "environment_vars": {},
            "build_args": {},
            "timestamp": None
        }

    def set_base_image(self, image, python_version):
        """Set base image configuration"""
        self.build_spec["base_image"] = image
        self.build_spec["python_version"] = python_version
        return self

    def add_package(self, package, version=None, extras=None):
        """Add package with specific version"""
        package_spec = {"name": package}

        if version:
            package_spec["version"] = version
        if extras:
            package_spec["extras"] = extras

        self.build_spec["packages"].append(package_spec)
        return self

    def set_env_var(self, key, value):
        """Set environment variable"""
        self.build_spec["environment_vars"][key] = value
        return self

    def generate_hash(self):
        """Generate deterministic hash of build specification"""
        # Create deterministic representation
        spec_copy = self.build_spec.copy()
        spec_copy.pop("timestamp", None)  # Remove timestamp for deterministic hash

        spec_str = json.dumps(spec_copy, sort_keys=True)
        return hashlib.sha256(spec_str.encode()).hexdigest()[:16]

    def build(self):
        """Build image with reproducible configuration"""

        # Set timestamp
        self.build_spec["timestamp"] = datetime.utcnow().isoformat()

        # Start with base image
        image = modal.Image.from_registry(
            self.build_spec["base_image"],
            add_python=self.build_spec["python_version"]
        )

        # Add environment variables
        if self.build_spec["environment_vars"]:
            image = image.env(self.build_spec["environment_vars"])

        # Install packages in deterministic order
        sorted_packages = sorted(self.build_spec["packages"], key=lambda x: x["name"])

        for package_spec in sorted_packages:
            package_str = package_spec["name"]

            if "version" in package_spec:
                package_str += f"=={package_spec['version']}"

            if "extras" in package_spec:
                extras_str = ",".join(package_spec["extras"])
                package_str += f"[{extras_str}]"

            image = image.pip_install(package_str)

        # Add build metadata
        build_hash = self.generate_hash()
        image = image.env({"BUILD_HASH": build_hash})

        return image

    def save_build_spec(self, filename=None):
        """Save build specification for reproducibility"""
        if filename is None:
            build_hash = self.generate_hash()
            filename = f"build-spec-{build_hash}.json"

        with open(filename, 'w') as f:
            json.dump(self.build_spec, f, indent=2, sort_keys=True)

        return filename

# Usage
builder = ReproducibleImageBuilder()
image = (
    builder
    .set_base_image("nvidia/cuda:12.8.0-devel-ubuntu22.04", "3.12")
    .add_package("torch", "2.7.1")
    .add_package("flashinfer-python", "0.2.8")
    .add_package("vllm", "0.10.1.1")
    .add_package("huggingface_hub", "0.34.4", ["hf_transfer"])
    .set_env_var("HF_HUB_ENABLE_HF_TRANSFER", "1")
    .build()
)

# Save build specification
spec_file = builder.save_build_spec()
print(f"Build specification saved to: {spec_file}")
```

### 2. Version Pinning Strategy

```python
# version_pinning.py
class VersionPinner:
    """Manage version pinning for reproducible builds"""

    def __init__(self):
        self.pins = {}
        self.constraints = {}

    def pin_version(self, package, version, reason=""):
        """Pin specific version of package"""
        self.pins[package] = {
            "version": version,
            "reason": reason,
            "pinned_at": datetime.utcnow().isoformat()
        }

    def add_constraint(self, package, constraint, reason=""):
        """Add version constraint"""
        self.constraints[package] = {
            "constraint": constraint,
            "reason": reason
        }

    def generate_requirements(self):
        """Generate requirements.txt content"""
        lines = ["# Auto-generated requirements file"]
        lines.append(f"# Generated at: {datetime.utcnow().isoformat()}")
        lines.append("")

        # Add pinned versions
        if self.pins:
            lines.append("# Pinned versions")
            for package, info in sorted(self.pins.items()):
                comment = f"  # {info['reason']}" if info['reason'] else ""
                lines.append(f"{package}=={info['version']}{comment}")
            lines.append("")

        # Add constraints
        if self.constraints:
            lines.append("# Version constraints")
            for package, info in sorted(self.constraints.items()):
                comment = f"  # {info['reason']}" if info['reason'] else ""
                lines.append(f"{package}{info['constraint']}{comment}")

        return "\n".join(lines)

    def validate_pins(self):
        """Validate that pinned versions are compatible"""
        # Implementation would check compatibility
        pass

# Usage
pinner = VersionPinner()
pinner.pin_version("torch", "2.7.1", "Known stable version with CUDA 12.8")
pinner.pin_version("vllm", "0.10.1.1", "Latest stable release")
pinner.pin_version("flashinfer-python", "0.2.8", "Compatible with VLLM 0.10.1.1")
pinner.add_constraint("huggingface_hub", ">=0.34.0,<0.35.0", "API compatibility")

requirements_content = pinner.generate_requirements()
print(requirements_content)
```

### 3. Build Caching and Invalidation

```python
# build_caching.py
import pickle
import os
from pathlib import Path

class BuildCache:
    """Cache build results for faster iterations"""

    def __init__(self, cache_dir=".modal_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def get_cache_key(self, build_spec):
        """Generate cache key from build specification"""
        spec_str = json.dumps(build_spec, sort_keys=True)
        return hashlib.sha256(spec_str.encode()).hexdigest()

    def is_cached(self, build_spec):
        """Check if build is cached"""
        cache_key = self.get_cache_key(build_spec)
        cache_file = self.cache_dir / f"{cache_key}.cache"
        return cache_file.exists()

    def get_cached_image(self, build_spec):
        """Get cached image if available"""
        if not self.is_cached(build_spec):
            return None

        cache_key = self.get_cache_key(build_spec)
        cache_file = self.cache_dir / f"{cache_key}.cache"

        with open(cache_file, 'rb') as f:
            cached_data = pickle.load(f)

        return cached_data.get("image_id")

    def cache_image(self, build_spec, image_id):
        """Cache built image"""
        cache_key = self.get_cache_key(build_spec)
        cache_file = self.cache_dir / f"{cache_key}.cache"

        cache_data = {
            "image_id": image_id,
            "build_spec": build_spec,
            "cached_at": datetime.utcnow().isoformat()
        }

        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)

    def invalidate_cache(self, pattern=None):
        """Invalidate cache entries"""
        if pattern:
            for cache_file in self.cache_dir.glob(f"*{pattern}*.cache"):
                cache_file.unlink()
        else:
            # Clear all cache
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()

# Usage with ReproducibleImageBuilder
class CachedImageBuilder(ReproducibleImageBuilder):
    """Image builder with caching support"""

    def __init__(self, cache_dir=".modal_cache"):
        super().__init__()
        self.cache = BuildCache(cache_dir)

    def build(self, use_cache=True):
        """Build image with caching support"""

        if use_cache:
            cached_image_id = self.cache.get_cached_image(self.build_spec)
            if cached_image_id:
                print(f"Using cached image: {cached_image_id}")
                return cached_image_id

        # Build new image
        image = super().build()

        # Cache the result
        image_id = str(hash(str(image)))  # Simplified image ID
        self.cache.cache_image(self.build_spec, image_id)

        return image
```

## Conclusion

This comprehensive guide provides strategies for managing complex dependency conflicts in Modal deployments. Key takeaways:

1. **Systematic Approach**: Use structured methods to identify and resolve conflicts
2. **Version Management**: Implement flexible version constraints while maintaining stability
3. **Testing Strategy**: Validate compatibility before deployment
4. **Reproducibility**: Ensure consistent builds across environments
5. **Monitoring**: Continuously monitor and update dependencies

For ongoing maintenance:

- Regularly update dependency matrices
- Monitor package release notes for breaking changes
- Implement automated testing for dependency updates
- Maintain detailed logs of resolution strategies that work

This guide should be updated as Modal's API evolves and new ML frameworks emerge.
