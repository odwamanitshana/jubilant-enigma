#!/bin/bash

# This script automates the process of running SQL migration files.

# Define the database connection parameters
DB_HOST="localhost"
DB_USER="your_username"
DB_PASSWORD="your_password"
DB_NAME="your_database_name"

# Run the migration SQL file
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < ../sql/migrations/001_create_wardrobe_items_table.sql

# You can add more migration files here as needed
# mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < ../sql/migrations/002_another_migration.sql

echo "Migrations have been run successfully."