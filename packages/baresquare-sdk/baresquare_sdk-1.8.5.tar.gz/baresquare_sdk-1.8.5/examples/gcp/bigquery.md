# BigQuery

This document outlines how to use BigQuery with the `baresquare_sdk`.

BigQuery is a fully managed, serverless data warehouse that enables super-fast SQL queries using the processing
power of Google's infrastructure.

## Initialize

```python
from dotenv import load_dotenv

from baresquare_sdk.gcp.authentication import GoogleAuth
from baresquare_sdk.gcp.bigquery import BQ

load_dotenv()

bq = BQ(GoogleAuth())
```

Alternatively, you can pass in a `GCPClients` instance instead of a `CredentialProvider`.

```python
from baresquare_sdk.gcp.clients import GCPClients

gcp = GCPClients(GoogleAuth())
bq = BQ(gcp)
```

## Query

Query a table and return a pandas DataFrame.

```python
df = bq.query("SELECT * FROM `project.dataset.table` LIMIT 10")
print(df)
```

### Query Parameters

You can pass parameters to the query using the `params` argument. The parameters are passed as a dictionary of
parameter names and values.

```python
df = bq.query("SELECT * FROM `project.dataset.table` LIMIT @limit", params={"limit": 10})
print(df)
```

Parameter types are inferred from the values:

| Type | BigQuery Type |
|------|---------------|
| bool | BOOL          |
| int  | INT64         |
| float | FLOAT64       |
| Decimal | NUMERIC       |
| str | STRING        |
| bytes | BYTES         |
| datetime | TIMESTAMP     |
| date | DATE          |
| time | TIME          |
| None | NULL          |

## External Tables Linked to Google Sheets

When querying BigQuery external tables backed by Google Sheets, ensure the service account has access to the
Sheet. You need to:

* Share the Google Sheet with the service account email (give at least Viewer access)
* The SDK automatically includes the necessary Drive API scope (`drive.readonly`) to access the sheets

Example:

```python
# Query an external table linked to a Google Sheet
df = bq.query("SELECT * FROM `project.dataset.external_sheet_table` LIMIT 10")
print(df)
```

**Note:** If you encounter a `403 Access Denied: Permission denied while getting Drive credentials` error, verify that:

1. The Google Sheet is shared with your service account email
2. The service account has BigQuery Data Viewer role (or equivalent) on the dataset
