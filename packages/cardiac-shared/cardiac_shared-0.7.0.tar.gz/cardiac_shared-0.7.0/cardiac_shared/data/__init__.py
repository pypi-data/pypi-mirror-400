"""
Data management module for cardiac imaging projects

Provides:
- IntermediateResultsRegistry: Cross-project data discovery and sharing
- BatchManager: Batch processing with manifest tracking
- BatchManifest: Manifest data structure for batch outputs
- BatchDiscovery: Dynamic batch discovery and selection (v0.6.4)
- DatasetRegistry: Unified dataset definitions with patient counts (v0.7.0)
"""

from .registry import (
    IntermediateResultsRegistry,
    RegistryEntry,
    get_registry,
)

from .batch_manager import (
    BatchManager,
    BatchManifest,
    PatientEntry,
    ConsumerRecord,
    create_nifti_batch,
    load_batch,
)

from .batch_discovery import (
    BatchDiscovery,
    BatchInfo,
    PatientBatchRecord,
    discover_batches,
)

from .datasets import (
    Dataset,
    DatasetStatus,
    DatasetCategory,
    SliceThickness,
    DatasetRegistry,
    get_dataset_registry,
    get_dataset,
    get_patient_count,
    list_datasets,
    print_dataset_summary,
    INTERNAL_DATASETS,
    EXTERNAL_DATASETS,
    ALL_DATASETS,
)

__all__ = [
    # Registry
    'IntermediateResultsRegistry',
    'RegistryEntry',
    'get_registry',
    # Batch Manager
    'BatchManager',
    'BatchManifest',
    'PatientEntry',
    'ConsumerRecord',
    'create_nifti_batch',
    'load_batch',
    # Batch Discovery (v0.6.4)
    'BatchDiscovery',
    'BatchInfo',
    'PatientBatchRecord',
    'discover_batches',
    # Dataset Registry (v0.7.0)
    'Dataset',
    'DatasetStatus',
    'DatasetCategory',
    'SliceThickness',
    'DatasetRegistry',
    'get_dataset_registry',
    'get_dataset',
    'get_patient_count',
    'list_datasets',
    'print_dataset_summary',
    'INTERNAL_DATASETS',
    'EXTERNAL_DATASETS',
    'ALL_DATASETS',
]
