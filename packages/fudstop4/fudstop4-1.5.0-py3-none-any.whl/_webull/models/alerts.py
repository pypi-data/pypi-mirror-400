import pandas as pd


def _sanitize_float(value: object) -> float:
    if value in (None, "", "--", "—"):
        return 0.0
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("%", "")
    if not text or text in ("--", "—"):
        return 0.0
    try:
        return float(text)
    except (TypeError, ValueError):
        return 0.0


def _sanitize_int(value: object) -> int:
    if value in (None, "", "--", "—"):
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    text = str(value).strip().replace(",", "")
    if not text or text in ("--", "—"):
        return 0
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return 0


class AlertChanges:
    def __init__(self, data):
        self.ticker = [i.get("symbol") for i in data]
        self.alert_type = [_sanitize_int(i.get("alertType")) for i in data]

        raw_volume = [i.get("volume") for i in data]
        self.volume_present = [v not in (None, "", "--", "—") for v in raw_volume]
        self.volume = [_sanitize_float(v) for v in raw_volume]

        raw_change = [i.get("changeRatio") for i in data]
        self.change_ratio_present = [v not in (None, "", "--", "—") for v in raw_change]
        self.change_ratio = [round(_sanitize_float(v) * 100, 2) for v in raw_change]

        self.data_dict = {
            "ticker": self.ticker,
            "alert_type": self.alert_type,
            "volume": self.volume,
            "change_ratio": self.change_ratio,
            "volume_present": self.volume_present,
            "change_ratio_present": self.change_ratio_present,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)


class VolumeAlerts:
    def __init__(self, data):
        self.ticker = [i.get("ticker") for i in data]
        self.alert = [i.get("alert") for i in data]
        self.alert_type = [_sanitize_int(i.get("alert_type")) for i in data]
        self.volume = [_sanitize_float(i.get("volume")) for i in data]

        self.data_dict = {
            "ticker": self.ticker,
            "alert": self.alert,
            "alert_type": self.alert_type,
            "volume": self.volume,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)


class ChangeAlerts:
    def __init__(self, data):
        self.ticker = [i.get("ticker") for i in data]
        self.alert = [i.get("alert") for i in data]
        self.alert_type = [_sanitize_int(i.get("alert_type")) for i in data]
        self.change_ratio = [_sanitize_float(i.get("change_ratio")) for i in data]

        self.data_dict = {
            "ticker": self.ticker,
            "alert": self.alert,
            "alert_type": self.alert_type,
            "change_ratio": self.change_ratio,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)
