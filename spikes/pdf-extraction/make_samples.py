"""Sinh bộ PDF mẫu cho spike T0.1 (không chứa dữ liệu thật).

Tạo trong ./samples:
  text_vi.pdf     5 trang tiếng Việt, mỗi trang có dấu "Trang N", trang 3 có bảng
  password.pdf    text_vi.pdf được mã hóa bằng mật khẩu người dùng
  corrupt.pdf     40% đầu của text_vi.pdf (file hỏng)
  scanned.pdf     3 trang chỉ có ảnh (không có lớp văn bản)
  fake.pdf        ảnh PNG đổi đuôi thành .pdf
  large.pdf       300 trang văn bản, để đo tốc độ
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

FONT_PATH = "C:/Windows/Fonts/arial.ttf"
OUT = Path(__file__).parent / "samples"

PARAGRAPHS = {
    1: "Hợp đồng dịch vụ số HD-2026-017 giữa Công ty A và Công ty B. Thời hạn hợp đồng là 24 tháng kể từ ngày ký.",
    2: "Điều khoản thanh toán: khách hàng thanh toán trong vòng 30 ngày kể từ ngày nhận hóa đơn. Thanh toán chậm bị tính lãi 1,5% mỗi tháng.",
    3: "Bảng doanh thu theo quý của dự án được trình bày dưới đây.",
    4: "Phạm vi công việc gồm triển khai, đào tạo người dùng và hỗ trợ vận hành trong 12 tháng.",
    5: "Điều khoản chấm dứt: mỗi bên được chấm dứt hợp đồng với thông báo trước 60 ngày.",
}


def styles():
    pdfmetrics.registerFont(TTFont("ArialVN", FONT_PATH))
    ss = getSampleStyleSheet()
    for name in ("Normal", "Heading2"):
        ss[name].fontName = "ArialVN"
    return ss


def build_text(path: Path, pages: int, ss) -> None:
    story = []
    for n in range(1, pages + 1):
        story.append(Paragraph(f"Trang {n}", ss["Heading2"]))
        story.append(Paragraph(PARAGRAPHS.get(n, f"Nội dung mẫu của trang {n}. " * 20), ss["Normal"]))
        if n == 3:
            story.append(Spacer(1, 12))
            table = Table([["Quý", "Doanh thu (tỷ đồng)"], ["Q1", "10,2"], ["Q2", "11,5"], ["Q3", "12,4"]])
            table.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), "ArialVN"), ("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
            story.append(table)
        if n < pages:
            story.append(PageBreak())
    SimpleDocTemplate(str(path), pagesize=A4).build(story)


def build_password(src: Path, dst: Path) -> None:
    writer = PdfWriter()
    for page in PdfReader(str(src)).pages:
        writer.add_page(page)
    writer.encrypt(user_password="matkhau123", owner_password="owner456")
    with dst.open("wb") as f:
        writer.write(f)


def build_scanned(path: Path) -> None:
    font = ImageFont.truetype(FONT_PATH, 28)
    images = []
    for n in range(1, 4):
        img = Image.new("RGB", (1240, 1754), "white")
        draw = ImageDraw.Draw(img)
        draw.text((80, 80), f"Trang {n} (bản scan)", fill="black", font=font)
        draw.text((80, 160), PARAGRAPHS[n][:60], fill="black", font=font)
        images.append(img)
    images[0].save(path, save_all=True, append_images=images[1:], resolution=150)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    ss = styles()
    text = OUT / "text_vi.pdf"
    build_text(text, 5, ss)
    build_password(text, OUT / "password.pdf")
    data = text.read_bytes()
    (OUT / "corrupt.pdf").write_bytes(data[: int(len(data) * 0.4)])
    build_scanned(OUT / "scanned.pdf")
    png = OUT / "_tmp.png"
    Image.new("RGB", (10, 10), "white").save(png)
    (OUT / "fake.pdf").write_bytes(png.read_bytes())
    png.unlink()
    build_text(OUT / "large.pdf", 300, ss)
    print("Đã tạo:", ", ".join(sorted(p.name for p in OUT.glob("*.pdf"))))


if __name__ == "__main__":
    main()
