from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# convert "mm/dd/yyyy" to iso 8601
def to_iso_8601_format(date: str) -> datetime:
    dt_hk = datetime.strptime(date, "%m/%d/%Y").replace(
        tzinfo=ZoneInfo("Asia/Hong_Kong")
    )

    return dt_hk