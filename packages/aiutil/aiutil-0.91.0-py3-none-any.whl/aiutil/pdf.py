"""Manipulating PDFs."""

import datetime
from pathlib import Path
import re
import time
from typing import Iterable
from pypdf import PdfWriter, PdfReader
import pdfplumber

FMT = "%Y%m%d"


def extract_pages(file: str, subfiles: dict[str, int | Iterable[int]]) -> None:
    """Extract pages from a PDF file and write into sub PDF file.

    :param file: The raw PDF file to extract pages from.
    :param subfiles: A dictionary specifying sub PDF files
        and their corresponding indexes (0-based) of pages from the raw PDF file.
        For example,
        the following code extract pages 0-4 as first.pdf,
        pages 5 and 7 as second.pdf,
        and page 6 as third.pdf from raw.pdf.
        .. highlight:: python
        .. code-block:: python

        from aiutil.pdf import extract_pages
        extract_pages("raw.pdf", {"first.pdf": range(5), "second.pdf": [5, 7], "third.pdf": 6})
    """
    with open(file, "rb") as fin:
        reader = PdfReader(fin)
        for subfile, indexes in subfiles.items():
            _extract_pages(reader, indexes, subfile)


def _extract_pages(
    reader: PdfReader, indexes: int | Iterable[int], output: str
) -> None:
    """A helper function for extract_pages.

    :param reader: A PdfFileReader object.
    :param indexes: Index (0-based) of pages to extract.
    :param output: The path of the sub PDF file to write the extracted pages to.
    """
    writer = PdfWriter()
    if isinstance(indexes, int):
        indexes = [indexes]
    for index in indexes:
        writer.add_page(reader.pages[index])
    with open(output, "wb") as fout:
        writer.write(fout)


def extract_text_first_page(path: str | Path) -> str:
    """Extract the text of the first page of a PDF file.

    :param path: The path of the PDF file.
    :return: The text of the first page.
    """
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[0]
        return page.extract_text()


def _rename_puget_sound_energy(path: Path, text_first_page: str) -> Path:
    pattern = r"Issued: (\w+ \d{1,2}, \d{4})"
    m = re.search(pattern, text_first_page)
    if not m:
        raise RuntimeError(
            f"The pattern {pattern} is not found on the first page of the PDF bill."
        )
    date = datetime.datetime.strptime(m.group(1), "%B %d, %Y").strftime(FMT)
    path_new = path.with_name(f"pse_{date}.pdf")
    path.rename(path_new)
    return path_new


def _rename_bellevue_water(path: Path, text_first_page: str) -> Path:
    pattern = r"Bill Date: (\d{1,2}/\d{1,2}/\d{4})"
    m = re.search(pattern, text_first_page)
    if not m:
        raise RuntimeError(
            f"The pattern {pattern} is not found on the first page of the PDF bill."
        )
    date = datetime.datetime.strptime(m.group(1), "%m/%d/%Y").strftime(FMT)
    path_new = path.with_name(f"bellevue_water_{date}.pdf")
    path.rename(path_new)
    return path_new


def rename(pdf: str | Path) -> Path:
    """Rename a PDF file automatically based on its content.

    :param pdf: The path of the PDF file.
    :return: The path of the renamed PDF file.
    """
    if isinstance(pdf, str):
        pdf = Path(pdf)
    text = extract_text_first_page(pdf)
    pdf_new = pdf
    if "Puget Sound Energy" in text:
        pdf_new = _rename_puget_sound_energy(pdf, text)
    elif "MyUtilityBill.bellevuewa.gov" in text:
        pdf_new = _rename_bellevue_water(pdf, text)
    print(f"{pdf} ==> {pdf_new}")
    return pdf_new


def rename_dir(
    dir_: str | Path, seconds_wait: float = 0.1, seconds_total: float = 3600
):
    if isinstance(dir_, str):
        dir_ = Path(dir_)
    processed = set()
    time_begin = time.time()
    while True:
        if time.time() - time_begin > seconds_total:
            break
        time.sleep(seconds_wait)
        for path in dir_.iterdir():
            if path in processed:
                continue
            if path.suffix.lower() == ".pdf":
                processed.add(rename(path))
