# lokryn-pipe-audit

Data validation library for audit pipelines using Polars. Define validation contracts in TOML and validate data from local files, S3, GCS, or Azure Blob Storage.

## Installation

```bash
pip install lokryn-pipe-audit
```

## Quick Start

```python
from lokryn_pipe_audit import load_contract, validate_dataframe, get_driver

# Load a validation contract
contract = load_contract("contracts/users.toml")

# Load data with the appropriate driver
driver = get_driver("csv")
df = driver.load(open("users.csv", "rb").read())

# Validate
outcome = validate_dataframe(df, contract)

if outcome.passed:
    print("Validation passed!")
else:
    for failure in outcome.failures:
        print(f"Failed: {failure.rule} on {failure.column}")
```

## Contracts

Define validation rules in TOML:

```toml
[contract]
name = "users"
version = "1.0"
format = "csv"

[[columns]]
name = "email"
rules = [
    { rule = "not_null" },
    { rule = "unique" },
    { rule = "pattern", pattern = "^[\\w.-]+@[\\w.-]+\\.\\w+$" }
]

[[columns]]
name = "age"
rules = [
    { rule = "not_null" },
    { rule = "range", min = 0, max = 150 }
]

[[columns]]
name = "status"
rules = [
    { rule = "in_set", values = ["active", "inactive", "pending"] }
]
```

## Built-in Validators

| Validator | Description | Parameters |
|-----------|-------------|------------|
| `not_null` | No null values | - |
| `unique` | All values unique | - |
| `pattern` | Regex match | `pattern` |
| `range` | Numeric range | `min`, `max` |
| `in_set` | Value in allowed set | `values` |
| `completeness` | % non-null above threshold | `threshold` |
| `mean_between` | Column mean in range | `min`, `max` |
| `row_count` | Row count in range | `min`, `max` |
| `compound_unique` | Unique across columns | `columns` |
| `date_format` | Date string format | `format` |
| `outlier_sigma` | No outliers beyond N sigma | `sigma` |

## Storage Connectors

### Local
```python
from lokryn_pipe_audit import LocalConnector

connector = LocalConnector()
data = await connector.fetch("/path/to/file.csv")
```

### S3
```python
from lokryn_pipe_audit import S3Connector, load_profiles, get_profile

profiles = load_profiles("profiles.toml")
profile = get_profile(profiles, "my_s3_profile")

connector = S3Connector.from_profile_and_url(profile, "s3://bucket/key")
data = await connector.fetch("s3://bucket/data.csv")
```

### GCS
```python
from lokryn_pipe_audit import GCSConnector, load_profiles, get_profile

profiles = load_profiles("profiles.toml")
profile = get_profile(profiles, "my_gcs_profile")

connector = GCSConnector.from_profile_and_url(profile, "gs://bucket/key")
data = await connector.fetch("gs://bucket/data.csv")
```

### Azure Blob Storage
```python
from lokryn_pipe_audit import AzureConnector, load_profiles, get_profile

profiles = load_profiles("profiles.toml")
profile = get_profile(profiles, "my_azure_profile")

connector = AzureConnector.from_profile_and_url(profile, url)
data = await connector.fetch("https://account.blob.core.windows.net/container/blob")
```

## Profiles

Configure storage credentials in `profiles.toml`:

```toml
[s3_profile]
provider = "s3"
region = "us-east-1"
access_key = "${AWS_ACCESS_KEY_ID}"
secret_key = "${AWS_SECRET_ACCESS_KEY}"

[gcs_profile]
provider = "gcs"
service_account_json = "${GCS_SERVICE_ACCOUNT_JSON}"

[azure_profile]
provider = "azure"
connection_string = "${AZURE_STORAGE_CONNECTION_STRING}"
```

Environment variables in `${VAR}` format are automatically expanded.

## File Formats

- CSV (`.csv`)
- Parquet (`.parquet`)

## License

AGPL-3.0 - See [LICENSE](LICENSE) for details.

## Links

- [Lokryn](https://lokryn.com)
- [Documentation](https://docs.lokryn.com/pipe-audit)
