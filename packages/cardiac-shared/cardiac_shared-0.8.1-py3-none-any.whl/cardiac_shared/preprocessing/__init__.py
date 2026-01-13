"""
Preprocessing utilities for cardiac imaging pipelines

Provides:
- DicomConverter: Unified DICOM to NIfTI conversion
- SharedPreprocessingPipeline: Multi-module preprocessing with deduplication
- PreprocessingConfig: Configuration for preprocessing pipeline
"""

from .dicom_converter import (
    DicomConverter,
    ConversionResult,
    convert_dicom_to_nifti,
)

from .pipeline import (
    SharedPreprocessingPipeline,
    PreprocessingConfig,
    PreprocessingResult,
    create_pipeline,
)

__all__ = [
    # DICOM Converter
    'DicomConverter',
    'ConversionResult',
    'convert_dicom_to_nifti',
    # Preprocessing Pipeline
    'SharedPreprocessingPipeline',
    'PreprocessingConfig',
    'PreprocessingResult',
    'create_pipeline',
]
