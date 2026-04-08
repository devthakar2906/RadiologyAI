import json
import re
from pathlib import Path
from urllib.parse import quote_plus, urljoin

import httpx

from app.core.config import get_settings


settings = get_settings()
TEMPLATE_CACHE_DIR = Path(settings.template_cache_dir)
_memory_cache: dict[str, dict] = {}


def _slugify(study_type: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (study_type or "general_radiology").lower()).strip("_") or "general_radiology"


def _cache_path(study_type: str) -> Path:
    return TEMPLATE_CACHE_DIR / f"{_slugify(study_type)}.json"


def _fallback_template(study_type: str, findings: str = "") -> dict:
    descriptor = f"{study_type} radiology report".strip()
    text = (findings or "").lower()

    if "brain" in descriptor.lower() or any(keyword in text for keyword in ["intracranial", "ventricle", "hemorrhage"]):
        return {
            "Technique": "Not mentioned",
            "Findings": {
                "Brain Parenchyma": "Not mentioned",
                "Ventricles and Cisterns": "Not mentioned",
                "Calvarium and Extra-axial Spaces": "Not mentioned",
            },
            "Impression": "Not mentioned",
        }

    if "spine" in descriptor.lower() or any(keyword in text for keyword in ["vertebral", "disc", "facet", "spinal canal"]):
        return {
            "Technique": "Not mentioned",
            "Alignment & Curvature": "Not mentioned",
            "Vertebral Bodies": "Not mentioned",
            "Intervertebral Discs": "Not mentioned",
            "Spinal Canal & Nerves": "Not mentioned",
            "Facet Joints": "Not mentioned",
            "Impression": "Not mentioned",
        }

    return {
        "Technique": "Not mentioned",
        "Findings": {
            "Primary Findings": "Not mentioned",
            "Ancillary Findings": "Not mentioned",
        },
        "Impression": "Not mentioned",
    }


def _extract_sections_from_html(html_text: str) -> list[str]:
    headings = re.findall(r"<h[1-4][^>]*>(.*?)</h[1-4]>", html_text, flags=re.IGNORECASE | re.DOTALL)
    cleaned: list[str] = []
    skip_words = {
        "radreport",
        "search",
        "menu",
        "home",
        "template",
        "templates",
        "download",
        "print",
        "report",
    }
    for heading in headings:
        text = re.sub(r"<[^>]+>", " ", heading)
        text = re.sub(r"&nbsp;?", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+", " ", text).strip(" :-\n\r\t")
        if not text:
            continue
        normalized = text.lower()
        if normalized in skip_words:
            continue
        if any(word in normalized for word in ["copyright", "license", "rsna"]):
            continue
        if len(text) > 45:
            continue
        if text not in cleaned:
            cleaned.append(text)
    return cleaned


def _template_from_sections(study_type: str, sections: list[str]) -> dict:
    if not sections:
        return _fallback_template(study_type)

    template: dict = {}
    findings_bucket: dict[str, str] = {}
    for section in sections:
        normalized = section.lower()
        if normalized in {"technique", "comparison", "impression", "recommendation", "recommendations"}:
            template[section] = "Not mentioned"
            continue
        findings_bucket[section] = "Not mentioned"

    if findings_bucket and "Findings" not in template:
        template["Findings"] = findings_bucket

    if "Technique" not in template:
        template = {"Technique": "Not mentioned", **template}
    if "Impression" not in template:
        template["Impression"] = "Not mentioned"

    return template


async def _search_radreport(study_type: str) -> tuple[dict | None, str | None]:
    search_url = f"{settings.radreport_base_url}/?s={quote_plus(study_type)}"
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        search_response = await client.get(search_url)
        search_response.raise_for_status()
        search_html = search_response.text

        candidate_links = re.findall(r'href="([^"]+)"', search_html, flags=re.IGNORECASE)
        for href in candidate_links:
            if "radreport.org" not in href and not href.startswith("/"):
                continue
            if any(token in href.lower() for token in ["license", ".pdf", "/wp-", "/feed", "#"]):
                continue

            template_url = urljoin(settings.radreport_base_url, href)
            template_response = await client.get(template_url)
            if template_response.status_code >= 400:
                continue

            sections = _extract_sections_from_html(template_response.text)
            if not sections:
                continue
            return _template_from_sections(study_type, sections), template_url

    return None, None


async def get_template(study_type: str, findings: str = "") -> tuple[dict, str]:
    cache_key = _slugify(study_type)
    if cache_key in _memory_cache:
        return _memory_cache[cache_key], "cache:memory"

    cache_file = _cache_path(study_type)
    if cache_file.exists():
        template = json.loads(cache_file.read_text(encoding="utf-8"))
        _memory_cache[cache_key] = template
        return template, f"cache:{cache_file.name}"

    try:
        template, source_url = await _search_radreport(study_type)
    except Exception:
        template, source_url = None, None

    if template is None:
        template = _fallback_template(study_type, findings=findings)
        source_url = "fallback"

    cache_file.write_text(json.dumps(template, indent=2, ensure_ascii=False), encoding="utf-8")
    _memory_cache[cache_key] = template
    return template, source_url or "fallback"
