"""
Dataset Registry - Unified dataset definitions for cardiac imaging research
数据集注册表 - 心脏影像研究统一数据集定义

This module provides a central registry for all datasets used in cardiac imaging
research, ensuring consistent patient counts and metadata across projects.

Data Source: ai-cac-research/config/data_sources_updated.yaml (authoritative)

Usage:
    from cardiac_shared.data import DatasetRegistry, get_dataset_registry

    # Get singleton registry
    registry = get_dataset_registry()

    # Get dataset info
    chd = registry.get('internal.chd')
    print(f"CHD patients: {chd.patient_count}")  # 489

    # Get all internal datasets
    internal = registry.list_datasets('internal')

    # Get total patient count
    total = registry.get_total_patients(['internal.chd', 'internal.normal'])
    print(f"Total: {total}")  # 766

Author: Cardiac ML Research Team
Created: 2026-01-04
Version: 0.7.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from enum import Enum


class DatasetStatus(Enum):
    """Dataset processing status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VALIDATED = "validated"
    ARCHIVED = "archived"


class DatasetCategory(Enum):
    """Dataset category"""
    INTERNAL = "internal"  # Dr. Chen's data
    EXTERNAL = "external"  # Public datasets (NLST, COCA, etc.)
    FUTURE = "future"      # Planned datasets


@dataclass
class SliceThickness:
    """Slice thickness configuration for paired scans"""
    thin: Optional[str] = None  # e.g., "1.0mm", "1.5mm", "2.0mm"
    thick: Optional[str] = None  # e.g., "5.0mm"

    def __str__(self) -> str:
        if self.thin and self.thick:
            return f"{self.thin} + {self.thick}"
        return self.thin or self.thick or "unknown"


@dataclass
class Dataset:
    """
    Dataset definition with patient count and metadata

    Attributes:
        id: Unique dataset identifier (e.g., 'internal.chd', 'nlst.batch1')
        name: Human-readable name
        description: Dataset description
        patient_count: Number of patients (authoritative count)
        category: Dataset category (internal/external/future)
        status: Processing status
        slice_thickness: Slice thickness configuration
        metadata: Additional metadata
    """
    id: str
    name: str
    description: str
    patient_count: int
    category: DatasetCategory = DatasetCategory.INTERNAL
    status: DatasetStatus = DatasetStatus.COMPLETED
    slice_thickness: Optional[SliceThickness] = None
    group_tag: Optional[str] = None
    root_dir: Optional[str] = None
    results_dir: Optional[str] = None
    metadata_index: Optional[str] = None
    notes: Optional[str] = None
    sub_batches: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_paired(self) -> bool:
        """Check if dataset has paired thin/thick scans"""
        return self.slice_thickness is not None and \
               self.slice_thickness.thin is not None and \
               self.slice_thickness.thick is not None


# =============================================================================
# Authoritative Dataset Definitions (from ai-cac-research)
# =============================================================================

INTERNAL_DATASETS = {
    # CHD Group - Confirmed CAD patients
    "internal.chd": Dataset(
        id="internal.chd",
        name="Internal CHD Group",
        description="Confirmed coronary artery disease patients from Dr. Chen",
        patient_count=489,
        category=DatasetCategory.INTERNAL,
        status=DatasetStatus.VALIDATED,
        slice_thickness=SliceThickness(thin="1.0mm/1.5mm", thick="5.0mm"),
        group_tag="chd",
        notes="内部数据集 - 确认冠心病患者 (489例)",
        metadata={
            "source": "Dr. Chen",
            "paired_scans": True,
            "metadata_coverage": "99.5%",
            "cac_positive_rate": "72.8%",
        }
    ),

    # Normal Group - General population (no confirmed CAD)
    "internal.normal": Dataset(
        id="internal.normal",
        name="Internal Normal Group",
        description="General population control group from Dr. Chen",
        patient_count=277,
        category=DatasetCategory.INTERNAL,
        status=DatasetStatus.VALIDATED,
        slice_thickness=SliceThickness(thin="1.0mm/1.5mm", thick="5.0mm"),
        group_tag="normal",
        notes="内部数据集 - 一般人/正常对照组 (277例)",
        metadata={
            "source": "Dr. Chen",
            "paired_scans": True,
            "metadata_coverage": "99.5%",
            "cac_positive_rate": "9.7%",
        }
    ),

    # Combined internal dataset
    "internal.all": Dataset(
        id="internal.all",
        name="Internal Dataset (All)",
        description="Complete internal dataset from Dr. Chen",
        patient_count=766,
        category=DatasetCategory.INTERNAL,
        status=DatasetStatus.VALIDATED,
        slice_thickness=SliceThickness(thin="1.0mm/1.5mm", thick="5.0mm"),
        group_tag="internal_all",
        sub_batches=["internal.chd", "internal.normal"],
        notes="内部数据集全集 - CHD 489例 + Normal 277例 = 766例",
        metadata={
            "source": "Dr. Chen",
            "paired_scans": True,
            "unique_patients": 765,  # 1 duplicate
            "metadata_coverage": "99.5%",
        }
    ),
}

