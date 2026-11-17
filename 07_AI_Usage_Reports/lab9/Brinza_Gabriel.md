# AI Usage Report

## SQLAlchemy Database Connection

### Work Performed with AI Assistance
The AI assistant was used to:

1. **Review the class diagrams** and identify persistent entities, their attributes, enumerated values, and relationships.
2. **Draft a PostgreSQL schema** containing tables, UUID primary keys, foreign keys, constraints, indexes, and PostgreSQL ENUM types.
3. **Represent user roles** (`student`, `validator`, and `admin`) as a database ENUM, with `student` as the default role.

### Limitations
The diagrams describe both persistent domain entities and non-persistent elements such as services, interfaces, adapters, and DTOs. The SQL schema focuses on persistent data; application behavior and authorization rules still need to be implemented in the application. In particular, the `user_role` ENUM restricts values stored in the role column but does not itself enforce role-based permissions.

The script's idempotency applies to repeated execution against a database created with the same schema. `CREATE TABLE IF NOT EXISTS` does not update the structure of an existing table. Future schema changes should therefore be handled with database migrations, for example using Alembic.

**ChatGPT chat URL:** https://chatgpt.com/c/6af9bd5a-c168-83ed-b7bd-d78e81c7f00d 