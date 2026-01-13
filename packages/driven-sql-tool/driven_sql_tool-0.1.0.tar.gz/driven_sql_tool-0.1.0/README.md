# SQL Tools

## Description

This is simply a turbodbc wrapper. To reduce boilerplate on routine SQL actions, making a code a little bit cleaner.

## Content

Core functionality include:
- `SQLConfig` : Collection of connection configuration options. With `TurbODBCOptions` for advanced options
- `Query` : Query object
- `QuerySequence` : Collection of Queries

```Python
from driven_sql_tool import SQLConfig, TurbODBCOptions, Query, QuerySequence
```

## Usage samples

```Python
# prepare sample instanced config ...
turbodbc_options = TurbODBCOptions(autocommit=False, use_async_io=False)
conf = SQLConfig(server=r'server.address', database=r'db', turbodbc_options=turbodbc_options)
# ... or simply set defaults
SQLConfig.default_server = r'default.server'
SQLConfig.default_database = r'default.database'
```

Most common actions (Data Query Language):
```Python
# regular querying
df_res = Query('SELECT * FROM db.schema.table', conf=conf).execute()
# not specifying conf attribute will grab class defaults
df_res = Query('SELECT * FROM db.schema.table').execute()
# the result is also stored in `data` property of `Query` object 
query = Query('SELECT * FROM db.schema.table')
query.execute()
df_res = query.data

# .sql file querying
df_res = Query('./path/to/file.sql').execute()
```

Parametrized actions 
```Python
# parametrized insertion ...
Query(
    """
        INSERT INTO db.schema.table
        ([ID], [field1], [field2], [date])
        VALUES (?, ?, ?, ?)
    """, 
    data=df_insert[['ID', 'field1', 'field2', 'date']]
).execute()
# ... or execution
Query('EXEC db.schema.sproc @p1=?, @p2=?', data=df_exec[['p1', 'p2']]).execute()
```

Running multiple queries
```Python
# prepare sequence of queries
queries = QuerySequence()

queries.case_1 = Query('SELECT * FROM db.schema.table', conf=conf_1)
queries.case_2 = Query('./query.sql', conf=conf_2)
queries.case_3 = Query('EXEC db.schema.sproc @p1=?', data=df_exec[['p1']])

# run multiple queries sequentially ...
queries.run_seq()
# ... or, alternatively, in parallel (`joblib`)
queries.run_par()

# then access `data` property
df_res_1 = queries.case_1.data
```
