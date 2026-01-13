# Another FastAPI JWT Auth

[//]: # (![Tests]&#40;https://github.com/IndominusByte/fastapi-jwt-auth/workflows/Tests/badge.svg&#41;)

[//]: # ([![Coverage Status]&#40;https://coveralls.io/repos/github/IndominusByte/fastapi-jwt-auth/badge.svg?branch=master&#41;]&#40;https://coveralls.io/github/IndominusByte/fastapi-jwt-auth?branch=master&#41;)

[//]: # ([![PyPI version]&#40;https://badge.fury.io/py/fastapi-jwt-auth.svg&#41;]&#40;https://badge.fury.io/py/fastapi-jwt-auth&#41;)

[//]: # ([![Downloads]&#40;https://static.pepy.tech/personalized-badge/fastapi-jwt-auth?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads&#41;]&#40;https://pepy.tech/project/fastapi-jwt-auth&#41;)

---

[//]: # (**Documentation**: <a href="https://indominusbyte.github.io/fastapi-jwt-auth" target="_blank">https://indominusbyte.github.io/fastapi-jwt-auth</a>)

**Source Code**:
<a href="https://github.com/delrey1/another-fastapi-jwt-auth/" target="_blank">https://github.com/delrey1/another-fastapi-jwt-auth/</a>

---

## Background

This was forked from https://github.com/IndominusByte/fastapi-jwt-auth as it is no longer maintained.

This release contains changes related to Pydantic >2 and PyJWT > 2. I used this on my own projects and will be updating
it
as required. PRs invited.

## Features
FastAPI extension that provides JWT Auth support (secure, easy to use and lightweight), if you were familiar with flask-jwt-extended this extension suitable for you, cause this extension inspired by flask-jwt-extended 😀

- Access tokens and refresh tokens
- Freshness Tokens
- Revoking Tokens
- Support for WebSocket authorization
- Support for adding custom claims to JSON Web Tokens
- Storing tokens in cookies and CSRF protection

## Installation
The easiest way to start working with this extension with pip

```bash
pip install another-fastapi-jwt-auth
```

## License
This project is licensed under the terms of the MIT license.