EXTERNAL_DATASETS = {
    # NLST Batches
    "nlst.batch1": Dataset(
        id="nlst.batch1",
        name="NLST Batch 1",
        description="NLST 2mm + 5mm paired data - First batch",
        patient_count=108,
        category=DatasetCategory.EXTERNAL,
        status=DatasetStatus.COMPLETED,
        slice_thickness=SliceThickness(thin="2.0mm", thick="5.0mm"),
        group_tag="nlst_batch1",
        notes="NLST Batch 1 - 108例, RESCUE率 11.1%",
    ),

    "nlst.batch2": Dataset(
        id="nlst.batch2",
        name="NLST Batch 2",
        description="NLST additional paired data",
        patient_count=92,
        category=DatasetCategory.EXTERNAL,
        status=DatasetStatus.COMPLETED,
        slice_thickness=SliceThickness(thin="2.0mm", thick="5.0mm"),
        group_tag="nlst_batch2",
        notes="NLST Batch 2 - 92例",
    ),

    "nlst.batch3": Dataset(
        id="nlst.batch3",
        name="NLST Batch 3",
        description="NLST large batch",
        patient_count=402,
        category=DatasetCategory.EXTERNAL,
        status=DatasetStatus.COMPLETED,
        slice_thickness=SliceThickness(thin="2.0mm", thick="5.0mm"),
        group_tag="nlst_batch3",
        notes="NLST Batch 3 - 402例",
    ),

    "nlst.batch4": Dataset(
        id="nlst.batch4",
        name="NLST Batch 4",
        description="NLST final batch",
        patient_count=255,
        category=DatasetCategory.EXTERNAL,
        status=DatasetStatus.COMPLETED,
        slice_thickness=SliceThickness(thin="2.0mm", thick="5.0mm"),
        group_tag="nlst_batch4",
        notes="NLST Batch 4 - 255例",
    ),

    "nlst.all": Dataset(
        id="nlst.all",
        name="NLST All Batches",
        description="Complete NLST dataset (all 4 batches)",
        patient_count=857,
        category=DatasetCategory.EXTERNAL,
        status=DatasetStatus.COMPLETED,
        slice_thickness=SliceThickness(thin="2.0mm", thick="5.0mm"),
        group_tag="nlst_all",
        sub_batches=["nlst.batch1", "nlst.batch2", "nlst.batch3", "nlst.batch4"],
        notes="NLST全集 - 857例 (852例成功配对, 99.4%成功率), RESCUE率 10.2%",
        metadata={
            "successful_pairs": 852,
            "rescue_cases": 87,
            "rescue_rate": "10.2%",
            "pearson_correlation": 0.9721,
        }
    ),

    # Stanford COCA
    "coca.gated": Dataset(
        id="coca.gated",
        name="Stanford COCA - Gated CT",
        description="ECG-gated coronary CT with CAC annotations",
        patient_count=444,
        category=DatasetCategory.EXTERNAL,
        status=DatasetStatus.VALIDATED,
        slice_thickness=SliceThickness(thin="3.0mm", thick=None),
        group_tag="coca_gated",
        notes="Stanford COCA Gated - 444例, per-vessel ground truth",
        metadata={
            "ground_truth_format": "xml",
            "citation": "Zeleznik et al., Nature Communications 2021",
        }
    ),

    "coca.nongated": Dataset(
        id="coca.nongated",
        name="Stanford COCA - Nongated CT",
        description="Non-gated chest CT with CAC annotations",
        patient_count=213,
        category=DatasetCategory.EXTERNAL,
        status=DatasetStatus.VALIDATED,
        slice_thickness=SliceThickness(thin="5.0mm/3.0mm", thick=None),
        group_tag="coca_nongated",
        notes="Stanford COCA Nongated - 213例, 唯一公开非门控CAC真值数据集",
        metadata={
            "ground_truth_format": "excel",
        }
    ),

    "coca.all": Dataset(
        id="coca.all",
        name="Stanford COCA All",
        description="Complete COCA dataset",
        patient_count=657,
        category=DatasetCategory.EXTERNAL,
        status=DatasetStatus.VALIDATED,
        group_tag="coca_all",
        sub_batches=["coca.gated", "coca.nongated"],
        notes="COCA全集 - Gated 444例 + Nongated 213例 = 657例",
    ),

    # TotalSegmentator
    "totalsegmentator": Dataset(
        id="totalsegmentator",
        name="TotalSegmentator Dataset",
        description="1.5mm CT scans with organ segmentations",
        patient_count=1228,
        category=DatasetCategory.EXTERNAL,
        status=DatasetStatus.PLANNED,
        slice_thickness=SliceThickness(thin="1.5mm", thick=None),
        group_tag="totalseg",
        notes="TotalSegmentator - 1228例, 117器官分割, P1优先级",
        metadata={
            "segmentation_organs": 117,
            "aorta_coverage": "100%",
            "heart_coverage": "100%",
            "research_value": "Aortic calcification, anatomically-guided CAC",
        }
    ),
}

