from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .captchaType import CaptchaType


class MetaData(BaseModel):
    id: int
    created_at: datetime
    name: str
    captcha_type: CaptchaType
    captcha_sitekey: Optional[str] = None
    captcha_secret: Optional[str] = None
