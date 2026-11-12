"""Privacy Shield: mask personal data in a CSV before it goes to any AI tool.

How it works
- Columns are classified by their header (name, email, phone, PAN, Aadhaar,
  GSTIN, address, date of birth) and, as a fallback, by what their values look
  like.
- Every real value gets a fake one that is consistent: the same person is
  always Person_0007, the same email is always person0007@example.com. So
  joins, counts and duplicates still behave the same when you test with the
  masked file.
- Free-text columns (notes, descriptions) are scanned too: emails, phone
  numbers, PAN, Aadhaar and GSTIN patterns are replaced, and so is any name
  that appears in a name column.
- A separate key file maps every fake value back to the real one. The key
  never leaves the firm's machine. `unmask` uses it to restore real values in
  a masked file (or in an AI tool's output).

Deterministic and local. No network, no AI.
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field

MAX_BYTES = 10 * 1024 * 1024   # 10 MB
MAX_ROWS = 100_000

# Kinds of personal data, in the order they are tried.
KINDS = ("email", "phone", "pan", "aadhaar", "gstin", "dob", "name", "address")

HEADER_HINTS: dict[str, tuple[str, ...]] = {
    "email": ("email", "e-mail", "mail id", "mailid"),
    "phone": ("phone", "mobile", "contact no", "contact number", "whatsapp", "tel", "cell"),
    "pan": ("pan",),
    "aadhaar": ("aadhaar", "aadhar", "uid"),
    "gstin": ("gstin", "gst no", "gst number", "gst"),
    "dob": ("dob", "date of birth", "birth"),
    "name": ("name", "client", "customer", "patient", "applicant", "contact person", "owner"),
    "address": ("address", "street", "locality", "addr"),
}
# Header words that mean "not personal data" even if a hint matches (for example "file name").
NOT_PERSONAL = ("file", "company name", "firm name", "trademark", "brand", "product", "user name", "username")

RE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RE_PHONE = re.compile(r"(?<!\d)(?:\+?91[\s-]?|0)?[6-9]\d{4}[\s-]?\d{5}(?!\d)")
RE_PAN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
RE_AADHAAR = re.compile(r"(?<!\d)[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}(?!\d)")
RE_GSTIN = re.compile(r"\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b")
PATTERNS = {"email": RE_EMAIL, "gstin": RE_GSTIN, "pan": RE_PAN, "aadhaar": RE_AADHAAR, "phone": RE_PHONE}


class MaskError(ValueError):
    pass


def _norm(header: str) -> str:
    return re.sub(r"[_\s]+", " ", header.strip().lower())


def classify_header(header: str) -> str | None:
    h = _norm(header)
    if any(word in h for word in NOT_PERSONAL):
        return None
    for kind in KINDS:
        for hint in HEADER_HINTS[kind]:
            if kind in ("pan", "uid", "gst", "tel") or len(hint) <= 3:
                if re.search(rf"\b{re.escape(hint)}\b", h):
                    return kind
            elif hint in h:
                return kind
    return None


def classify_values(values: list[str]) -> str | None:
    """Fallback when the header says nothing: most non-empty values match one pattern."""
    sample = [v.strip() for v in values if v and v.strip()][:200]
    if not sample:
        return None
    for kind in ("email", "gstin", "pan", "aadhaar", "phone"):
        rx = PATTERNS[kind]
        hits = sum(1 for v in sample if rx.fullmatch(v))
        if hits >= max(1, int(0.8 * len(sample))):
            return kind
    return None


@dataclass
class Masker:
    """Keeps one consistent fake for each real value, per kind."""
    maps: dict[str, dict[str, str]] = field(default_factory=lambda: {k: {} for k in KINDS})
    counters: dict[str, int] = field(default_factory=lambda: {k: 0 for k in KINDS})

    def _next(self, kind: str) -> int:
        self.counters[kind] += 1
        return self.counters[kind]

    @staticmethod
    def _key(kind: str, value: str) -> str:
        v = value.strip()
        if kind in ("phone", "aadhaar"):
            digits = re.sub(r"\D", "", v)
            return digits[-10:] if kind == "phone" else digits
        if kind in ("email", "pan", "gstin", "name"):
            return v.lower() if kind in ("email", "name") else v.upper()
        return v

    def fake(self, kind: str, value: str) -> str:
        if not value or not value.strip():
            return value
        key = self._key(kind, value)
        known = self.maps[kind].get(key)
        if known:
            return known
        n = self._next(kind)
        made = {
            "name": f"Person_{n:04d}",
            "email": f"person{n:04d}@example.com",
            "phone": f"90000{n:05d}"[-10:],
            "pan": f"AAAPZ{n % 10000:04d}X",
            "aadhaar": f"9999 {n // 10000 % 10000:04d} {n % 10000:04d}",
            "gstin": f"24AAAPZ{n % 10000:04d}X1Z{n % 10}",
            "dob": "01-01-1990",
            "address": f"Address_{n:04d}, Sample City",
        }[kind]
        self.maps[kind][key] = made
        return made

    def scrub_text(self, text: str, names: list[tuple[re.Pattern, str]]) -> str:
        """Replace patterns and known names inside free text."""
        if not text:
            return text
        for kind in ("email", "gstin", "pan", "aadhaar", "phone"):
            text = PATTERNS[kind].sub(lambda m, k=kind: self.fake(k, m.group(0)), text)
        for rx, fake in names:
            text = rx.sub(fake, text)
        return text

    def key_rows(self, originals: dict[str, dict[str, str]]) -> list[list[str]]:
        rows = []
        for kind in KINDS:
            for key, fake in self.maps[kind].items():
                rows.append([fake, originals[kind].get(key, key), kind])
        return rows


@dataclass
class MaskResult:
    masked_csv: str
    key_csv: str
    columns: dict[str, str]          # header -> kind ("" if left as is / text-scrubbed)
    rows: int
    replaced: int
    preview_before: list[list[str]]
    preview_after: list[list[str]]
    headers: list[str]


def _decode(data: bytes) -> str:
    if len(data) > MAX_BYTES:
        raise MaskError(f"File is larger than {MAX_BYTES // (1024 * 1024)} MB. Split it and mask each part.")
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    raise MaskError("Could not read the file. Save it as CSV (UTF-8) and try again.")


def mask_csv(data: bytes | str, preview: int = 5) -> MaskResult:
    text = data if isinstance(data, str) else _decode(data)
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(io.StringIO(text), dialect))
    if not rows or not any(c.strip() for c in rows[0]):
        raise MaskError("The file is empty or has no header row.")
    headers, body = rows[0], rows[1:]
    if len(body) > MAX_ROWS:
        raise MaskError(f"More than {MAX_ROWS:,} rows. Split the file and mask each part.")
    width = len(headers)
    body = [(r + [""] * width)[:width] for r in body]

    kinds: list[str | None] = []
    for i, h in enumerate(headers):
        kinds.append(classify_header(h) or classify_values([r[i] for r in body]))

    masker = Masker()
    originals: dict[str, dict[str, str]] = {k: {} for k in KINDS}
    replaced = 0

    # Pass 1: structured columns.
    out = [list(r) for r in body]
    for i, kind in enumerate(kinds):
        if not kind:
            continue
        for r_in, r_out in zip(body, out):
            value = r_in[i]
            if value.strip():
                originals[kind].setdefault(Masker._key(kind, value), value.strip())
                new = masker.fake(kind, value)
                if new != value:
                    replaced += 1
                r_out[i] = new

    # Pass 2: free text in the other columns (longest names first so "Rajesh Patel" beats "Rajesh").
    names = sorted(((orig, masker.maps["name"][k]) for k, orig in originals["name"].items()),
                   key=lambda x: -len(x[0]))
    name_rx = [(re.compile(rf"\b{re.escape(orig)}\b", re.IGNORECASE), fake) for orig, fake in names if len(orig) >= 3]
    for i, kind in enumerate(kinds):
        if kind:
            continue
        for r_out in out:
            before = r_out[i]
            for k in PATTERNS:   # remember originals found in text, for the key file
                for m in PATTERNS[k].finditer(before):
                    originals[k].setdefault(Masker._key(k, m.group(0)), m.group(0))
            after = masker.scrub_text(before, name_rx)
            if after != before:
                replaced += 1
                r_out[i] = after

    masked = io.StringIO()
    w = csv.writer(masked, lineterminator="\n")
    w.writerow(headers)
    w.writerows(out)
    key = io.StringIO()
    kw = csv.writer(key, lineterminator="\n")
    kw.writerow(["fake_value", "real_value", "kind"])
    kw.writerows(masker.key_rows(originals))
    return MaskResult(
        masked_csv=masked.getvalue(), key_csv=key.getvalue(),
        columns={h: (k or "") for h, k in zip(headers, kinds)},
        rows=len(body), replaced=replaced,
        preview_before=body[:preview], preview_after=out[:preview], headers=headers,
    )


def unmask_text(text: str, key_csv: bytes | str) -> str:
    """Put real values back into any text (a masked CSV, or an AI tool's answer) using the key file."""
    key_text = key_csv if isinstance(key_csv, str) else _decode(key_csv)
    reader = csv.reader(io.StringIO(key_text))
    header = next(reader, None)
    if not header or [h.strip().lower() for h in header[:2]] != ["fake_value", "real_value"]:
        raise MaskError("That is not a Privacy Shield key file.")
    pairs = [(r[0], r[1]) for r in reader if len(r) >= 2 and r[0]]
    pairs.sort(key=lambda p: -len(p[0]))   # Person_0012 before Person_001
    if not pairs:
        return text
    rx = re.compile("|".join(re.escape(f) for f, _ in pairs))
    lookup = dict(pairs)
    return rx.sub(lambda m: lookup[m.group(0)], text)


SAMPLE_CSV = """client_name,email,mobile,pan,city,matter,notes
Rajesh Patel,rajesh.patel@gmail.com,9876543210,ABCPP1234K,Ahmedabad,Trademark filing - class 30,Rajesh Patel called about objection; call back on 9876543210
Meera Shah,meera.shah@yahoo.in,+91 98250 11223,BXZPS5678L,Surat,Trademark opposition,Send hearing notice to meera.shah@yahoo.in
Rajesh Patel,rajesh.patel@gmail.com,9876543210,ABCPP1234K,Ahmedabad,Copyright registration,Same client as row 1
Anil Desai,anil.d@outlook.com,9909012345,CDEPD4321M,Vadodara,Patent search,Aadhaar 2345 6789 0123 shared at intake by Anil Desai
"""


def main(argv: list[str] | None = None) -> int:
    """CLI: python -m app.shield.mask clients.csv  -> clients.masked.csv + clients.key.csv
             python -m app.shield.mask --unmask answer.txt clients.key.csv"""
    import argparse
    from pathlib import Path

    ap = argparse.ArgumentParser(prog="python -m app.shield.mask", description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("key", nargs="?")
    ap.add_argument("--unmask", action="store_true", help="restore real values using a key file")
    a = ap.parse_args(argv)
    src = Path(a.file)
    if a.unmask:
        if not a.key:
            ap.error("--unmask needs the key file")
        restored = unmask_text(src.read_text(encoding="utf-8-sig"), Path(a.key).read_bytes())
        dest = src.with_name(src.stem + ".unmasked" + src.suffix)
        dest.write_text(restored, encoding="utf-8")
        print(f"Restored real values -> {dest}")
        return 0
    result = mask_csv(src.read_bytes())
    masked = src.with_name(src.stem + ".masked.csv")
    key = src.with_name(src.stem + ".key.csv")
    masked.write_text(result.masked_csv, encoding="utf-8")
    key.write_text(result.key_csv, encoding="utf-8")
    print(f"{result.rows} rows, {result.replaced} values replaced.")
    print(f"Safe to share with AI tools: {masked}")
    print(f"KEEP PRIVATE (never share): {key}")
    for h, k in result.columns.items():
        print(f"  {h:<24} {k or 'text scanned'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
