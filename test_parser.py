from app.parser import parse_text

def test_basic_parse():
    sample = 'Vendor: Acme Ltd\nInvoice No.: INV-900\nDate: 2024-04-05\nTotal: $2,000.00\n'
    res = parse_text(sample)
    assert res['vendor'] is not None

