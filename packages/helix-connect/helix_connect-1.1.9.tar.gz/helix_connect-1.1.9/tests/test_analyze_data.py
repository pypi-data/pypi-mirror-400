"""
Test suite for the _analyze_data functionality in HelixProducer.

Tests cover:
1. Empty file handling
2. Single record analysis
3. Missing fields counting
4. Empty value detection (null, "", [], {})
5. Nested object traversal (dot notation)
6. Arrays of objects ([] notation)
7. Schema sampling from first N records
8. Malformed JSON handling
9. Large file memory efficiency
10. Integration with upload metadata
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Get the testdata directory path
TESTDATA_DIR = Path(__file__).parent / "testdata"


class MockProducer:
    """
    Minimal mock of HelixProducer with only the analysis methods.
    This avoids needing AWS credentials for unit tests.
    """

    def _is_empty_value(self, value) -> bool:
        """Check if a value is considered empty."""
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        return False

    def _get_field_status(self, obj, prefix: str) -> tuple:
        """Recursively collect field paths and their presence status."""
        all_fields = set()
        present_fields = set()

        if isinstance(obj, dict):
            for key, value in obj.items():
                field_path = f"{prefix}.{key}" if prefix else key
                all_fields.add(field_path)

                if not self._is_empty_value(value):
                    present_fields.add(field_path)

                    if isinstance(value, dict):
                        nested_all, nested_present = self._get_field_status(
                            value, field_path
                        )
                        all_fields.update(nested_all)
                        present_fields.update(nested_present)
                    elif isinstance(value, list) and value:
                        if isinstance(value[0], dict):
                            for item in value:
                                if isinstance(item, dict):
                                    nested_all, nested_present = self._get_field_status(
                                        item, f"{field_path}[]"
                                    )
                                    all_fields.update(nested_all)
                                    present_fields.update(nested_present)

        return all_fields, present_fields

    def _analyze_data(self, file_path: str, schema_sample_limit: int = 1000) -> dict:
        """Analyze dataset to extract schema and field emptiness statistics."""
        from genson import SchemaBuilder

        schema_builder = SchemaBuilder()
        all_fields = set()
        field_present_count = {}
        record_count = 0
        analysis_errors = 0

        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    analysis_errors += 1
                    continue

                record_count += 1

                if schema_sample_limit == 0 or record_count <= schema_sample_limit:
                    schema_builder.add_object(record)

                discovered, present = self._get_field_status(record, "")
                all_fields.update(discovered)

                for field in present:
                    field_present_count[field] = field_present_count.get(field, 0) + 1

        field_emptiness = {}
        for field in all_fields:
            present = field_present_count.get(field, 0)
            missing_or_empty = record_count - present
            percentage = (
                (missing_or_empty / record_count * 100) if record_count > 0 else 0.0
            )
            field_emptiness[field] = round(percentage, 2)

        field_emptiness = dict(
            sorted(field_emptiness.items(), key=lambda x: x[1], reverse=True)
        )

        schema = schema_builder.to_schema() if record_count > 0 else {}

        return {
            "schema": schema,
            "field_emptiness": field_emptiness,
            "record_count": record_count,
            "analysis_errors": analysis_errors,
        }


@pytest.fixture
def producer():
    """Create a mock producer for testing."""
    return MockProducer()


class TestIsEmptyValue:
    """Tests for _is_empty_value method."""

    def test_none_is_empty(self, producer):
        assert producer._is_empty_value(None) is True

    def test_empty_string_is_empty(self, producer):
        assert producer._is_empty_value("") is True

    def test_whitespace_string_is_empty(self, producer):
        assert producer._is_empty_value("   ") is True
        assert producer._is_empty_value("\t\n") is True

    def test_empty_list_is_empty(self, producer):
        assert producer._is_empty_value([]) is True

    def test_empty_dict_is_empty(self, producer):
        assert producer._is_empty_value({}) is True

    def test_non_empty_string_not_empty(self, producer):
        assert producer._is_empty_value("hello") is False

    def test_non_empty_list_not_empty(self, producer):
        assert producer._is_empty_value([1, 2, 3]) is False

    def test_non_empty_dict_not_empty(self, producer):
        assert producer._is_empty_value({"key": "value"}) is False

    def test_zero_not_empty(self, producer):
        assert producer._is_empty_value(0) is False

    def test_false_not_empty(self, producer):
        assert producer._is_empty_value(False) is False


class TestGetFieldStatus:
    """Tests for _get_field_status method."""

    def test_flat_object(self, producer):
        obj = {"name": "Alice", "age": 30}
        all_fields, present = producer._get_field_status(obj, "")

        assert all_fields == {"name", "age"}
        assert present == {"name", "age"}

    def test_flat_object_with_empty_values(self, producer):
        obj = {"name": "Alice", "email": "", "phone": None}
        all_fields, present = producer._get_field_status(obj, "")

        assert all_fields == {"name", "email", "phone"}
        assert present == {"name"}  # Only name is non-empty

    def test_nested_object(self, producer):
        obj = {"user": {"name": "Alice", "address": {"city": "NYC"}}}
        all_fields, present = producer._get_field_status(obj, "")

        assert "user" in all_fields
        assert "user.name" in all_fields
        assert "user.address" in all_fields
        assert "user.address.city" in all_fields

        assert "user" in present
        assert "user.name" in present
        assert "user.address.city" in present

    def test_array_of_objects(self, producer):
        obj = {"items": [{"id": 1, "name": "Item1"}, {"id": 2, "name": "Item2"}]}
        all_fields, present = producer._get_field_status(obj, "")

        assert "items" in all_fields
        assert "items[].id" in all_fields
        assert "items[].name" in all_fields

    def test_empty_array(self, producer):
        obj = {"items": []}
        all_fields, present = producer._get_field_status(obj, "")

        assert "items" in all_fields
        assert "items" not in present  # Empty array is empty


class TestAnalyzeDataEmptyFile:
    """Tests for empty file handling."""

    def test_empty_file(self, producer):
        result = producer._analyze_data(TESTDATA_DIR / "empty.ndjson")

        assert result["record_count"] == 0
        assert result["field_emptiness"] == {}
        assert result["schema"] == {}
        assert result["analysis_errors"] == 0


class TestAnalyzeDataSingleRecord:
    """Tests for single record analysis."""

    def test_single_record(self, producer):
        result = producer._analyze_data(TESTDATA_DIR / "single_record.ndjson")

        assert result["record_count"] == 1
        assert result["analysis_errors"] == 0

        # All fields should be 0% empty
        for field, emptiness in result["field_emptiness"].items():
            assert emptiness == 0.0, f"Field {field} should be 0% empty"

        # Schema should have all fields
        schema = result["schema"]
        assert schema["type"] == "object"
        assert "id" in schema["properties"]
        assert "name" in schema["properties"]
        assert "active" in schema["properties"]
        assert "score" in schema["properties"]


class TestAnalyzeDataMissingFields:
    """Tests for missing field handling."""

    def test_missing_fields_counted_as_empty(self, producer):
        result = producer._analyze_data(TESTDATA_DIR / "missing_fields.ndjson")

        assert result["record_count"] == 3

        emptiness = result["field_emptiness"]

        # name: present in all 3 records
        assert emptiness["name"] == 0.0

        # email: present in 2/3 records, missing in 1
        assert emptiness["email"] == pytest.approx(33.33, abs=0.01)

        # phone: present in 1/3 records, missing in 2
        assert emptiness["phone"] == pytest.approx(66.67, abs=0.01)


class TestAnalyzeDataEmptyValues:
    """Tests for empty value detection."""

    def test_empty_values_detected(self, producer):
        result = producer._analyze_data(TESTDATA_DIR / "simple.ndjson")

        assert result["record_count"] == 3
        emptiness = result["field_emptiness"]

        # name: all 3 have names
        assert emptiness["name"] == 0.0

        # email: 1 empty (""), 2 have values
        assert emptiness["email"] == pytest.approx(33.33, abs=0.01)

        # phone: 1 empty (""), 1 null, 1 has value = 66.67% empty
        assert emptiness["phone"] == pytest.approx(66.67, abs=0.01)


class TestAnalyzeDataNestedObjects:
    """Tests for nested object analysis."""

    def test_nested_objects_dot_notation(self, producer):
        result = producer._analyze_data(TESTDATA_DIR / "nested.ndjson")

        assert result["record_count"] == 3
        emptiness = result["field_emptiness"]

        # Check nested field paths exist
        assert "user" in emptiness
        assert "user.name" in emptiness
        assert "user.address" in emptiness
        assert "user.address.city" in emptiness
        assert "user.address.zip" in emptiness

        # user.name: all 3 have names
        assert emptiness["user.name"] == 0.0

        # user.address.city: 1 empty (""), 2 have values
        assert emptiness["user.address.city"] == pytest.approx(33.33, abs=0.01)

        # user.address.zip: 1 empty (""), 1 null, 1 has value
        assert emptiness["user.address.zip"] == pytest.approx(66.67, abs=0.01)


class TestAnalyzeDataArrays:
    """Tests for arrays of objects."""

    def test_arrays_of_objects(self, producer):
        result = producer._analyze_data(TESTDATA_DIR / "arrays.ndjson")

        assert result["record_count"] == 3
        emptiness = result["field_emptiness"]

        # Check array field paths exist
        assert "id" in emptiness
        assert "items" in emptiness

        # items: 1 record has empty array = 33.33% empty
        assert emptiness["items"] == pytest.approx(33.33, abs=0.01)


class TestAnalyzeDataSchemaSampling:
    """Tests for schema sampling behavior."""

    def test_schema_sampling_limit(self, producer):
        # Create a temp file with many records
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False) as f:
            # First record has field "a"
            f.write('{"a": 1}\n')
            # Records 2-10 have field "b"
            for i in range(9):
                f.write('{"b": 2}\n')
            # Record 11+ has field "c" (beyond default sample limit of 1000, but within our test limit)
            f.write('{"c": 3}\n')
            temp_path = f.name

        try:
            # With sample limit of 5, schema should include "a" and "b" but not "c"
            result = producer._analyze_data(temp_path, schema_sample_limit=5)

            schema = result["schema"]
            assert "a" in schema.get("properties", {})
            assert "b" in schema.get("properties", {})
            # "c" appears after sample limit, so not in schema
            assert "c" not in schema.get("properties", {})

            # But field_emptiness should have all fields (full scan)
            assert "a" in result["field_emptiness"]
            assert "b" in result["field_emptiness"]
            assert "c" in result["field_emptiness"]
        finally:
            os.unlink(temp_path)

    def test_schema_sample_all_records(self, producer):
        # With sample_limit=0, all records should be sampled for schema
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False) as f:
            f.write('{"a": 1}\n')
            for i in range(100):
                f.write('{"b": 2}\n')
            f.write('{"c": 3}\n')  # Last record has new field
            temp_path = f.name

        try:
            result = producer._analyze_data(temp_path, schema_sample_limit=0)
            schema = result["schema"]

            # All fields should be in schema
            assert "a" in schema.get("properties", {})
            assert "b" in schema.get("properties", {})
            assert "c" in schema.get("properties", {})
        finally:
            os.unlink(temp_path)


class TestAnalyzeDataMalformedJSON:
    """Tests for malformed JSON handling."""

    def test_malformed_json_counted_as_errors(self, producer):
        result = producer._analyze_data(TESTDATA_DIR / "malformed.ndjson")

        # 3 valid records, 2 invalid
        assert result["record_count"] == 3
        assert result["analysis_errors"] == 2

        # Valid records should still be analyzed
        emptiness = result["field_emptiness"]
        assert "valid" in emptiness
        assert "count" in emptiness


class TestAnalyzeDataLargeFile:
    """Tests for memory efficiency with large files."""

    def test_large_file_memory_efficient(self, producer):
        """
        Test that analysis doesn't load entire file into memory.
        Creates a large file and verifies it can be processed.
        """
        # Create a file with 10,000 records
        record_count = 10000
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False) as f:
            for i in range(record_count):
                record = {
                    "id": i,
                    "name": f"User{i}",
                    "email": f"user{i}@example.com" if i % 2 == 0 else "",
                    "score": i * 1.5,
                }
                f.write(json.dumps(record) + "\n")
            temp_path = f.name

        try:
            result = producer._analyze_data(temp_path)

            assert result["record_count"] == record_count
            assert result["analysis_errors"] == 0

            # email: 50% empty (every other record)
            assert result["field_emptiness"]["email"] == 50.0
        finally:
            os.unlink(temp_path)


class TestAnalyzeDataIntegration:
    """Integration tests with full HelixProducer (mocked AWS)."""

    def test_upload_includes_analysis_metadata(self):
        """Test that upload_dataset includes analysis results in metadata."""
        with patch("helix_connect.producer.boto3"):
            with patch("helix_connect.consumer.boto3.Session"):
                from helix_connect.producer import HelixProducer

                # Create producer with mocked AWS
                producer = HelixProducer(
                    aws_access_key_id="test",
                    aws_secret_access_key="test",
                    customer_id="test-customer",
                )

                # Mock required attributes
                producer.bucket_name = "test-bucket"
                producer.kms_key_id = "test-key"
                producer.s3 = Mock()
                producer.kms = Mock()
                producer.kms.encrypt = Mock(
                    return_value={"CiphertextBlob": b"encrypted"}
                )

                # Mock API request to capture payload
                captured_payload = {}

                def capture_api_request(method, path, **kwargs):
                    if "json" in kwargs:
                        captured_payload.update(kwargs["json"])
                    return {"_id": "test-dataset-id"}

                producer._make_api_request = capture_api_request

                # Create test file
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".ndjson", delete=False
                ) as f:
                    f.write('{"name": "Test", "value": 123}\n')
                    f.write('{"name": "", "value": 456}\n')
                    temp_path = f.name

                try:
                    # Upload dataset
                    producer.upload_dataset(
                        file_path=temp_path,
                        dataset_name="test-dataset",
                        description="Test",
                    )

                    # Verify payload aligns with dataset schema defaults
                    assert captured_payload["_id"].startswith(
                        "test-customer-test-dataset"
                    )
                    assert captured_payload["name"] == "test-dataset"
                    assert captured_payload["visibility"] == "private"
                    assert captured_payload["status"] == "active"
                    assert captured_payload["record_count"] == 2
                    assert captured_payload["s3_bucket_name"] == producer.bucket_name
                    assert captured_payload["s3_key"].startswith(
                        "datasets/test-dataset"
                    )
                    assert captured_payload["metadata"]["record_count"] == 2

                    # Schema should surface at top-level and inside metadata for backwards compat
                    assert (
                        captured_payload["schema"]
                        == captured_payload["metadata"]["schema"]
                    )

                    # Check field emptiness persisted in metadata
                    field_emptiness = captured_payload["metadata"].get(
                        "field_emptiness", {}
                    )
                    assert "name" in field_emptiness
                    assert field_emptiness["name"] == 50.0  # 1/2 empty
                finally:
                    os.unlink(temp_path)

    def test_dataset_payload_matches_schema_defaults(self):
        """Ensure dataset payload satisfies the shared dataset schema."""
        with patch("helix_connect.producer.boto3"):
            with patch("helix_connect.consumer.boto3.Session"):
                from helix_connect.producer import HelixProducer

                producer = HelixProducer(
                    aws_access_key_id="test",
                    aws_secret_access_key="test",
                    customer_id="schema-customer",
                )
                producer.bucket_name = "helix-bucket"

                analysis = {
                    "schema": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                    },
                    "field_emptiness": {"name": 0.0},
                    "record_count": 1,
                    "analysis_errors": 0,
                }

                payload = producer._build_dataset_payload(
                    dataset_name="Schema Dataset",
                    description="desc",
                    category="general",
                    data_freshness="daily",
                    s3_key="datasets/schema/data.ndjson",
                    final_size=256,
                    combined_metadata={"custom": True},
                    analysis=analysis,
                    dataset_overrides={"visibility": "restricted"},
                )

                schema_path = (
                    Path(__file__).resolve().parents[2]
                    / "schemas"
                    / "dataset.schema.json"
                )
                with open(schema_path, "r", encoding="utf-8") as fh:
                    dataset_schema = json.load(fh)

                for field in dataset_schema.get("required", []):
                    assert field in payload, f"Missing required field {field}"

                assert payload["visibility"] == "restricted"
                assert payload["metadata"]["schema"] == payload["schema"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
