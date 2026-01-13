# fast-tor-requests

A fast drop-in replacement for `requests.Session` using Tor
with `IsolateSOCKSAuth` for automatic IP rotation.

## Requirements
- Tor running locally
- torrc must include:
