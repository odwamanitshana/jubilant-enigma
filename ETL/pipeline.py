import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def extract_data(source_path):
    """
    Extract data from source CSV file
    Args:
        source_path (str): Path to the source CSV file
    Returns:
        pandas.DataFrame: Extracted data
    """
    logger.info(f"Extracting data from {source_path}")
    try:
        df = pd.read_csv(source_path)
        logger.info(f"Successfully extracted {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Error extracting data: {e}")
        raise

def save_processed_data(df, original_filename):
    """
    Save the transformed data to the processed folder
    Args:
        df (pandas.DataFrame): Transformed data
        original_filename (str): Name of the original file
    """
    processed_dir = Path('../data/processed')
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Create processed filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    processed_filename = f"processed_{Path(original_filename).stem}_{timestamp}.csv"
    processed_path = processed_dir / processed_filename
    
    # Save to CSV
    df.to_csv(processed_path, index=False)
    logger.info(f"Saved processed data to {processed_path}")

def transform_data(df):
    """
    Clean and transform the wardrobe items data
    Args:
        df (pandas.DataFrame): Raw data
    Returns:
        pandas.DataFrame: Transformed data
    """
    logger.info("Starting data transformation")
    logger.info(f"Input columns: {df.columns.tolist()}")
    try:
        # Rename columns to match database schema
        column_mapping = {
            'web-scraper-start-url': 'web_scraper_start_url',
            'Products-href': 'products_href',
            'Image URL-src': 'image_url_src',
            'Gender': 'gender',
            'Category Style': 'category_style'
        }
        df = df.rename(columns=column_mapping)

        # Define all expected columns with default values
        expected_columns = {
            'web_scraper_start_url': '',
            'products_href': '',
            'image_url_src': '',
            'product_name': 'unknown',
            'main_category': 'unknown',
            'color': 'unknown',
            'occasion': 'general',
            'season': 'all-season',
            'price_pkr': 0,
            'discount': '0%',
            'work_details': '',
            'shoe_color': 'unknown',
            'shoe_style': 'unknown',
            'gender': 'unisex',
            'fit_type': 'regular',
            'categorize_outfit': 'unknown',
            'category_style': 'unknown',
            'fabric': 'unknown'
        }
        
        # Add missing columns with default values
        for col, default_value in expected_columns.items():
            if col not in df.columns:
                logger.warning(f"Adding missing column '{col}' with default value '{default_value}'")
                df[col] = default_value
                
        # Handle missing values in existing columns
        df = df.fillna(expected_columns)

        # Convert price to integer, replacing invalid values with 0
        df['price_pkr'] = pd.to_numeric(df['price_pkr'], errors='coerce').fillna(0).astype(int)

        # Standardize text columns
        text_columns = ['color', 'occasion', 'season', 'gender', 'main_category', 
                       'shoe_color', 'shoe_style', 'fit_type', 'categorize_outfit', 
                       'category_style', 'fabric']
        
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].str.lower().str.strip()

        # Validate URLs
        url_columns = ['web_scraper_start_url', 'products_href', 'image_url_src']
        for col in url_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')

        logger.info("Data transformation completed successfully")
        return df

    except Exception as e:
        logger.error(f"Error during transformation: {e}")
        raise

def load_data(df, conn):
    """
    Load transformed data into MySQL database
    Args:
        df (pandas.DataFrame): Transformed data
        conn (mysql.connector.connection): Database connection
    """
    logger.info("Starting data loading")
    cursor = conn.cursor()
    
    try:
        # Define the expected columns in the correct order
        expected_columns = [
            'web_scraper_start_url', 'products_href', 'image_url_src',
            'product_name', 'main_category', 'color', 'occasion', 'season',
            'price_pkr', 'discount', 'work_details', 'shoe_color',
            'shoe_style', 'gender', 'fit_type', 'categorize_outfit',
            'category_style', 'fabric'
        ]
        
        # Create a new DataFrame with only the required columns in the correct order
        insert_df = pd.DataFrame(columns=expected_columns)
        
        # Copy data from source DataFrame to the new one, handling missing columns
        for col in expected_columns:
            if col in df.columns:
                insert_df[col] = df[col]
            else:
                insert_df[col] = ''  # Set empty string as default for missing columns
        
        # Insert data row by row
        for idx, row in insert_df.iterrows():
            sql = """INSERT INTO wardrobe_items (
                web_scraper_start_url, products_href, image_url_src,
                product_name, main_category, color, occasion, season,
                price_pkr, discount, work_details, shoe_color,
                shoe_style, gender, fit_type, categorize_outfit,
                category_style, fabric
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            values = tuple(row)
            cursor.execute(sql, values)
            
            if idx > 0 and idx % 100 == 0:
                logger.info(f"Inserted {idx} records")
            
        conn.commit()
        logger.info(f"Successfully loaded {len(df)} records into the database")
        
    except Exception as e:
        logger.error(f"Error during data loading: {e}")
        conn.rollback()
        raise
        
    finally:
        cursor.close()

def main():
    """Main ETL process"""
    logger.info("Starting ETL process")
    
    # Validate environment variables
    required_env_vars = ['DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return

    # Set up paths
    data_dir = Path('../data/raw')  # Adjust this path as needed
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return

    conn = None
    try:
        # Connect to database
        conn = mysql.connector.connect(**db_config)
        logger.info("Successfully connected to database")

        # Process each CSV file in the raw data directory
        for csv_file in data_dir.glob('*.csv'):
            logger.info(f"Processing file: {csv_file}")
            
            # Extract
            data = extract_data(csv_file)
            
            # Transform
            transformed_data = transform_data(data)
            
            # Save transformed data to processed folder
            save_processed_data(transformed_data, csv_file.name)
            
            # Load
            load_data(transformed_data, conn)
            
        logger.info("ETL process completed successfully!")
        
    except Exception as e:
        logger.error(f"ETL process failed: {e}")
        
    finally:
        if conn and conn.is_connected():
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    main()