# Combined datasets dict
ALL_DATASETS = {**INTERNAL_DATASETS, **EXTERNAL_DATASETS}


class DatasetRegistry:
    """
    Central registry for dataset definitions

    Provides unified access to all dataset definitions with patient counts
    that are authoritative across all cardiac imaging projects.
    """

    def __init__(self):
        self._datasets: Dict[str, Dataset] = ALL_DATASETS.copy()

    def get(self, dataset_id: str) -> Optional[Dataset]:
        """Get dataset by ID"""
        return self._datasets.get(dataset_id)

    def __getitem__(self, dataset_id: str) -> Dataset:
        """Get dataset by ID (raises KeyError if not found)"""
        return self._datasets[dataset_id]

    def exists(self, dataset_id: str) -> bool:
        """Check if dataset exists"""
        return dataset_id in self._datasets

    def list_datasets(self, category: Optional[str] = None) -> List[str]:
        """
        List all dataset IDs, optionally filtered by category prefix

        Args:
            category: Filter by category prefix (e.g., 'internal', 'nlst', 'coca')
        """
        if category:
            return [k for k in self._datasets.keys() if k.startswith(f"{category}.")]
        return list(self._datasets.keys())

    def get_patient_count(self, dataset_id: str) -> int:
        """Get patient count for a dataset"""
        dataset = self.get(dataset_id)
        return dataset.patient_count if dataset else 0

    def get_total_patients(self, dataset_ids: List[str]) -> int:
        """Get total patient count for multiple datasets"""
        return sum(self.get_patient_count(did) for did in dataset_ids)

    def get_by_category(self, category: DatasetCategory) -> List[Dataset]:
        """Get all datasets in a category"""
        return [d for d in self._datasets.values() if d.category == category]

    def get_by_status(self, status: DatasetStatus) -> List[Dataset]:
        """Get all datasets with a specific status"""
        return [d for d in self._datasets.values() if d.status == status]

    def summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        internal = self.get_patient_count("internal.all")
        nlst = self.get_patient_count("nlst.all")
        coca = self.get_patient_count("coca.all")

        return {
            "internal": {
                "total": internal,
                "chd": self.get_patient_count("internal.chd"),
                "normal": self.get_patient_count("internal.normal"),
            },
            "external": {
                "nlst": nlst,
                "coca": coca,
                "totalsegmentator": self.get_patient_count("totalsegmentator"),
            },
            "grand_total": {
                "validated": internal + nlst + coca,  # 766 + 857 + 657 = 2280
                "including_planned": internal + nlst + coca + self.get_patient_count("totalsegmentator"),
            }
        }

    def print_summary(self) -> None:
        """Print formatted summary"""
        s = self.summary()
        print("=" * 60)
        print("CARDIAC IMAGING DATASET REGISTRY")
        print("=" * 60)
        print("\nInternal Datasets (Dr. Chen):")
        print(f"  CHD Group:    {s['internal']['chd']:>5} patients")
        print(f"  Normal Group: {s['internal']['normal']:>5} patients")
        print(f"  Total:        {s['internal']['total']:>5} patients")
        print("\nExternal Datasets:")
        print(f"  NLST:              {s['external']['nlst']:>5} patients (4 batches)")
        print(f"  COCA:              {s['external']['coca']:>5} patients (Gated + Nongated)")
        print(f"  TotalSegmentator:  {s['external']['totalsegmentator']:>5} patients (planned)")
        print("\nGrand Total:")
        print(f"  Validated:   {s['grand_total']['validated']:>5} patients")
        print(f"  With Planned: {s['grand_total']['including_planned']:>5} patients")
        print("=" * 60)


# Singleton instance
_registry_instance: Optional[DatasetRegistry] = None


def get_dataset_registry() -> DatasetRegistry:
    """Get or create singleton registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = DatasetRegistry()
    return _registry_instance


# Convenience functions
def get_dataset(dataset_id: str) -> Optional[Dataset]:
    """Get dataset by ID"""
    return get_dataset_registry().get(dataset_id)


def get_patient_count(dataset_id: str) -> int:
    """Get patient count for a dataset"""
    return get_dataset_registry().get_patient_count(dataset_id)


def list_datasets(category: Optional[str] = None) -> List[str]:
    """List all dataset IDs"""
    return get_dataset_registry().list_datasets(category)


def print_dataset_summary() -> None:
    """Print dataset summary"""
    get_dataset_registry().print_summary()
