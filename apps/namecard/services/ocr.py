# -*- encoding: utf-8 -*-

import abc
import logging

logger = logging.getLogger(__name__)


class OCREngine(abc.ABC):
    """Abstract base class for OCR engines."""

    @abc.abstractmethod
    def extract_text(self, image_path):
        """Extract text from an image file. Returns raw text string."""
        pass


class TesseractOCR(OCREngine):
    """OCR using Tesseract via pytesseract."""

    def __init__(self, tesseract_cmd=None, lang='eng+chi_tra+jpn'):
        import pytesseract
        if tesseract_cmd and tesseract_cmd != 'tesseract':
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.pytesseract = pytesseract
        self.lang = lang

    def extract_text(self, image_path):
        from PIL import Image
        logger.info(f"Running Tesseract OCR on: {image_path}")
        image = Image.open(image_path)
        text = self.pytesseract.image_to_string(image, lang=self.lang)
        logger.info(f"OCR extracted {len(text)} characters")
        return text.strip()


def get_ocr_engine(engine_type='tesseract', **kwargs):
    """Factory function to get an OCR engine instance."""
    if engine_type == 'tesseract':
        return TesseractOCR(**kwargs)
    raise ValueError(f"Unknown OCR engine: {engine_type}")
