# iCloud HideMyEmail Generator

**Python CLI tool for generating and managing iCloud+ HideMyEmail addresses with multi-account support**

<div align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status: Active">
  <img src="https://img.shields.io/badge/Python-3.8+-blue" alt="Python: 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License: MIT">
  <a href="https://pypi.org/project/icloud-hme/"><img src="https://img.shields.io/pypi/v/icloud-hme.svg?style=flat-square&color=cb3837&logo=pypi&logoColor=white" alt="PyPI version"></a>
  <a href="https://github.com/glizzykingdreko/icloud-hidemymail-generator"><img src="https://img.shields.io/github/stars/glizzykingdreko/icloud-hidemymail-generator?style=flat-square&logo=github" alt="GitHub stars"></a>
</div>

<br>

<div align="center">
  <a href="https://takionapi.tech/discord"><img src="https://img.shields.io/badge/Discord-5865F2?logo=discord&logoColor=white&style=flat-square" alt="Discord"></a>
  <a href="https://medium.com/@glizzykingdreko"><img src="https://img.shields.io/badge/Medium-12100E?logo=medium&logoColor=white&style=flat-square" alt="Medium"></a>
  <a href="https://buymeacoffee.com/glizzykingdreko"><img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-FFDD00?logo=buy-me-a-coffee&logoColor=black&style=flat-square" alt="Buy Me a Coffee"></a>
</div>

<br>

## Table of Contents

- [iCloud HideMyEmail Generator](#icloud-hidemyemail-generator)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Commands](#commands)
    - [Authentication](#authentication)
    - [Generate Emails](#generate-emails)
    - [List Emails](#list-emails)
    - [Export Emails](#export-emails)
    - [Manage Accounts](#manage-accounts)
  - [Rate Limits](#rate-limits)
  - [Data Storage](#data-storage)
  - [Python API Usage](#python-api-usage)
  - [Contributing](#contributing)
  - [License](#license)
  - [Author](#author)

## Overview

With an iCloud+ subscription you get this nice "HideMyMail" feature that let's you create random email addresses that forward to your personal inbox. Let's use our subscription at its best and easily generate them instead of buying address lists.

There are some other similar open source projects around, but I hated the fact that the login was via a "copy and paste" cookies logic. Here you get everything done properly with full SRP authentication and 2FA support.

## Installation

```bash
pip install icloud-hme
```

Or install from source:

```bash
git clone https://github.com/glizzykingdreko/icloud-hidemymail-generator
cd icloud-hidemymail-generator
pip install -e .
```

## Quick Start

```bash
# 1. Authenticate with your iCloud account
icloud-hme auth

# 2. Generate 5 new email aliases
icloud-hme generate -n 5

# 3. Export all emails to CSV
icloud-hme export --format csv
```

## Commands

### Authentication

```bash
# Interactive login with 2FA support
icloud-hme auth

# Or provide email directly
icloud-hme auth -e your@icloud.com
```

### Generate Emails

```bash
# Interactive generation (prompts for count)
icloud-hme generate

# Generate 5 permanent emails
icloud-hme generate -n 5

# Generate with custom label
icloud-hme generate -n 10 --label shopping

# Generate temporary emails (not reserved)
icloud-hme generate -n 3 --temp

# Generate and save to file
icloud-hme generate -n 5 --output emails.csv --format csv

# Use specific account
icloud-hme generate -n 5 --account other@icloud.com
```

### List Emails

```bash
# List all HideMyEmail addresses
icloud-hme list

# List for specific account
icloud-hme list --account your@icloud.com
```

### Export Emails

```bash
# Export to CSV (prompts for output path)
icloud-hme export

# Export to JSON
icloud-hme export --format json

# Export only active emails
icloud-hme export --filter active

# Custom output path
icloud-hme export --output ~/Desktop/my_emails --format csv
```

### Manage Accounts

```bash
# List authenticated accounts
icloud-hme accounts

# Remove an account
icloud-hme logout
```

## Rate Limits

Apple enforces the following rate limits on HideMyEmail:

| Limit | Value |
|-------|-------|
| Per 30 minutes | ~5 emails × family members |
| Total per account | ~700 emails |

The CLI automatically detects rate limits and displays warnings when they're hit.

## Data Storage

All data is stored locally in `~/.icloud-hme/`:

```
~/.icloud-hme/
├── account1_at_icloud_com/
│   ├── session.json      # Authentication tokens
│   └── emails.json       # Generated emails log
└── account2_at_icloud_com/
    └── ...
```

Session tokens and all of your data is stored **locally**.

## Python API Usage

You can also use the library programmatically:

```python
from icloud_hme import ICloudSession, HideMyEmailGenerator

# Authenticate
session = ICloudSession()
session.login("your@icloud.com", "password")

# Generate emails
generator = HideMyEmailGenerator(session)
emails = generator.generate_multiple(
    count=5,
    reserve=True,
    label_prefix="api_test"
)

for email in emails:
    print(email)
```

## Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

If you found this project helpful or interesting, consider starring the repo and following me for more tools, or buy me a coffee to keep me going ☕

<p align="center">
  <a href="https://github.com/glizzykingdreko"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>
  <a href="https://twitter.com/glizzykingdreko"><img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" alt="Twitter"></a>
  <a href="https://medium.com/@glizzykingdreko"><img src="https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white" alt="Medium"></a>
  <a href="https://takionapi.tech/discord"><img src="https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="mailto:glizzykingdreko@protonmail.com"><img src="https://img.shields.io/badge/ProtonMail-8B89CC?style=for-the-badge&logo=protonmail&logoColor=white" alt="Email"></a>
  <a href="https://buymeacoffee.com/glizzykingdreko"><img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me a Coffee"></a>
</p>
