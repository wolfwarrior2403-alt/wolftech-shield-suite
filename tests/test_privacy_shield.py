"""Privacy Shield: masking is consistent, catches Indian identifiers, reverses exactly, and stores nothing."""
import csv
import io
import zipfile

import pytest

from app.shield.mask import SAMPLE_CSV, MaskError, classify_header, mask_csv, unmask_text

REAL = ["Rajesh Patel", "rajesh.patel@gmail.com", "9876543210", "ABCPP1234K", "Meera Shah",
        "meera.shah@yahoo.in", "98250 11223", "2345 6789 0123", "Anil Desai"]


def test_no_real_value_survives():
    r = mask_csv(SAMPLE_CSV)
    for value in REAL:
        assert value.lower() not in r.masked_csv.lower(), value


def test_same_person_same_fake():
    rows = list(csv.DictReader(io.StringIO(mask_csv(SAMPLE_CSV).masked_csv)))
    assert rows[0]["client_name"] == rows[2]["client_name"] == "Person_0001"
    assert rows[0]["email"] == rows[2]["email"]
    assert rows[0]["client_name"] != rows[1]["client_name"]


def test_names_and_patterns_in_free_text():
    rows = list(csv.DictReader(io.StringIO(mask_csv(SAMPLE_CSV).masked_csv)))
    assert rows[0]["notes"].startswith("Person_0001 called")
    assert "9000000001" in rows[0]["notes"]           # same phone as the mobile column
    assert "Person_0003" in rows[3]["notes"] and "2345" not in rows[3]["notes"]


def test_non_personal_columns_untouched():
    rows = list(csv.DictReader(io.StringIO(mask_csv(SAMPLE_CSV).masked_csv)))
    assert rows[0]["city"] == "Ahmedabad"
    assert rows[0]["matter"] == "Trademark filing - class 30"


def test_round_trip_restores_exactly():
    r = mask_csv(SAMPLE_CSV)
    assert unmask_text(r.masked_csv, r.key_csv).strip() == SAMPLE_CSV.strip()


def test_unmask_ai_answer():
    r = mask_csv(SAMPLE_CSV)
    answer = "Call Person_0002 first, then email person0001@example.com."
    assert unmask_text(answer, r.key_csv) == "Call Meera Shah first, then email rajesh.patel@gmail.com."


def test_header_classification():
    assert classify_header("Client Name") == "name"
    assert classify_header("Mobile No") == "phone"
    assert classify_header("PAN") == "pan"
    assert classify_header("GSTIN") == "gstin"
    assert classify_header("Aadhar Number") == "aadhaar"
    assert classify_header("Trademark name") is None
    assert classify_header("File name") is None
    assert classify_header("Company name") is None


def test_detects_by_values_when_header_is_vague():
    data = "col_a,col_b\nx,someone@firm.in\ny,other@firm.in\n"
    r = mask_csv(data)
    assert r.columns["col_b"] == "email"
    assert "firm.in" not in r.masked_csv


def test_semicolon_and_bom():
    data = "﻿Name;Phone\nRavi Kumar;9123456789\n".encode("utf-8")
    r = mask_csv(data)
    assert "Ravi" not in r.masked_csv and "9123456789" not in r.masked_csv


def test_bad_inputs():
    with pytest.raises(MaskError):
        mask_csv("")
    with pytest.raises(MaskError):
        unmask_text("x", "not,a,key\n")


def test_fourteen_thousand_rows_fast():
    lines = ["name,email,phone"] + [f"Client {i},c{i}@mail.com,98{i:08d}" for i in range(14000)]
    r = mask_csv("\n".join(lines))
    assert r.rows == 14000
    assert "c13999@mail.com" not in r.masked_csv


# ---- web


def test_page(client):
    r = client.get("/privacy-shield")
    assert r.status_code == 200
    assert "Person_0001" in r.text and "<script" not in r.text and " style=" not in r.text


def test_mask_sample_download(client):
    r = client.post("/privacy-shield/mask", data={"use_sample": "yes"})
    assert r.status_code == 200 and r.headers["content-type"] == "application/zip"
    z = zipfile.ZipFile(io.BytesIO(r.content))
    assert set(z.namelist()) == {"masked.csv", "KEY-KEEP-PRIVATE.csv", "README.txt"}
    assert "Rajesh" not in z.read("masked.csv").decode()


def test_mask_upload_and_restore(client):
    up = client.post("/privacy-shield/mask", files={"file": ("c.csv", SAMPLE_CSV.encode(), "text/csv")})
    z = zipfile.ZipFile(io.BytesIO(up.content))
    masked, key = z.read("masked.csv"), z.read("KEY-KEEP-PRIVATE.csv")
    back = client.post("/privacy-shield/unmask", files={"file": ("masked.csv", masked, "text/csv"),
                                                         "key": ("key.csv", key, "text/csv")})
    assert back.status_code == 200
    assert back.text.strip() == SAMPLE_CSV.strip()


def test_public_demo_refuses_real_uploads(client, monkeypatch):
    monkeypatch.setenv("WOLFTECH_PUBLIC_DEMO", "1")
    r = client.post("/privacy-shield/mask", files={"file": ("c.csv", SAMPLE_CSV.encode(), "text/csv")})
    assert r.status_code == 400 and "only masks the built-in sample" in r.text
    assert client.post("/privacy-shield/mask", data={"use_sample": "yes"}).status_code == 200
    assert 'type="file"' not in client.get("/privacy-shield").text
