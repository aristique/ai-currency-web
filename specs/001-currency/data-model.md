# Data model
RateSet.date: datetime.date parsed from XML Date (DD.MM.YYYY).
RateSet.rates: dictionary of three-letter currency codes to finite positive Decimal values in MDL/unit; includes MDL=1.
Cache: the last successfully validated XML payload, atomically replaced in the mounted directory.
Fetch metadata: requested date, source date, cached boolean and human-readable warning.
Amount: finite Decimal greater than zero and at most 10^15.
A result is calculated from one immutable rate set: currency dates cannot be mixed.
