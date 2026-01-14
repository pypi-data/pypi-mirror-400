# OVINC Union Api SDK

[![PyPI version](https://badge.fury.io/py/ovinc-client.svg)](https://badge.fury.io/py/ovinc-client)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

[中文文档](README_CN.md)

A Python client for OVINC Union API, providing easy access to authentication, notifications, and TCaptcha verification.

## Installation

```bash
pip install ovinc-client
```

## Usage

### Initialization

```python
from ovinc_client.client import OVINCClient

APP_CODE = "your_app_code"
APP_SECRET = "your_app_secret"
OVINC_API_URL = "https://api.ovinc.cn"

client = OVINCClient(app_code=APP_CODE, app_secret=APP_SECRET, union_api_url=OVINC_API_URL)
```

### Notifications (Notice)

#### Send Email

```python
response = client.notice.mail({
    "to": "user@example.com",
    "subject": "Hello",
    "content": "This is a test email."
})
print(response.data)
```

#### Send SMS

```python
response = client.notice.sms({
    "phone": "13800138000",
    "template_id": "123456",
    "params": ["1234"]
})
print(response.data)
```

#### Send Robot Message

```python
response = client.notice.robot({
    "channel": "wecom",
    "content": "Hello from robot"
})
print(response.data)
```

### Authentication (Auth)

#### Verify Code

```python
response = client.auth.verify_code({
    "code": "123456",
    "key": "user_identifier"
})
print(response.data)
```

### TCaptcha Verification

This module requires Django settings configuration.

**Settings:**

```python
# settings.py
CAPTCHA_TCLOUD_ID = "your_tencent_cloud_id"
CAPTCHA_TCLOUD_KEY = "your_tencent_cloud_key"
CAPTCHA_APP_ID = "your_captcha_app_id"
CAPTCHA_APP_SECRET = "your_captcha_app_secret"
CAPTCHA_ENABLED = True
```

**Usage:**

```python
from ovinc_client.tcaptcha.utils import TCaptchaVerify

# In your view or API
def verify_captcha(request):
    user_ip = request.META.get("REMOTE_ADDR")
    ticket = request.data.get("ticket")
    randstr = request.data.get("randstr")
    ret = request.data.get("ret")
    
    verifier = TCaptchaVerify(
        user_ip=user_ip,
        ticket=ticket,
        randstr=randstr,
        ret=ret
    )
    
    if verifier.verify():
        return "Success"
    else:
        return "Failed"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
