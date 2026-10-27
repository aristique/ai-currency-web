from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path
import hashlib
import os
import re
import tempfile
import threading
import urllib.request
import xml.etree.ElementTree as ET

SOURCE = "Национальный банк Молдовы (BNM)"
ENDPOINT = "https://www.bnm.md/en/official_exchange_rates?get_xml=1&date="


class RateError(Exception):
    pass


class EmptyRates(RateError):
    pass


@dataclass(frozen=True)
class RateSet:
    date: date
    rates: dict[str, Decimal]


def parse_xml(payload: bytes) -> RateSet:
    if len(payload) > 2_000_000:
        raise RateError("Ответ источника слишком большой.")
    try:
        root = ET.fromstring(payload)
        if root.tag != "ValCurs":
            raise ValueError("unexpected root")
        source_date = __import__("datetime").datetime.strptime(root.attrib["Date"], "%d.%m.%Y").date()
        rates = {"MDL": Decimal(1)}
        elements = root.findall("Valute")
        if not elements:
            raise EmptyRates("Источник не опубликовал курсы на эту дату.")
        for item in elements:
            code = (item.findtext("CharCode") or "").strip()
            nominal = Decimal((item.findtext("Nominal") or "").replace(",", "."))
            value = Decimal((item.findtext("Value") or "").replace(",", "."))
            if not re.fullmatch("[A-Z]{3}", code) or code in rates:
                raise ValueError("invalid or duplicate currency")
            if not nominal.is_finite() or not value.is_finite() or nominal <= 0 or value <= 0:
                raise ValueError("non-positive rate")
            rates[code] = value / nominal
        return RateSet(source_date, rates)
    except EmptyRates:
        raise
    except Exception as exc:
        raise RateError("Источник вернул некорректные данные курсов.") from exc


def amount_value(raw):
    try:
        value = Decimal(str(raw).strip().replace(",", "."))
    except InvalidOperation as exc:
        raise RateError("Введите положительную сумму числом.") from exc
    if not value.is_finite() or value <= 0 or value > Decimal("1e15"):
        raise RateError("Сумма должна быть больше нуля и не превышать 10¹⁵.")
    return value


def convert(raw, source, target, rates):
    amount = amount_value(raw)
    if source not in rates.rates or target not in rates.rates:
        raise RateError("Выберите валюты из доступного списка.")
    with localcontext() as context:
        context.prec = 50
        return (amount * rates.rates[source] / rates.rates[target]).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)


def parse_date(raw):
    try:
        parsed = date.fromisoformat(raw)
        if parsed.isoformat() != raw:
            raise ValueError()
        return parsed
    except (TypeError, ValueError) as exc:
        raise RateError("Укажите существующую дату в формате ГГГГ-ММ-ДД.") from exc


def download(day):
    try:
        request = urllib.request.Request(ENDPOINT + day.strftime("%d.%m.%Y"),
                                         headers={"User-Agent": "EducationalBNMConverter/1.0"})
        with urllib.request.urlopen(request, timeout=6) as response:
            payload = response.read(2_000_001)
        if len(payload) > 2_000_000:
            raise RateError("Ответ источника слишком большой.")
        return payload
    except RateError:
        raise
    except Exception as exc:
        raise RateError("Не удалось получить курс. Проверьте интернет или попробуйте позже.") from exc


class Store:
    def __init__(self, directory, fetcher=download):
        self.path = Path(directory) / "latest.xml"
        self.fetcher = fetcher
        self.snapshots = {}
        self.lock = threading.Lock()

    def cache_info(self):
        try:
            return parse_xml(self.path.read_bytes()).date.isoformat()
        except (OSError, RateError):
            return None

    def _remember(self, payload):
        rates = parse_xml(payload)
        key = hashlib.sha256(payload).hexdigest()
        with self.lock:
            if len(self.snapshots) >= 128:
                self.snapshots.clear()
            self.snapshots[key] = rates
        return key, rates

    def get(self, day=None, cached=False):
        day = day or date.today()
        warning = ""
        if cached:
            try:
                payload = self.path.read_bytes()
            except OSError as exc:
                raise RateError("Сохранённого курса пока нет. Сначала получите данные при наличии сети.") from exc
        else:
            for offset in range(15):
                actual_day = day - timedelta(days=offset)
                payload = self.fetcher(actual_day)
                try:
                    parsed = parse_xml(payload)
                except EmptyRates:
                    continue
                if parsed.date > day:
                    raise RateError("Источник вернул курс из будущего относительно выбранной даты.")
                break
            else:
                raise RateError("Нет доступного курса за выбранную дату и 14 предыдущих дней.")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = None
            try:
                handle, temporary = tempfile.mkstemp(dir=self.path.parent, prefix=".rates-", suffix=".tmp")
                with os.fdopen(handle, "wb") as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(stream.fileno())
                with self.lock:
                    os.replace(temporary, self.path)
                temporary = None
            except OSError as exc:
                raise RateError("Курс получен, но не удалось сохранить кэш. Проверьте папку данных.") from exc
            finally:
                if temporary:
                    Path(temporary).unlink(missing_ok=True)
        key, rates = self._remember(payload)
        if cached:
            warning = "Используется сохранённый курс. Его дата может отличаться от выбранной."
        elif rates.date != day:
            warning = f"На {day.isoformat()} курс недоступен. Использован последний найденный курс."
        return {"snapshot": key, "date": rates.date.isoformat(), "requestedDate": day.isoformat(),
                "cached": cached, "warning": warning, "source": SOURCE,
                "rates": {code: str(value) for code, value in sorted(rates.rates.items())}}

    def conversion(self, body):
        with self.lock:
            rates = self.snapshots.get(body.get("snapshot"))
        if rates is None:
            raise RateError("Сначала загрузите курс или выберите сохранённый.")
        source, target = body.get("from"), body.get("to")
        result = convert(body.get("amount", ""), source, target, rates)
        return {"amount": str(result), "from": source, "to": target,
                "date": rates.date.isoformat(), "source": SOURCE}
