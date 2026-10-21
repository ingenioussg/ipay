from modules.settings.validation import account_errors, company_name_errors, country_errors, identifier_errors


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


def test_countries_need_at_least_one():
    assert country_errors(True, False) == {} and country_errors(False, True) == {} and country_errors(True, True) == {}
    assert "countries" in country_errors(False, False)


def test_company_name_and_account():
    assert "name" in company_name_errors(" A ")
    assert company_name_errors("Acme Pte Ltd") == {}
    assert account_errors("Ann", "ann@example.com", "longenough1", "longenough1") == {}
    e = account_errors("", "nope", "short", "short")
    assert set(e) == {"display_name", "email", "password"}
    assert "confirm" in account_errors("Ann", "ann@example.com", "longenough1", "different11")
