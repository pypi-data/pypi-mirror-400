# Cardiac Shared

[![PyPI version](https://badge.fury.io/py/cardiac-shared.svg)](https://pypi.org/project/cardiac-shared/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Shared utilities for cardiac imaging analysis projects.

**Version**: 0.5.1 | **PyPI**: https://pypi.org/project/cardiac-shared/

## Installation

```bash
# Install from PyPI (recommended)
pip install cardiac-shared

# Install with optional dependencies
pip install cardiac-shared[all]      # All optional deps
pip install cardiac-shared[dicom]    # DICOM support
pip install cardiac-shared[nifti]    # NIfTI support
pip install cardiac-shared[gpu]      # GPU/PyTorch support
```

## Modules

### IO Module

| Function | Description |
|----------|-------------|
| `read_dicom_series(path)` | Read DICOM series from directory |
| `get_dicom_metadata(ds)` | Extract metadata from DICOM dataset |
| `load_nifti(path)` | Load NIfTI file with metadata |
| `save_nifti(volume, path)` | Save numpy array as NIfTI |
| `extract_zip(path)` | Context manager for ZIP extraction |
| `find_dicom_root(path)` | Find DICOM directory in extracted ZIP |
| `AsyncNiftiPreloader` | Background NIfTI preloading (v0.5.1) |
| `preload_nifti_batch()` | Batch preloading convenience function (v0.5.1) |

### Hardware Module

| Function | Description |
|----------|-------------|
| `detect_hardware()` | Detect complete hardware info (GPU/CPU/RAM) |
| `HardwareInfo` | Dataclass with GPU, CPU, RAM, environment info |
| `print_hardware_summary(hw)` | Print formatted hardware summary |
| `get_optimal_config(hw)` | Get optimal inference configuration |
| `CPUOptimizer` | CPU optimization for hospital deployments |
| `get_recommended_gpu_stabilization_time()` | Dynamic GPU wait time (v0.5.1) |
| `get_gpu_performance_tier()` | GPU tier classification (v0.5.1) |

### Environment Module

| Function | Description |
|----------|-------------|
| `detect_runtime()` | Detect runtime environment |
| `RuntimeEnvironment` | Dataclass with environment info |
| `detect_colab()` | Check if running in Google Colab |
| `detect_wsl()` | Check if running in WSL |

### Parallel Module (v0.3.0)

| Class/Function | Description |
|----------------|-------------|
| `ParallelProcessor` | Unified parallel processing framework |
| `parallel_map()` | Quick parallel map without checkpoint |
| `parallel_map_with_checkpoint()` | Parallel map with resume support |
| `ProcessingResult` | Result dataclass for each processed item |
| `Checkpoint` | Checkpoint data for resume capability |

### Progress Module (v0.3.0)

| Class/Function | Description |
|----------------|-------------|
| `ProgressTracker` | Multi-level progress visualization |
| `create_tracker()` | Create and start a progress tracker |
| `ProgressLevel` | Progress tracking for a single level |

### Cache Module (v0.3.0)

| Class | Description |
|-------|-------------|
| `CacheManager` | Multi-level caching with resume capability |

### Batch Module (v0.3.0)

| Class | Description |
|-------|-------------|
| `BatchProcessor` | Generic batch processing framework |
| `BatchConfig` | Batch processing configuration |

### Config Module (v0.3.0)

| Class/Function | Description |
|----------------|-------------|
| `ConfigManager` | YAML/JSON configuration management |
| `load_config()` | Load configuration with defaults |

### Data Module (v0.4.0)

| Class/Function | Description |
|----------------|-------------|
| `IntermediateResultsRegistry` | Cross-project data discovery and sharing |
| `RegistryEntry` | Dataclass for registry entries |
| `get_registry()` | Get singleton registry instance |

### Data Sources Module (v0.5.0)

| Class/Function | Description |
|----------------|-------------|
| `DataSourceManager` | Multi-source data management (ZAL/CHD/Normal/Custom) |
| `DataSource` | Configuration for a single data source |
| `DataSourceStatus` | Status check result for a data source |
| `get_source()` | Get data source from default manager |
| `list_sources()` | List all configured data sources |

### Vertebra Module (v0.5.0)

| Class/Function | Description |
|----------------|-------------|
| `VertebraDetector` | Detect and analyze vertebrae from TotalSegmentator output |
| `VertebraInfo` | Vertebra metadata (center slice, volume, etc.) |
| `VertebraROI` | Region of interest around a vertebra |
| `parse_vertebrae()` | Parse vertebra names from labels directory |
| `sort_vertebrae()` | Sort vertebrae cranial to caudal |

### Tissue Module (v0.5.0)

| Class/Function | Description |
|----------------|-------------|
| `TissueClassifier` | Tissue-specific HU filtering (Alberta Protocol 2024) |
| `TissueMetrics` | Metrics for a tissue type (area, HU, quality) |
| `FilterStats` | Statistics from HU filtering |
| `filter_tissue()` | Filter tissue mask by HU range |
| `get_tissue_hu_range()` | Get HU range for tissue type |
| `TISSUE_HU_RANGES` | Standard HU ranges for all tissue types |

## Usage Examples

### Hardware Detection

```python
from cardiac_shared import detect_hardware, detect_runtime

hw = detect_hardware()
print(f"GPU: {hw.gpu.device_name if hw.gpu.available else 'None'}")
print(f"CPU Cores: {hw.cpu.physical_cores}")
print(f"RAM: {hw.ram.total_gb:.1f} GB")

env = detect_runtime()
print(f"Runtime: {env.runtime_type}")  # wsl, linux, windows, colab
```

### Parallel Processing with Checkpoint

```python
from cardiac_shared.parallel import ParallelProcessor

def process_patient(patient_id):
    # Your processing logic
    return {"id": patient_id, "status": "done"}

processor = ParallelProcessor(
    max_workers=4,
    checkpoint_file="results/checkpoint.json"
)

results = processor.map_with_checkpoint(
    process_patient,
    patient_list,
    desc="Processing patients"
)

processor.print_summary(results)
```

### Progress Tracking

```python
from cardiac_shared.progress import ProgressTracker

tracker = ProgressTracker()
tracker.start_overall("Processing Pipeline", total=100)

for i, item in enumerate(items):
    tracker.start_step(f"Step {i+1}", total=3)

    tracker.update_substep("Loading data")
    # ... load data
    tracker.update_step_progress()

    tracker.update_substep("Processing")
    # ... process
    tracker.update_step_progress()

    tracker.complete_step()
    tracker.update_overall(i + 1)

tracker.finish()
```

### Cache Management

```python
from cardiac_shared.cache import CacheManager

cache = CacheManager("results/cache.json")

for patient_id in patient_list:
    if cache.is_completed(patient_id):
        continue  # Skip already processed

    result = process_patient(patient_id)
    cache.mark_completed(patient_id, result)
```

### Configuration Management

```python
from cardiac_shared.config import ConfigManager

config = ConfigManager("config/settings.yaml")
db_host = config.get("database.host", default="localhost")
config.set("processing.batch_size", 32)
config.save()
```

### Intermediate Results Registry (v0.4.0)

```python
from cardiac_shared.data import get_registry

# Get singleton registry instance
registry = get_registry()

# Check if TotalSegmentator results are available
if registry.exists('segmentation.totalsegmentator_organs.chd_v2'):
    organs_path = registry.get_path('segmentation.totalsegmentator_organs.chd_v2')
    heart_mask = organs_path / patient_id / 'heart.nii.gz'

# Get metadata
meta = registry.get_metadata('body_composition.vbca_stage1_labels.zal_v3.2')
print(f"Patient count: {meta.get('patient_count')}")

# List available results
available = registry.list_available('segmentation')

# Get usage suggestion for a project
suggestion = registry.suggest_input('pcfa', 'heart_masks', 'chd')
```

### Data Source Management (v0.5.0)

```python
from cardiac_shared.data_sources import DataSourceManager

# Load from project config
manager = DataSourceManager('/path/to/data_sources.yaml')

# Or use project auto-discovery
manager = DataSourceManager.from_project('vbca')

# Get data source
source = manager.get_source('zal')
print(f"Input: {source.input_dir}")
print(f"Files: {source.file_count()}")

# Get input files
for file in source.get_files(limit=10):
    process(file)

# Check all sources status
manager.print_status()
```

### Vertebra Detection (v0.5.0)

```python
from cardiac_shared.vertebra import VertebraDetector, parse_vertebrae
import numpy as np

# Simple parsing
vertebrae = parse_vertebrae('/path/to/labels')
print(f"Found: {vertebrae}")  # ['T10', 'T11', 'T12', 'L1']

# Full analysis
detector = VertebraDetector()
vertebrae_info = detector.find_vertebrae('/path/to/labels')

for v in vertebrae_info:
    print(f"{v.name}: center slice {v.center_slice}")

# Get center slice from mask
mask = np.load('vertebrae_T12.npy')
center = detector.get_center_slice(mask)
```

### Tissue Classification (v0.5.0)

```python
from cardiac_shared.tissue import TissueClassifier, filter_tissue, TISSUE_HU_RANGES
import numpy as np

# Check HU ranges
print(TISSUE_HU_RANGES['skeletal_muscle']['range'])  # (-29, 150)

# Filter tissue by HU
filtered_mask, stats = filter_tissue(ct_array, mask, 'skeletal_muscle')
print(f"Retention: {stats.retention_pct:.1f}%")

# Full metrics calculation
classifier = TissueClassifier()
metrics = classifier.calculate_metrics(
    ct_array, mask, 'skeletal_muscle',
    spacing=(1.0, 0.5, 0.5),
    slice_idx=50  # Single slice
)
print(f"Area: {metrics.area_cm2:.1f} cm^2")
print(f"Mean HU: {metrics.mean_hu:.1f}")
print(f"Quality: {metrics.quality_grade}")
```

## Projects Using This Package

- [vbca](https://github.com/zhurong2020/vbca) - Vertebral Body Composition Analysis
- cardiac-ml-research - Main research project
- pcfa - Pericardial Fat Analysis
- ai-cac-research - CAC scoring research

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for full version history.

### v0.5.1 (2026-01-03)
- Added `hardware/gpu_utils.py` (GPU stabilization time optimization)
- Added `io/preloader.py` (AsyncNiftiPreloader for background preloading)
- ~5-10% speedup for TotalSegmentator pipelines
- 38 new unit tests

### v0.5.0 (2026-01-03)
- Added `data_sources` module (DataSourceManager for ZAL/CHD/Normal/Custom)
- Added `vertebra` module (VertebraDetector, ROI calculation)
- Added `tissue` module (TissueClassifier, Alberta Protocol 2024 HU ranges)
- 44 new unit tests (100% pass)

### v0.4.0 (2026-01-02)
- Added `data` module (IntermediateResultsRegistry)
- Cross-project intermediate results discovery and sharing
- Automatic Windows/WSL path conversion
- Usage pattern suggestions per project

### v0.3.0 (2026-01-02)
- Added `parallel` module (ParallelProcessor, checkpoint/resume)
- Added `progress` module (ProgressTracker, multi-level)
- Added `cache` module (CacheManager)
- Added `batch` module (BatchProcessor)
- Added `config` module (ConfigManager)
- Published to PyPI

### v0.2.0 (2026-01-02)
- Added `hardware` module (detector, cpu_optimizer)
- Added `environment` module (runtime_detector)

### v0.1.0 (2025-12-01)
- Initial release with IO modules

## License

MIT License - see [LICENSE](LICENSE) for details.
