"""Statutory identifier formats (pure, no database)."""

from modules.settings.validation import identifier_errors


def test_uen_formats():
    assert identifier_errors({"sg.uen": "53012345D"}) == {}        # business: 8 digits + letter
    assert identifier_errors({"sg.uen": "201912345A"}) == {}       # local company: year + 5 digits + letter
    assert identifier_errors({"sg.uen": "T09LL0001B"}) == {}       # other entity
    assert identifier_errors({"sg.uen": "t09ll0001b"}) == {}       # case-insensitive input
    assert "sg.uen" in identifier_errors({"sg.uen": "12345"})
    assert "sg.uen" in identifier_errors({"sg.uen": "X09LL0001B"})


def test_cpf_submission_number():
    assert identifier_errors({"sg.cpf_csn": "201912345A-PTE-01"}) == {}
    assert identifier_errors({"sg.cpf_csn": "201912345APTE01"}) == {}
    assert "sg.cpf_csn" in identifier_errors({"sg.cpf_csn": "201912345A-PT-1"})


def test_blank_identifiers_allowed_and_my_ids_loose():
    assert identifier_errors({"sg.uen": "", "my.epf_employer_no": "  "}) == {}
    assert identifier_errors({"my.lhdn_employer_no": "E 1234567890"}) == {}
    assert "my.epf_employer_no" in identifier_errors({"my.epf_employer_no": "12#45"})
