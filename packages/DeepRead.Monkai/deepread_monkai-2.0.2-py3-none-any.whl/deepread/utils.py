# ============================================================================
# DEEPREAD UTILS - UTILITÁRIOS
# ============================================================================
"""
Funções utilitárias do DeepRead.
"""

import unicodedata
import re
from pathlib import Path
from typing import List, Tuple, Optional
import fitz


def normalize_text(text: str) -> str:
    """Remove acentos e converte para lowercase."""
    text_normalized = unicodedata.normalize('NFD', text)
    text_without_accents = ''.join(c for c in text_normalized if unicodedata.category(c) != 'Mn')
    return text_without_accents.lower()


def clean_text(text: str) -> str:
    """Remove caracteres especiais mantendo apenas alfanuméricos e espaços."""
    return re.sub(r'[^a-zA-Z0-9\s]', ' ', text)


def load_pdf(pdf_path: Path) -> list:
    """
    Carrega um PDF e retorna lista de documentos (páginas).
    
    Args:
        pdf_path: Caminho do arquivo PDF
        
    Returns:
        Lista de Document objects
    """
    from llama_index.readers.file import PDFReader
    pdf_reader = PDFReader()
    return pdf_reader.load_data(file=pdf_path)


def filter_relevant_pages(
    documents: list, 
    keywords: list
) -> Tuple[list, dict]:
    """
    Filtra páginas que contêm pelo menos uma keyword.
    
    Args:
        documents: Lista de documentos (páginas)
        keywords: Lista de keywords para filtrar
        
    Returns:
        Tuple: (páginas filtradas, info dict)
    """
    if not keywords:
        return documents, {"total": len(documents), "filtered": len(documents)}
    
    keywords_normalized = [normalize_text(kw) for kw in keywords]
    filtered_pages = []
    
    for doc in documents:
        text_normalized = normalize_text(doc.text)
        for keyword in keywords_normalized:
            if keyword in text_normalized:
                filtered_pages.append(doc)
                break
    
    return filtered_pages, {
        "total": len(documents),
        "filtered": len(filtered_pages)
    }


def list_documents(directory: Path, extension: str = ".pdf") -> List[Path]:
    """Lista todos os PDFs em um diretório."""
    if not directory.exists():
        return []
    return sorted([f for f in directory.iterdir() if f.suffix.lower() == extension])


def get_document_metadata(pdf_path: Path) -> dict:
    """
    Obtém metadados do documento PDF.
    
    Args:
        pdf_path: Caminho do arquivo
        
    Returns:
        Dict com tipo, páginas e tamanho
    """
    size_bytes = pdf_path.stat().st_size
    size_kb = round(size_bytes / 1024, 2)
    
    try:
        doc = fitz.open(pdf_path)
        num_pages = doc.page_count
        
        total_chars = 0
        for page_num in range(num_pages):
            page = doc.load_page(page_num)
            total_chars += len(page.get_text().strip())
        
        doc.close()
        
        avg_chars = total_chars / max(num_pages, 1)
        doc_type = "text" if avg_chars >= 100 else "image"
        
    except Exception:
        num_pages = 0
        doc_type = "unknown"
    
    return {
        "doc_type": doc_type,
        "num_pages": num_pages,
        "size_kb": size_kb
    }


def needs_ocr(pdf_path: Path, min_chars_per_page: int = 100) -> bool:
    """
    Verifica se um PDF precisa de OCR.
    
    Args:
        pdf_path: Caminho do arquivo
        min_chars_per_page: Mínimo de caracteres para considerar página com texto
        
    Returns:
        True se precisa de OCR
    """
    try:
        doc = fitz.open(pdf_path)
        total_chars = 0
        num_pages = doc.page_count
        
        for page_num in range(num_pages):
            page = doc.load_page(page_num)
            total_chars += len(page.get_text().strip())
        
        doc.close()
        
        avg_chars = total_chars / max(num_pages, 1)
        return avg_chars < min_chars_per_page
        
    except Exception:
        return True


def extract_main_response(result) -> str:
    """
    Extrai resposta formatada de um resultado Pydantic.
    
    Args:
        result: Objeto de resultado (Pydantic model)
        
    Returns:
        String formatada da resposta
    """
    if result is None:
        return "Sem resposta"
    
    # Método customizado
    if hasattr(result, 'get_main_response'):
        return result.get_main_response()
    
    # Fallback: converter para string
    if hasattr(result, 'model_dump'):
        data = result.model_dump()
        return " | ".join([f"{k}: {v}" for k, v in data.items() if not k.startswith("_")])
    
    return str(result)
