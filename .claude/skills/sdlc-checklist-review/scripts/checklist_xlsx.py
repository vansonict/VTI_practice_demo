"""Đọc và điền checklist .xlsx (cột Status + Notes) chỉ bằng thư viện chuẩn Python.

  read <checklist.xlsx>                         in các dòng và giá trị Status hợp lệ
  fill <gốc.xlsx> <bản-sao.xlsx> <results.json> chép file gốc rồi ghi Status/Notes theo results.json
                                                 results.json: {"<số dòng>": ["Done", "ghi chú"], ...}

Giả định bố cục checklist trong References/: hàng 1 là tiêu đề; có cột "Status" và cột "Notes" (tên chứa "Note").
File gốc không bị sửa; định dạng, data validation, conditional formatting được giữ nguyên.
"""

import json
import re
import shutil
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
SHEET = "xl/worksheets/sheet1.xml"


def _shared_strings(z: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")) for si in root.findall("m:si", NS)]


def _cell_value(c: ET.Element, strings: list[str]) -> str:
    t = c.get("t")
    if t == "s":
        v = c.find("m:v", NS)
        return strings[int(v.text)] if v is not None and v.text else ""
    if t == "inlineStr":
        return "".join(x.text or "" for x in c.iter(f"{{{NS['m']}}}t"))
    v = c.find("m:v", NS)
    return v.text if v is not None and v.text else ""


def _rows(path: Path) -> tuple[dict[int, dict[str, str]], list[str]]:
    with zipfile.ZipFile(path) as z:
        strings = _shared_strings(z)
        xml = z.read(SHEET).decode("utf-8")
    root = ET.fromstring(xml)
    rows: dict[int, dict[str, str]] = {}
    for r in root.iter(f"{{{NS['m']}}}row"):
        rows[int(r.get("r"))] = {re.sub(r"\d+", "", c.get("r")): _cell_value(c, strings) for c in r.findall("m:c", NS)}
    m = re.search(r"<formula1>&quot;(.*?)&quot;</formula1>", xml)
    return rows, (m.group(1).split(",") if m else [])


def _columns(header: dict[str, str]) -> tuple[str, str]:
    status = next((k for k, v in header.items() if v.strip().lower() == "status"), None)
    notes = next((k for k, v in header.items() if "note" in v.lower()), None)
    if not status or not notes:
        sys.exit(f"Không tìm thấy cột Status/Notes ở hàng tiêu đề: {header}")
    return status, notes


def read(path: Path) -> None:
    rows, allowed = _rows(path)
    status, notes = _columns(rows[1])
    print(f"Status hợp lệ: {', '.join(allowed) or '(không có data validation)'}  |  cột Status={status}, Notes={notes}")
    for n in sorted(rows)[1:]:
        r = rows[n]
        fields = [v for k, v in sorted(r.items()) if k not in (status, notes) and v]
        print(f"[{n}] {' | '.join(fields)}  →  {r.get(status, '')}")


def _set(xml: str, ref: str, text: str) -> str:
    esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    new = f't="inlineStr"><is><t xml:space="preserve">{esc}</t></is></c>'
    # ô có giá trị (có thể là shared string) hoặc ô rỗng tự đóng
    pat_full = re.compile(rf'(<c r="{ref}"(?: s="\d+")?)(?: t="\w+")?>.*?</c>', re.S)
    pat_empty = re.compile(rf'(<c r="{ref}"(?: s="\d+")?)\s*/>')
    if pat_full.search(xml):
        return pat_full.sub(lambda m: f"{m.group(1)} {new}", xml, count=1)
    if pat_empty.search(xml):
        return pat_empty.sub(lambda m: f"{m.group(1)} {new}", xml, count=1)
    sys.exit(f"Không tìm thấy ô {ref} trong sheet (checklist có bố cục khác?)")


def fill(src: Path, dst: Path, results_path: Path) -> None:
    results: dict[str, list[str]] = json.loads(results_path.read_text(encoding="utf-8"))
    rows, allowed = _rows(src)
    status, notes = _columns(rows[1])
    for n, (st, _) in results.items():
        if allowed and st not in allowed:
            sys.exit(f"Dòng {n}: Status '{st}' không thuộc {allowed}")
        if int(n) not in rows:
            sys.exit(f"Dòng {n} không có trong checklist")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    with zipfile.ZipFile(src) as zin:
        xml = zin.read(SHEET).decode("utf-8")
        for n, (st, note) in results.items():
            xml = _set(xml, f"{status}{n}", st)
            xml = _set(xml, f"{notes}{n}", note)
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                zout.writestr(item, xml.encode("utf-8") if item.filename == SHEET else zin.read(item.filename))
    after, _ = _rows(dst)
    counts: dict[str, int] = {}
    for n in sorted(after)[1:]:
        counts[after[n].get(status, "")] = counts.get(after[n].get(status, ""), 0) + 1
    missing = [n for n in sorted(after)[1:] if str(n) not in results]
    print(f"Đã ghi {dst}: " + ", ".join(f"{k or '(trống)'}={v}" for k, v in sorted(counts.items())))
    if missing:
        print(f"Cảnh báo: chưa chấm các dòng {missing}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "read":
        read(Path(sys.argv[2]))
    elif len(sys.argv) == 5 and sys.argv[1] == "fill":
        fill(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
    else:
        sys.exit(__doc__)
