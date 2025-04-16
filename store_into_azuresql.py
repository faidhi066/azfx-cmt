import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
server = os.getenv("AZURE_SQL_SERVER")
database = os.getenv("AZURE_SQL_DATABASE")
username = os.getenv("AZURE_SQL_USERNAME")
password = os.getenv("AZURE_SQL_PASSWORD")
driver = "{SQL Server}"
# Connect to the database
connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"


def insert_user_details(users):
    try:
        # Connect to the database
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        # Clear existing data in the target table
        clear_command = (
            "DELETE FROM UserDetails; DBCC CHECKIDENT ('UserDetails', RESEED, 0);"
        )
        cursor.execute(clear_command)
        # Create a list of tuples for each user detail
        user_details = [
            (user["userId"], user["email"], user["displayName"], user["department"])
            for user in users
        ]
        # Construct the SQL command to insert the TVP data
        sql_command = """
            DECLARE @UserDetails UserDetailsType;
            INSERT INTO @UserDetails (userId, email, displayName, department)
            VALUES (?, ?, ?, ?);
            EXEC MergeUserDetails @UserDetails;
        """
        # Execute the SQL command with the parameterized user details
        cursor.executemany(sql_command, user_details)
        connection.commit()
    except pyodbc.Error as e:
        print("Error inserting user details:", e)
        connection.rollback()

    finally:
        cursor.close()
        connection.close()
