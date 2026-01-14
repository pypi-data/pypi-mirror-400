# SecretVerify
A terminal-based tool to quickly validate leaked secrets across multiple providers.

## Installation

### PyPI
```bash
pip install secretverify
```

### From source
```bash
git clone https://github.com/markgraziano-twlo/secretverify.git
cd secretverify
pip install .
```

### Homebrew (macOS)
```bash
brew tap markgraziano-twlo/tap
brew install secretverify
```

## Usage

Run the interactive CLI:
```bash
secretverify
```

1. **Select** the secret type from the numbered list.
2. **Enter** the required credentials (token, key, domain/subdomain).
3. **View** the full HTTP response and a clear status:
   - ✅ Secret successfully rotated.
   - ⚠️ Secret is still live.

## Example

```bash
$ secretverify
Select a secret type to validate:
  1. GitHub Personal Access Token
  2. AWS Access Key & Secret
  …
Enter number: 1
Enter token: ghp_…
{HTTP 200 OK JSON}
✅ Secret successfully rotated.
```

## Contributing
Feel free to add new providers or improve error handling.