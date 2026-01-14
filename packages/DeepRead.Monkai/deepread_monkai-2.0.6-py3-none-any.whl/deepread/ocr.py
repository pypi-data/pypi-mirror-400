# ============================================================================
# DEEPREAD OCR - EXTRAÇÃO DE TEXTO COM OCR
# ============================================================================
"""
Módulo OCR usando Azure AI Vision.
"""

import io
import logging
from pathlib import Path
from typing import List, Optional

import fitz

from .config import get_azure_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)


def render_page_as_image(doc: fitz.Document, page_num: int, dpi: int = 150) -> bytes:
    """Renderiza uma página como imagem PNG."""
    page = doc.load_page(page_num)
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    return pix.tobytes("png")


def perform_azure_ocr(image_bytes: bytes, image_format: str = "png") -> Optional[str]:
    """
    Realiza OCR usando Azure AI Vision.
    
    Args:
        image_bytes: Bytes da imagem
        image_format: Formato da imagem
        
    Returns:
        Texto extraído ou None
    """
    endpoint, key = get_azure_config()
    
    if not key:
        logger.warning("AZURE_AI_VISION_KEY não configurada!")
        return None
    
    MAX_RETRIES = 3
    MIN_DIM, MAX_DIM = 200, 16000
    
    for attempt in range(MAX_RETRIES):
        try:
            from azure.ai.vision.imageanalysis import ImageAnalysisClient
            from azure.ai.vision.imageanalysis.models import VisualFeatures
            from azure.core.credentials import AzureKeyCredential
            from PIL import Image
            
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            w, h = img.size
            
            if min(w, h) < MIN_DIM:
                return None
            
            if max(w, h) > MAX_DIM:
                scale = MAX_DIM / max(w, h)
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            
            fmt_map = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "bmp": "BMP"}
            out_buf = io.BytesIO()
            img.save(out_buf, format=fmt_map.get(image_format.lower(), "PNG"))
            
            client = ImageAnalysisClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(key)
            )
            
            result = client.analyze(
                image_data=out_buf.getvalue(),
                visual_features=[VisualFeatures.READ],
                language="pt"
            )
            
            text = ""
            if result.read:
                for block in result.read.blocks:
                    for line in block.lines:
                        text += line.text + "\n"
            
            return text.strip() if text.strip() else None
            
        except Exception as e:
            logger.error(f"Azure OCR tentativa {attempt + 1} falhou: {e}")
            if attempt < MAX_RETRIES - 1:
                import time
                time.sleep(5)
    
    return None


def load_pdf_with_ocr(pdf_path: Path, use_azure: bool = True) -> List:
    """
    Carrega PDF aplicando OCR nas páginas com imagem.
    
    Args:
        pdf_path: Caminho do arquivo
        use_azure: Se True, usa Azure OCR
        
    Returns:
        Lista de Document objects
    """
    from llama_index.core.schema import Document
    
    doc = fitz.open(pdf_path)
    documents = []
    
    logger.info(f"Processando PDF com OCR: {pdf_path.name} ({doc.page_count} páginas)")
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text().strip()
        
        if len(text) > 100:
            documents.append(Document(
                text=text,
                metadata={"page": page_num + 1, "source": "text"}
            ))
            continue
        
        logger.info(f"Renderizando página {page_num + 1} para OCR...")
        img_bytes = render_page_as_image(doc, page_num)
        
        ocr_text = perform_azure_ocr(img_bytes, "png") if use_azure else ""
        
        final_text = f"{text}\n\n{ocr_text}".strip()
        
        if final_text:
            documents.append(Document(
                text=final_text,
                metadata={"page": page_num + 1, "source": "ocr" if ocr_text else "text"}
            ))
            logger.info(f"Página {page_num + 1}: {len(final_text)} caracteres extraídos via OCR")
    
    doc.close()
    return documents


def process_pdf_smart(pdf_path: Path, min_chars: int = 100) -> List:
    """
    Processa PDF de forma inteligente, aplicando OCR quando necessário.
    
    Args:
        pdf_path: Caminho do arquivo
        min_chars: Mínimo de caracteres para considerar página com texto
        
    Returns:
        Lista de Document objects
    """
    from .utils import needs_ocr
    
    if needs_ocr(pdf_path, min_chars):
        logger.info(f"PDF {pdf_path.name} precisa de OCR")
        return load_pdf_with_ocr(pdf_path)
    else:
        from llama_index.readers.file import PDFReader
        return PDFReader().load_data(file=pdf_path)
