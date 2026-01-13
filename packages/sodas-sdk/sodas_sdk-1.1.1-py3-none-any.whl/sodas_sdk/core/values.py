from enum import Enum


class ORIGIN_VALUES(str, Enum):
    EXISTING = "existing"
    APPENDING = "appending"
    # APPENDED = "appended"  # Uncomment if needed later


class BASIC_TYPE_VALUES(str, Enum):
    date = "date"
    celcius = "celcius"
    fahrent = "fahrent"
    mph = "mph"
    mps = "mps"
    inHg = "inHg"
    hPa = "hPa"
    inch = "in"
    mm = "mm"
    microgram = "microgram"


class MEASURE_VALUES(str, Enum):
    CONSTRAINT = "constraint"
    YDATA = "y-data"


class CONVERSION_VALUES(str, Enum):
    HTML = "html"
    PDF = "pdf"
