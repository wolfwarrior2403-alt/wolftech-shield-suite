"""MCP server: the four tools are registered and return structured, cited results."""
import asyncio
import json

import pytest

import mcp_server
from app.compliance.documents import DOC_SLUGS
from app.rules.base import DISCLAIMER


@pytest.fixture(autouse=True)
def demo_db(client):
    """The client fixture gives a fresh in-memory database with the demo firm."""


def test_exactly_the_four_tools_are_exposed():
    tools = asyncio.run(mcp_server.mcp.list_tools())
    assert sorted(t.name for t in tools) == ["assess_readiness", "generate_document", "list_gaps", "run_health_check"]
    assert all(t.description for t in tools)


def test_tools_work_over_the_mcp_call_path():
    result = asyncio.run(mcp_server.mcp.call_tool("assess_readiness", {}))
    payload = json.dumps(result, default=lambda o: getattr(o, "model_dump", lambda: str(o))())
    assert "Sample Law Associates" in payload and DISCLAIMER in payload


def test_assess_readiness():
    out = mcp_server.assess_readiness()
    assert out["firm"] == "Sample Law Associates" and 20 <= out["score"] <= 60
    assert out["gaps"] > 0 and out["disclaimer"] == DISCLAIMER
    assert [d["date"] for d in out["deadlines"]] == ["2025-11-13", "2026-11-13", "2027-05-13"]
    assert out["workspaces"][0]["demo"] is True


def test_list_gaps_are_cited_and_prioritised():
    out = mcp_server.list_gaps(limit=5)
    assert len(out["gaps"]) == 5 and out["total_gaps"] > 5
    assert out["gaps"][0]["priority"] == "High"
    for gap in out["gaps"]:
        assert gap["rule_id"].startswith("DPDP-") and gap["citation"] and gap["fix"]
        assert gap["source_url"].startswith("https://")


@pytest.mark.parametrize("slug", DOC_SLUGS)
def test_generate_document(slug):
    out = mcp_server.generate_document(slug)
    assert DISCLAIMER in out["text"] and "Sample Law Associates" in out["text"]
    assert out["rules_cited"] and "Sources" in out["text"]


def test_generate_document_saves_pdf(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    out = mcp_server.generate_document("Privacy Notice", save_pdf=True)
    with open(out["pdf_path"], "rb") as fh:
        assert fh.read(4) == b"%PDF"


def test_generate_document_rejects_unknown():
    with pytest.raises(ValueError):
        mcp_server.generate_document("will")


def test_run_health_check_ranks_fixes_and_cites():
    out = mcp_server.run_health_check()
    efforts = [f["effort"] for f in out["fixes_easiest_first"]]
    assert efforts == sorted(efforts, key=["Low", "Medium", "High"].index)
    assert all(f["source_url"].startswith("https://www.cert-in.org.in/") for f in out["fixes_easiest_first"])
    assert out["domain_check"]["domain"] == "samplelaw.example"


def test_run_health_check_refuses_domain_without_confirmation():
    out = mcp_server.run_health_check(domain="firm.in")
    assert "confirm" in out["domain_check_refused"]
    assert out["domain_check"]["domain"] == "samplelaw.example"      # nothing new was run or stored


def test_unknown_workspace():
    with pytest.raises(ValueError):
        mcp_server.assess_readiness(firm_id=999)
