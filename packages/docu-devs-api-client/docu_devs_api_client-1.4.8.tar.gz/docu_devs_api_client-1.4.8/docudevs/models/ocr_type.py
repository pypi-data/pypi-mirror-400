from typing import Literal, cast

OcrType = Literal["AUTO", "DEFAULT", "EXCEL", "LOW", "NONE", "PREMIUM"]

OCR_TYPE_VALUES: set[OcrType] = {
    "AUTO",
    "DEFAULT",
    "EXCEL",
    "LOW",
    "NONE",
    "PREMIUM",
}


def check_ocr_type(value: str) -> OcrType:
    if value in OCR_TYPE_VALUES:
        return cast(OcrType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {OCR_TYPE_VALUES!r}")
