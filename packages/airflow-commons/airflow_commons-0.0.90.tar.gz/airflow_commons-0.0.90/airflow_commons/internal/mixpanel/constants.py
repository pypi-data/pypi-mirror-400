BASE_URL = "https://api.mixpanel.com/"

ENGAGE_API_URL = BASE_URL + "engage?ip=0"
ENGAGE_BATCH_SIZE = 50

QUERY_START = "?"
AND = "&"
PROJECT_ID_QUERY_PARAM = "project_id="
STRICT = "strict=1"
IMPORT_API_URL = (
    BASE_URL
    + "import"
    + QUERY_START
    + STRICT
    + AND
    + PROJECT_ID_QUERY_PARAM
    + "{project_id}"
)

LOOKUP_TABLE_API_URL = BASE_URL + "lookup-tables"
GET_LOOKUP_TABLES = (
    LOOKUP_TABLE_API_URL + QUERY_START + PROJECT_ID_QUERY_PARAM + "{project_id}"
)
REPLACE_LOOKUP_TABLE = (
    LOOKUP_TABLE_API_URL
    + "/{table_id}"
    + QUERY_START
    + PROJECT_ID_QUERY_PARAM
    + "{project_id}"
)
