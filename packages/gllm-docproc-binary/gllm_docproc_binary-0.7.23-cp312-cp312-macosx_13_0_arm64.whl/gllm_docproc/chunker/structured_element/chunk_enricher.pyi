from gllm_docproc.model.element import Element as Element
from gllm_docproc.model.element_metadata import AUDIO as AUDIO, PDF as PDF, VIDEO as VIDEO

def enrich_chunk(chunk: Element, elements: list[Element]) -> Element:
    """Enrich the chunk with information from the original elements.

    This is the default enrichment function for structured element chunker.
    The function enrich the chunk with information from the original elements.
    Based on the source type, the information that we want to keep are different.

    Args:
        chunk (Element): The chunk to be enriched.
        elements (list[Element]): The original elements that form the chunk.

    Returns:
        Element: The enriched chunk.
    """
def enrich_pdf_chunk(chunk: Element, elements: list[Element]) -> Element:
    """The default function for enriching the PDF chunk.

    The function enriches the PDF chunk with the coordinates and page_number information
    of the original elements.

    Args:
        chunk (Element): The PDF chunk to be enriched.
        elements (list[Element]): The original elements that form the chunk.

    Returns:
        Element: The enriched PDF chunk.
    """
def enrich_audio_chunk(chunk: Element, elements: list[Element]) -> Element:
    """The default function for enriching the audio chunk.

    The function enriches the audio chunk by replacing the double newlines with a single newline.
    Then, it adds the start_time, end_time, and lang_id information of the original elements.

    Args:
        chunk (Element): The audio chunk to be enriched.
        elements (list[Element]): The original elements that form the chunk.

    Returns:
        Element: The enriched audio chunk.
    """
