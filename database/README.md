# Database Configuration

This folder contains all database-related files for the Chainloot Yoda Bot Interface project.

## Files & Folders

- **`schema.prisma`**: Prisma database schema defining the data models for conversations, threads, and user data
- **`prisma/`**: Prisma client and generated files
- **`migrations/`**: Database migration files for schema changes

## Database Setup

The application uses PostgreSQL as the database backend. The database is automatically set up and migrated when the Docker containers start.

### Key Components

- **Prisma ORM**: Type-safe database access with schema definitions
- **PostgreSQL**: Primary database for conversation persistence
- **Automatic Migrations**: Database schema is automatically migrated on container startup

## Usage

### Manual Database Operations

If you need to run database operations manually:

```bash
# Generate Prisma client (usually done automatically)
npx prisma generate --schema=database/schema.prisma

# Create a new migration (development)
npx prisma migrate dev --schema=database/schema.prisma

# Deploy migrations (production)
npx prisma migrate deploy --schema=database/schema.prisma

# View database
npx prisma studio --schema=database/schema.prisma
```

### Database Schema

The schema includes:
- **Thread**: Conversation threads
- **Message**: Individual messages within threads
- **User**: User information
- **Tag**: Message tagging system

## Docker Integration

Database operations are automatically handled during container startup via the `start.sh` script:

1. Migrations are deployed: `prisma migrate deploy --schema=database/schema.prisma`
2. Prisma client is generated: `prisma generate --schema=database/schema.prisma`

## Development

When making schema changes:

1. Edit `database/schema.prisma`
2. Run `npx prisma migrate dev` to create and apply migrations
3. The changes will be automatically applied in Docker on next startup

## Links

- [Prisma Documentation](https://www.prisma.io/docs)
- [Prisma Migrate](https://www.prisma.io/docs/concepts/components/prisma-migrate)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)</content>
<parameter name="filePath">c:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\database\README.md