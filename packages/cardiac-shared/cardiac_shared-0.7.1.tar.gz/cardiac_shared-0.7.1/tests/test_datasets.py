"""
Unit tests for Dataset Registry module

Tests the unified dataset definitions and registry functionality.
"""

import pytest
from cardiac_shared.data.datasets import (
    Dataset,
    DatasetStatus,
    DatasetCategory,
    SliceThickness,
    DatasetRegistry,
    get_dataset_registry,
    get_dataset,
    get_patient_count,
    list_datasets,
    INTERNAL_DATASETS,
    EXTERNAL_DATASETS,
    ALL_DATASETS,
)


class TestSliceThickness:
    """Tests for SliceThickness dataclass"""

    def test_slice_thickness_paired(self):
        st = SliceThickness(thin="1.0mm", thick="5.0mm")
        assert str(st) == "1.0mm + 5.0mm"

    def test_slice_thickness_thin_only(self):
        st = SliceThickness(thin="2.0mm")
        assert str(st) == "2.0mm"

    def test_slice_thickness_thick_only(self):
        st = SliceThickness(thick="5.0mm")
        assert str(st) == "5.0mm"

    def test_slice_thickness_none(self):
        st = SliceThickness()
        assert str(st) == "unknown"


class TestDataset:
    """Tests for Dataset dataclass"""

    def test_dataset_creation(self):
        ds = Dataset(
            id="test.dataset",
            name="Test Dataset",
            description="A test dataset",
            patient_count=100,
        )
        assert ds.id == "test.dataset"
        assert ds.patient_count == 100
        assert ds.category == DatasetCategory.INTERNAL
        assert ds.status == DatasetStatus.COMPLETED

    def test_dataset_is_paired(self):
        ds_paired = Dataset(
            id="test.paired",
            name="Paired",
            description="Paired dataset",
            patient_count=100,
            slice_thickness=SliceThickness(thin="1.0mm", thick="5.0mm"),
        )
        assert ds_paired.is_paired is True

        ds_single = Dataset(
            id="test.single",
            name="Single",
            description="Single thickness",
            patient_count=100,
            slice_thickness=SliceThickness(thin="1.0mm"),
        )
        assert ds_single.is_paired is False

        ds_none = Dataset(
            id="test.none",
            name="None",
            description="No thickness",
            patient_count=100,
        )
        assert ds_none.is_paired is False


class TestInternalDatasets:
    """Tests for internal dataset definitions"""

    def test_internal_chd_count(self):
        """CHD group should have 489 patients"""
        assert INTERNAL_DATASETS["internal.chd"].patient_count == 489

    def test_internal_normal_count(self):
        """Normal group should have 277 patients"""
        assert INTERNAL_DATASETS["internal.normal"].patient_count == 277

    def test_internal_all_count(self):
        """All internal should have 765 unique patients (766 cases, 1 duplicate)"""
        assert INTERNAL_DATASETS["internal.all"].patient_count == 765

    def test_internal_all_sub_batches(self):
        """internal.all should reference chd and normal"""
        all_ds = INTERNAL_DATASETS["internal.all"]
        assert "internal.chd" in all_ds.sub_batches
        assert "internal.normal" in all_ds.sub_batches

    def test_internal_category(self):
        """All internal datasets should have INTERNAL category"""
        for ds in INTERNAL_DATASETS.values():
            assert ds.category == DatasetCategory.INTERNAL


class TestExternalDatasets:
    """Tests for external dataset definitions"""

    def test_nlst_batch_counts(self):
        """NLST batch counts: 108, 92, 402, 255"""
        assert EXTERNAL_DATASETS["nlst.batch1"].patient_count == 108
        assert EXTERNAL_DATASETS["nlst.batch2"].patient_count == 92
        assert EXTERNAL_DATASETS["nlst.batch3"].patient_count == 402
        assert EXTERNAL_DATASETS["nlst.batch4"].patient_count == 255

    def test_nlst_all_count(self):
        """NLST all should have 857 patients"""
        assert EXTERNAL_DATASETS["nlst.all"].patient_count == 857

    def test_nlst_sum_matches_all(self):
        """Sum of NLST batches should equal nlst.all"""
        batch_sum = sum(
            EXTERNAL_DATASETS[f"nlst.batch{i}"].patient_count
            for i in range(1, 5)
        )
        assert batch_sum == EXTERNAL_DATASETS["nlst.all"].patient_count

    def test_coca_counts(self):
        """COCA: Gated 444, Nongated 213, All 657"""
        assert EXTERNAL_DATASETS["coca.gated"].patient_count == 444
        assert EXTERNAL_DATASETS["coca.nongated"].patient_count == 213
        assert EXTERNAL_DATASETS["coca.all"].patient_count == 657

    def test_coca_sum_matches_all(self):
        """Sum of COCA parts should equal coca.all"""
        coca_sum = (
            EXTERNAL_DATASETS["coca.gated"].patient_count +
            EXTERNAL_DATASETS["coca.nongated"].patient_count
        )
        assert coca_sum == EXTERNAL_DATASETS["coca.all"].patient_count

    def test_totalsegmentator_count(self):
        """TotalSegmentator should have 1228 patients"""
        assert EXTERNAL_DATASETS["totalsegmentator"].patient_count == 1228

    def test_totalsegmentator_planned_status(self):
        """TotalSegmentator should be in PLANNED status"""
        assert EXTERNAL_DATASETS["totalsegmentator"].status == DatasetStatus.PLANNED

    def test_external_category(self):
        """All external datasets should have EXTERNAL category"""
        for ds in EXTERNAL_DATASETS.values():
            assert ds.category == DatasetCategory.EXTERNAL


