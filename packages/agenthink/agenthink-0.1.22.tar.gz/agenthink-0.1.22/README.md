# DBConnector (Agenthink)

`DBConnector` is a database connectivity utility for the **Agenthink platform**.  
It enables agents running on Agenthink to securely connect to external **MySQL** and **MSSQL** databases using credentials managed by **Azure Blob Storage** and **Azure Key Vault**.

Connections are cached per session and are designed for **read-only access**, allowing agents to safely query data without modifying source databases.

## Purpose
This library allows **Agenthink agents** to:
- Connect to user-registered databases on the Agenthink platform
- Execute safe, read-only SQL queries
- Reuse database connections across agent sessions

## Features
- Session-based connection caching for agents  
- Supports **MySQL** and **MS SQL Server**  
- Secure secret management via **Azure Key Vault**  
- Datastore metadata loaded from **Azure Blob Storage**  
- Read-only SQL enforcement (`SELECT`, `SHOW`, `EXPLAIN`, etc.)  
- Built-in logging for observability and debugging  

## Basic Usage (Agenthink Agent)

```python
db = DBConnector.get(
    session_id="session_123",
    user_id="user1",
    workflow_id="workflow_A"
)

result = db.execute_query(
    db_name="database_name",
    query="SELECT * FROM item LIMIT 10"
)
