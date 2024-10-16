import enum


class CaptchaType(enum.Enum):
    NONE = "NONE"
    RECAPTCHA = "RECAPTCHA"
    HCAPTCHA = "HCAPTCHA"
    MCAPTCHA = "MCAPTCHA"
    TURNSTILE = "TURNSTILE"
