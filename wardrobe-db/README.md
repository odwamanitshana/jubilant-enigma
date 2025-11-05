# Wardrobe Database Project

This project is designed to manage wardrobe items through a structured database. It includes SQL scripts for creating tables, seeding initial data, and running migrations.

## Project Structure

```
wardrobe-db
├── sql
│   ├── migrations
│   │   └── 001_create_wardrobe_items_table.sql
│   ├── seeds
│   │   └── seed_wardrobe_items.sql
│   └── schema.sql
├── scripts
│   └── run_migrations.sh
├── .gitignore
└── README.md
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd wardrobe-db
   ```

2. **Database Configuration**
   - Ensure you have a compatible database server running (e.g., MySQL, PostgreSQL).
   - Update the database connection settings in the `run_migrations.sh` script as needed.

3. **Run Migrations**
   - Execute the migration script to create the necessary tables:
   ```bash
   bash scripts/run_migrations.sh
   ```

4. **Seed Initial Data**
   - Optionally, run the seed script to populate the `wardrobe_items` table with sample data.

## Usage Guidelines

- Modify the SQL scripts in the `sql` directory as needed to adjust the database schema or seed data.
- Use version control best practices to manage changes to the project.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.