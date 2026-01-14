# robloxinfo

**robloxinfo** is a Python library for fetching **public Roblox account information** using official Roblox APIs.  
It provides a clean, reliable, and easy-to-use interface for developers who want to retrieve account details, social statistics, presence information, and avatar data for Roblox users. No authentication or private access is required.

---

## Features

- Retrieve basic account details:
  - Username
  - Display name
  - User ID
  - Account creation date
  - Account description
  - Ban status
- Fetch social statistics:
  - Friends count
  - Followers count
  - Following count
- Presence tracking:
  - Online/offline status
  - Last online timestamp (if available)
- Avatar thumbnail URL
- Safe and robust: handles missing fields gracefully
- Pure Python, no Discord dependency, fully asynchronous optional

---

## Installation

Install via `pip`:

```bash
pip install robloxinfo