class TestDatasetRegistry:
    """Tests for DatasetRegistry class"""

    def test_get_existing_dataset(self):
        registry = DatasetRegistry()
        ds = registry.get("internal.chd")
        assert ds is not None
        assert ds.patient_count == 489

    def test_get_nonexistent_dataset(self):
        registry = DatasetRegistry()
        ds = registry.get("nonexistent.dataset")
        assert ds is None

    def test_getitem_existing(self):
        registry = DatasetRegistry()
        ds = registry["internal.chd"]
        assert ds.patient_count == 489

    def test_getitem_raises_keyerror(self):
        registry = DatasetRegistry()
        with pytest.raises(KeyError):
            _ = registry["nonexistent.dataset"]

    def test_exists(self):
        registry = DatasetRegistry()
        assert registry.exists("internal.chd") is True
        assert registry.exists("nonexistent") is False

    def test_list_datasets_all(self):
        registry = DatasetRegistry()
        all_ids = registry.list_datasets()
        assert "internal.chd" in all_ids
        assert "nlst.all" in all_ids
        assert "coca.gated" in all_ids

    def test_list_datasets_by_category(self):
        registry = DatasetRegistry()

        internal = registry.list_datasets("internal")
        assert "internal.chd" in internal
        assert "internal.normal" in internal
        assert "nlst.all" not in internal

        nlst = registry.list_datasets("nlst")
        assert "nlst.batch1" in nlst
        assert "nlst.all" in nlst
        assert "internal.chd" not in nlst

    def test_get_patient_count(self):
        registry = DatasetRegistry()
        assert registry.get_patient_count("internal.chd") == 489
        assert registry.get_patient_count("nonexistent") == 0

    def test_get_total_patients(self):
        registry = DatasetRegistry()
        total = registry.get_total_patients(["internal.chd", "internal.normal"])
        assert total == 766  # Cases count (489 + 277), not unique patients

    def test_get_by_category(self):
        registry = DatasetRegistry()
        internal = registry.get_by_category(DatasetCategory.INTERNAL)
        assert len(internal) == 3  # chd, normal, all
        for ds in internal:
            assert ds.category == DatasetCategory.INTERNAL

    def test_get_by_status(self):
        registry = DatasetRegistry()
        validated = registry.get_by_status(DatasetStatus.VALIDATED)
        assert any(ds.id == "internal.chd" for ds in validated)
        assert any(ds.id == "coca.gated" for ds in validated)

    def test_summary(self):
        registry = DatasetRegistry()
        summary = registry.summary()

        assert summary["internal"]["chd"] == 489
        assert summary["internal"]["normal"] == 277
        assert summary["internal"]["total"] == 765  # Unique patients

        assert summary["external"]["nlst"] == 857
        assert summary["external"]["coca"] == 657
        assert summary["external"]["totalsegmentator"] == 1228

        # 765 + 857 + 657 = 2279
        assert summary["grand_total"]["validated"] == 2279


class TestSingletonRegistry:
    """Tests for singleton registry pattern"""

    def test_get_dataset_registry_singleton(self):
        reg1 = get_dataset_registry()
        reg2 = get_dataset_registry()
        assert reg1 is reg2

    def test_get_dataset_convenience(self):
        ds = get_dataset("internal.chd")
        assert ds is not None
        assert ds.patient_count == 489

    def test_get_patient_count_convenience(self):
        count = get_patient_count("internal.all")
        assert count == 765  # Unique patients

    def test_list_datasets_convenience(self):
        internal = list_datasets("internal")
        assert "internal.chd" in internal


class TestDataIntegrity:
    """Tests for data integrity across datasets"""

    def test_all_datasets_combined(self):
        """ALL_DATASETS should contain all internal and external"""
        assert len(ALL_DATASETS) == len(INTERNAL_DATASETS) + len(EXTERNAL_DATASETS)

    def test_no_duplicate_ids(self):
        """Dataset IDs should be unique"""
        all_ids = list(ALL_DATASETS.keys())
        assert len(all_ids) == len(set(all_ids))

    def test_grand_total_calculation(self):
        """Grand total should match expected values"""
        registry = DatasetRegistry()
        summary = registry.summary()

        # Internal: 765 unique patients
        assert summary["internal"]["total"] == 765

        # External validated: 857 + 657 = 1514
        external_validated = summary["external"]["nlst"] + summary["external"]["coca"]
        assert external_validated == 1514

        # Grand total validated: 765 + 857 + 657 = 2279
        assert summary["grand_total"]["validated"] == 2279

        # Including planned: 2279 + 1228 = 3507
        assert summary["grand_total"]["including_planned"] == 3507
