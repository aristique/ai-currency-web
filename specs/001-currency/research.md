# Source research
On 2026-10-28 actual HTTPS XML requests were checked for 28.10.2026, 27.10.2026 and 04.10.2026.
All returned ValCurs XML with 40 currencies and a Date attribute.
BNM endpoint: https://www.bnm.md/en/official_exchange_rates?get_xml=1&date=DD.MM.YYYY
Each Valute contains CharCode, Nominal and Value. Value must be divided by Nominal.
The tested Sunday returned a valid official rate set for that date: weekends cannot be assumed to return empty data.
No API key is needed. Historical requests make the same source suitable for Lab 4; request availability and gaps must still be handled.
