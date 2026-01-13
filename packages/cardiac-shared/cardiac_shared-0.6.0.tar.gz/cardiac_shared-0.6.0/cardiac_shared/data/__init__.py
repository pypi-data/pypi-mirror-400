"""
Data management module for cardiac imaging projects

Provides:
- IntermediateResultsRegistry: Cross-project data discovery and sharing
- BatchManager: Batch processing with manifest tracking
- BatchManifest: Manifest data structure for batch outputs
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
]
