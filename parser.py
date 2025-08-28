import re
from typing import Dict, Optional

DATE_PATTERNS = [r'(\d{4}-\d{2}-\d{2})', r'(\d{2}/\d{2}/\d{4})', r'(\d{1,2} \w{3,9} \d{4})']
AMOUNT_PATTERNS = [r'\bTotal\s*[:\-]?\s*([\$₹£]?\s*[0-9,]+(?:\.[0-9]{2})?)', r'\bAmount\s*[:\-]?\s*([\$₹£]?\s*[0-9,]+(?:\.[0-9]{2})?)', r'([\$₹£]\s*[0-9,]+(?:\.[0-9]{2})?)']
INVOICE_PATTERNS = [r'Invoice\s*No\.?\:?\s*([\w\-/]+)', r'Inv\.?\s*#\s*([\w\-/]+)', r'Invoice\s*#\s*([\w\-/]+)']
VENDOR_PATTERNS = [r'From:\s*(.+)', r'Vendor:\s*(.+)', r'Bill To:\s*(.+)']

def _first_regex_match(patterns, text):
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            for g in m.groups():
                if g:
                    return g.strip()
            return m.group(0).strip()
    return None


def normalize_amount(amount_str: Optional[str]) -> Optional[str]:
    if not amount_str:
        return None
    s = amount_str.replace('\xa0', ' ').strip()
    s = re.sub(r'[^0-9.,₹$£]', '', s)
    s = s.replace(',', '')
    return s if s else None


def parse_text(text: str) -> Dict[str, Optional[str]]:
    if not text:
        return {"vendor": None, "invoice_no": None, "date": None, "total": None}
    text = str(text)
    norm = re.sub(r'\r\n?', '\n', text)
    norm = re.sub(r'\t', ' ', norm)
    norm = re.sub(r' +', ' ', norm)
    vendor = _first_regex_match(VENDOR_PATTERNS, norm)
    invoice_no = _first_regex_match(INVOICE_PATTERNS, norm)
    date = _first_regex_match(DATE_PATTERNS, norm)
    total_raw = _first_regex_match(AMOUNT_PATTERNS, norm)
    total = normalize_amount(total_raw)
    return {"vendor": vendor, "invoice_no": invoice_no, "date": date, "total": total}
