from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from dirty_equals import Contains, IsPartialDict
from litestar import Litestar
from litestar.testing import TestClient


@dataclass
class SearchExample:
    """A search test example with query and expected results.

    Attributes:
        query: The search query to send to the API.
        expected_records: A list of expected records, where each record is a
            sub-dictionary that should match at least one record in the results.
        unexpected_records: A list of records that should NOT appear in the
            search results. Each record is a sub-dictionary that must not match
            any record in the results.
    """

    query: dict
    expected_records: list[dict] = field(default_factory=list)
    unexpected_records: list[dict] = field(default_factory=list)


def get_record_by_id(
    client: TestClient[Litestar],
    base_url: str,
    record_id: int | str,
) -> dict:
    """Fetch a record by ID and return the extracted record data.

    The API response is usually in the format { "ModelName": [ record ] }.
    This function extracts and returns the first record.
    """
    resp = client.get(f"{base_url}/{record_id}")
    assert resp.status_code == 200, (
        f"Failed to get record {record_id}: {resp.status_code} - {resp.text}"
    )
    # The response is usually in the format { "ModelName": [ record ] }
    # We take the first value's first element.
    return list(resp.json().values())[0][0]


def test_has(
    client: TestClient[Litestar],
    base_url: str,
    exist_records: list[int | str],
    non_exist_records: list[int | str],
) -> None:
    for record in exist_records:
        resp = client.head(f"{base_url}/{record}")
        assert resp.status_code == 204, (
            f"Record {record} should exist but got {resp.status_code}"
        )

    for record in non_exist_records:
        resp = client.head(f"{base_url}/{record}")
        assert resp.status_code == 404, (
            f"Record {record} should not exist but got {resp.status_code}"
        )


def test_get_by_id(
    client: TestClient[Litestar],
    base_url: str,
    exist_records: dict[int | str, dict],
    non_exist_records: list[int | str],
) -> None:
    for record, data in exist_records.items():
        resp = client.get(f"{base_url}/{record}")
        assert resp.status_code == 200, (
            f"Record {record} should exist but got {resp.status_code}"
        )
        assert resp.json() == data, (resp.json(), data)

    for record in non_exist_records:
        resp = client.get(f"{base_url}/{record}")
        assert resp.status_code == 404, (
            f"Record {record} should not exist but got {resp.status_code}"
        )


def test_create(
    client: TestClient[Litestar],
    base_url: str,
    create_examples: list[dict],
    compare_properties: Optional[list[str]] = None,
) -> list[int]:
    """Test creating records and return the created IDs."""
    created_ids = []
    for data in create_examples:
        resp = client.post(base_url, json=data)
        assert resp.status_code == 201, (
            f"Failed to create record: {resp.status_code} - {resp.text}"
        )
        assert isinstance(resp.json(), int), f"Expected ID as int, got {resp.json()}"
        id = resp.json()
        created_ids.append(id)

        if compare_properties is not None:
            record = get_record_by_id(client, base_url, id)
            expected = {prop: data[prop] for prop in compare_properties}
            assert record == IsPartialDict(expected), (
                f"Created record does not match expected properties. "
                f"Expected {expected}, got {record}"
            )

    return created_ids


def test_update(
    client: TestClient[Litestar],
    base_url: str,
    update_examples: dict[int | str, dict],
    compare_properties: Optional[list[str]] = None,
) -> None:
    for record_id, data in update_examples.items():
        resp = client.put(f"{base_url}/{record_id}", json=data)
        assert resp.status_code == 200, (
            f"Failed to update record {record_id}: {resp.status_code} - {resp.text}"
        )
        assert resp.json() == record_id, (
            f"Expected returned ID {record_id}, got {resp.json()}"
        )

        if compare_properties is not None:
            record = get_record_by_id(client, base_url, record_id)
            expected = {prop: data[prop] for prop in compare_properties}
            assert record == IsPartialDict(expected), (
                f"Updated record does not match expected properties. "
                f"Expected {expected}, got {record}"
            )


def test_search(
    client: TestClient[Litestar],
    base_url: str,
    search_examples: list[SearchExample],
) -> None:
    """Test search functionality.

    Args:
        client: The test client.
        base_url: The base URL for the API.
        search_examples: A list of SearchExample objects, each containing a query
            and expected records to verify in the search results.

    Note:
        Uses dirty-equals for ergonomic assertions. Each expected record is
        matched as a partial dictionary against the search results.
    """
    for example in search_examples:
        resp = client.post(f"{base_url}/q", json=example.query)
        assert resp.status_code == 200, (
            f"Failed to search: {resp.status_code} - {resp.text}"
        )
        result = resp.json()
        assert isinstance(result, dict), f"Expected dict response, got {type(result)}"

        # Extract records from the response (format: { "ModelName": [ records ] })
        records = list(result.values())[0] if result else []

        # Use dirty-equals Contains with IsPartialDict for ergonomic assertions
        for expected in example.expected_records:
            assert records == Contains(IsPartialDict(expected)), (
                f"Expected record {expected} not found in search results. "
                f"Got records: {records}"
            )

        # Verify unexpected records are NOT in the results
        for unexpected in example.unexpected_records:
            assert records != Contains(IsPartialDict(unexpected)), (
                f"Unexpected record {unexpected} was found in search results. "
                f"Got records: {records}"
            )
