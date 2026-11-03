"""
Tests for restocking API endpoints.
"""
import pytest

import mock_data


@pytest.fixture(autouse=True)
def clear_submitted_orders():
    """Keep in-memory submitted orders isolated between tests."""
    mock_data.submitted_orders.clear()
    yield
    mock_data.submitted_orders.clear()


class TestRestockingEndpoints:
    """Test suite for restocking endpoints."""

    def test_demand_has_restocking_fields(self, client):
        data = client.get("/api/demand").json()
        assert len(data) == 9
        for d in data:
            assert isinstance(d["unit_cost"], (int, float))
            assert isinstance(d["current_stock"], int)
            assert isinstance(d["supplier"], str)
            assert isinstance(d["lead_time_days"], int)

    def test_recommendations_zero_budget(self, client):
        r = client.get("/api/restocking/recommendations?budget=0")
        assert r.status_code == 200
        data = r.json()
        assert data["items"] == []
        assert data["total_cost"] == 0
        assert data["lead_time_days"] == 0

    def test_recommendations_structure(self, client):
        data = client.get("/api/restocking/recommendations?budget=100000").json()
        for key in ["budget", "total_cost", "remaining_budget", "lead_time_days", "items"]:
            assert key in data
        assert len(data["items"]) > 0
        for item in data["items"]:
            for key in ["sku", "name", "trend", "current_demand", "forecasted_demand",
                        "current_stock", "shortfall", "quantity", "unit_cost",
                        "line_total", "supplier", "lead_time_days"]:
                assert key in item
            assert item["shortfall"] > 0
            assert 0 < item["quantity"] <= item["shortfall"]
            assert abs(item["line_total"] - item["quantity"] * item["unit_cost"]) < 0.01

    @pytest.mark.parametrize("budget", [1, 100, 1000, 5000, 20000, 1000000])
    def test_recommendations_total_within_budget(self, client, budget):
        data = client.get(f"/api/restocking/recommendations?budget={budget}").json()
        assert data["total_cost"] <= budget
        assert abs(data["remaining_budget"] - (budget - data["total_cost"])) < 0.01
        assert abs(sum(i["line_total"] for i in data["items"]) - data["total_cost"]) < 0.01

    def test_recommendations_priority_order(self, client):
        data = client.get("/api/restocking/recommendations?budget=1000000").json()
        rank = {"increasing": 0, "stable": 1, "decreasing": 2}
        keys = [(rank[i["trend"]], -i["shortfall"]) for i in data["items"]]
        assert keys == sorted(keys)
        assert data["items"][0]["trend"] == "increasing"

    def test_recommendations_lead_time_is_max(self, client):
        data = client.get("/api/restocking/recommendations?budget=1000000").json()
        assert data["lead_time_days"] == max(i["lead_time_days"] for i in data["items"])

    def test_recommendations_bigger_budget_more_items(self, client):
        counts = [
            len(client.get(f"/api/restocking/recommendations?budget={b}").json()["items"])
            for b in (500, 5000, 50000, 1000000)
        ]
        assert counts == sorted(counts)

    def test_recommendations_partial_last_item(self, client):
        full = client.get("/api/restocking/recommendations?budget=1000000").json()
        first = full["items"][0]
        budget = first["unit_cost"] * 10
        data = client.get(f"/api/restocking/recommendations?budget={budget}").json()
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 10

    def _order(self, client, sku="WDG-001", quantity=5, budget=10000, unit_cost=0.01):
        return client.post("/api/restocking/orders", json={
            "budget": budget,
            "items": [{"sku": sku, "name": "x", "quantity": quantity, "unit_cost": unit_cost}],
        })

    def test_create_order_success(self, client):
        r = self._order(client)
        assert r.status_code == 201
        order = r.json()
        assert order["status"] == "Submitted"
        assert order["lead_time_days"] == 7
        assert order["order_number"]
        assert order["expected_delivery"] > order["order_date"]
        # server-side cost, client unit_cost ignored
        assert order["items"][0]["unit_cost"] == 24.99
        assert abs(order["total_cost"] - 5 * 24.99) < 0.01

    def test_create_order_lead_time_max(self, client):
        r = client.post("/api/restocking/orders", json={"budget": 100000, "items": [
            {"sku": "WDG-001", "name": "a", "quantity": 1, "unit_cost": 1},
            {"sku": "GSK-203", "name": "b", "quantity": 1, "unit_cost": 1},
        ]})
        assert r.status_code == 201
        assert r.json()["lead_time_days"] == 14

    def test_created_order_appears_in_list_newest_first(self, client):
        first = self._order(client).json()
        second = self._order(client, sku="FLT-405").json()
        data = client.get("/api/restocking/orders").json()
        assert [o["id"] for o in data] == [second["id"], first["id"]]

    def test_list_orders_empty(self, client):
        assert client.get("/api/restocking/orders").json() == []

    def test_create_order_empty_items(self, client):
        r = client.post("/api/restocking/orders", json={"budget": 100, "items": []})
        assert r.status_code == 422

    @pytest.mark.parametrize("qty", [0, -3])
    def test_create_order_non_positive_quantity(self, client, qty):
        assert self._order(client, quantity=qty).status_code == 422

    def test_create_order_unknown_sku(self, client):
        r = self._order(client, sku="NOPE-000")
        assert r.status_code in (400, 404)

    def test_create_order_over_budget(self, client):
        r = self._order(client, quantity=100, budget=10)
        assert r.status_code == 400
        assert "budget" in r.json()["detail"].lower()
        assert client.get("/api/restocking/orders").json() == []


class TestRestockingValidation:
    """Input validation hardening."""

    @pytest.mark.parametrize("budget", ["nan", "inf", "-inf", "-1"])
    def test_recommendations_invalid_budget(self, client, budget):
        r = client.get(f"/api/restocking/recommendations?budget={budget}")
        assert r.status_code == 422

    @pytest.mark.parametrize("budget", [float("nan"), float("inf"), -1])
    def test_post_invalid_budget(self, client, budget):
        # httpx rejects nan/inf in json=, so send raw content
        import json
        body = json.dumps({"budget": budget, "items": [
            {"sku": "WDG-001", "name": "x", "quantity": 1, "unit_cost": 1}]})
        r = client.post("/api/restocking/orders", content=body,
                        headers={"Content-Type": "application/json"})
        assert r.status_code == 422

    def test_post_quantity_cap(self, client):
        r = client.post("/api/restocking/orders", json={"budget": 1e9, "items": [
            {"sku": "WDG-001", "name": "x", "quantity": 1_000_001, "unit_cost": 1}]})
        assert r.status_code == 422

    def test_post_duplicate_skus(self, client):
        r = client.post("/api/restocking/orders", json={"budget": 100000, "items": [
            {"sku": "WDG-001", "name": "x", "quantity": 1, "unit_cost": 1},
            {"sku": "WDG-001", "name": "x", "quantity": 2, "unit_cost": 1}]})
        assert r.status_code == 400
        assert client.get("/api/restocking/orders").json() == []

    def test_post_total_equal_budget_within_rounding(self, client):
        # 3 * 24.99 = 74.97; budget rounded down by under half a cent is accepted
        r = client.post("/api/restocking/orders", json={"budget": 74.966, "items": [
            {"sku": "WDG-001", "name": "x", "quantity": 3, "unit_cost": 1}]})
        assert r.status_code == 201
