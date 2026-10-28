"""Sinh bộ dữ liệu kiểm thử TD-* (Test_Case_Specification §2) thành file thật để test trên giao diện.
Mỗi mã TD một thư mục con, giữ đúng tên file như trong ca kiểm thử (vd. TD-03/hop_dong.pdf).

Chạy: `cd backend && uv run python -m tests.make_test_data <thư-mục-đích>` (mặc định ./data/test-data).
Toàn bộ là dữ liệu tổng hợp, không nhạy cảm.
"""

import sys
from pathlib import Path

from tests.pdfs import make_blank_pdf, make_corrupt_pdf, make_encrypted_pdf, make_pdf

CONTRACT = [
    "Service contract between Company A and Company B. Duration is twenty four months.",
    "Scope of work includes deployment training and support.",
    "Payment terms: the customer pays within thirty days after receiving the invoice. Late payment interest applies.",
]

FILES: dict[str, bytes] = {
    "TD-01/hop_dong_A.pdf": make_pdf(CONTRACT),
    "TD-02/bao_cao.pdf": make_pdf(["Quarter report revenue", "Second page"]),
    "TD-03/hop_dong.pdf": make_pdf(["Contract text"]),
    "TD-04/a.pdf": make_pdf(["alpha"]),
    "TD-04/b.pdf": make_pdf(["beta"]),
    "TD-05/ghi_chu.txt": b"plain text, not a pdf",
    "TD-06/anh.pdf": b"\x89PNG\r\n\x1a\n" + b"\x00" * 32,
    "TD-07/mat_khau.pdf": make_encrypted_pdf(["secret contract"]),
    "TD-07b/hop_dong_A_khoa.pdf": make_encrypted_pdf(CONTRACT),
    "TD-08/hong.pdf": make_corrupt_pdf(),
    "TD-09/scan.pdf": make_blank_pdf(3),
    "TD-10/ten_pages.pdf": make_pdf([" ".join(f"page{n}word{i}" for i in range(60)) for n in range(1, 11)]),
    "TD-11/other.pdf": make_pdf(["Unrelated marketing brochure about coffee machines"]),
    "TD-12/x.pdf": make_pdf(["some text"]),
}


def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name, data in FILES.items():
        (out / name).parent.mkdir(parents=True, exist_ok=True)
        (out / name).write_bytes(data)
    print(f"Đã sinh {len(FILES)} file vào {out.resolve()}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/test-data"))
