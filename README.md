DataDock
===========

DataDock is simple utility for quickly loading data from a variety of data sources into a local SQLite file. All connection and column type information is encoded in SQL comments, such that the SQL code contains all necessary metadata for connecting to source database, creating local SQLite database/tables, and inserting data.  This tool is helpful for quickly pulling data from a variety of sources in preparation for further analysis.  

Flags
--------

Following flags are available:
* `--from`: SQLAlchemy engine url of source database
* `--to`:   SQLAlchemy engine url of target database
* `--name`: Name of target table
* `--type`: Type of column. Must be a class/object inheriting SQLAlchemy `TypeEngine` class

Example
--------

### SQL Script test_datadock.sql
```sql
--from sqlite:///testing/tigerking.db
--to   sqlite:///testing/tigerking_new.db
--name trainer
SELECT
  first_name                   --type String(length=100)
, last_name as alias           --type String(length=100)
, dob                          --type Date
, CASE WHEN tiger_skills > 0.8
       THEN 1              
       ELSE 0
       END as binary_tiger_skills    --type Integer
FROM Trainer
```

### Shell
```bash
> datadock test_datadock.sql
```