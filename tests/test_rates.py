from datetime import date
from decimal import Decimal
from unittest.mock import patch
import pytest

from currency.rates import Store, RateError, EmptyRates, amount_value, convert, parse_xml, parse_date

DAY = date(2026, 10, 28)


def xml(day=DAY, euro="20"):
    return f'<ValCurs Date="{day:%d.%m.%Y}"><Valute><CharCode>EUR</CharCode><Nominal>1</Nominal><Value>{euro}</Value></Valute><Valute><CharCode>JPY</CharCode><Nominal>100</Nominal><Value>12</Value></Valute></ValCurs>'.encode()


def test_parse_nominal_and_mdl():
    rates = parse_xml(xml())
    assert rates.date == DAY
    assert rates.rates == {"MDL": Decimal(1), "EUR": Decimal(20), "JPY": Decimal("0.12")}


@pytest.mark.parametrize("payload", [b"not xml", b"<html/>", xml(euro="NaN"),
                                     xml(euro="0"), xml(euro="-1"), b'<ValCurs Date="bad"/>'])
def test_bad_source_is_rejected(payload):
    with pytest.raises(RateError):
        parse_xml(payload)


def test_empty_source_is_distinct_from_malformed():
    with pytest.raises(EmptyRates):
        parse_xml(b'<ValCurs Date="28.10.2026"/>')


@pytest.mark.parametrize("value", ["", " ", "words", "0", "-1", "NaN", "Infinity", "1e16", None])
def test_invalid_amounts(value):
    with pytest.raises(RateError):
        amount_value(value)


def test_decimal_comma_bidirectional_and_same_currency():
    rates = parse_xml(xml())
    assert convert("10,5", "EUR", "MDL", rates) == Decimal("210.00")
    assert convert("210", "MDL", "EUR", rates) == Decimal("10.50")
    assert convert("10.5", "EUR", "EUR", rates) == Decimal("10.50")
    assert convert("100", "JPY", "MDL", rates) == Decimal("12.00")


def test_unknown_currency():
    with pytest.raises(RateError):
        convert("1", "BAD", "MDL", parse_xml(xml()))


def test_empty_day_falls_back_and_reports_actual_date(tmp_path):
    calls = []
    def fetch(day):
        calls.append(day)
        return b'<ValCurs Date="28.10.2026"/>' if day == DAY else xml(day)
    result = Store(tmp_path, fetch).get(DAY)
    assert result["date"] == "2026-10-27"
    assert result["requestedDate"] == "2026-10-28"
    assert result["warning"]
    assert len(calls) == 2


def test_cache_survives_new_instance_without_network(tmp_path):
    online = Store(tmp_path, lambda day: xml(day))
    online.get(DAY)
    def offline(_):
        raise RateError("Нет сети")
    restarted = Store(tmp_path, offline)
    with pytest.raises(RateError):
        restarted.get(DAY)
    cached = restarted.get(DAY, cached=True)
    assert cached["cached"]
    assert cached["date"] == DAY.isoformat()
    result = restarted.conversion({"snapshot": cached["snapshot"], "amount": "100",
                                    "from": "EUR", "to": "MDL"})
    assert result["amount"] == "2000.00"


def test_failed_fetch_keeps_last_successful_cache(tmp_path):
    store = Store(tmp_path, lambda day: xml(day))
    store.get(DAY)
    previous = store.path.read_bytes()
    store.fetcher = lambda _: b"broken"
    with pytest.raises(RateError):
        store.get(DAY)
    assert store.path.read_bytes() == previous


def test_failed_atomic_save_keeps_old_cache(tmp_path):
    store = Store(tmp_path, lambda day: xml(day))
    store.get(DAY)
    before = store.path.read_bytes()
    with patch("currency.rates.os.replace", side_effect=PermissionError):
        with pytest.raises(RateError):
            store.get(DAY)
    assert store.path.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.parametrize("raw", ["2026-02-31", "no-date", "20261028", ""])
def test_invalid_calendar_dates(raw):
    with pytest.raises(RateError):
        parse_date(raw)
