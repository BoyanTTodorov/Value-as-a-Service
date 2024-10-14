VAS Data Management Application
This project is a Python-based application for managing and querying data related to VAS (Value-Added Services) operations. The application connects to a database, retrieves data based on user-defined date ranges, and presents it in a user-friendly interface built with Tkinter.

Table of Contents
Features
Installation
Usage
Files
Contributing
License
Features
Connects to a database using ODBC.
Executes complex SQL queries to retrieve VAS data.
User-friendly GUI for selecting date ranges and displaying results.
Ability to save query results to an Excel report.
Supports multithreading for loading data without freezing the UI.
Installation
To set up this project, ensure you have Python 3.x installed. Follow these steps:

Clone the repository:

bash
Copy code
git clone <repository-url>
cd <repository-directory>
Install the required packages:

bash
Copy code
pip install -r requirements.txt
Ensure you have the ODBC driver for your database installed and correctly configured.

Update the user_credential.py file with your database connection details.

Usage
Run the application:

bash
Copy code
python user_interface.py
Enter the desired date range in the format yyyy-mm-dd.

Click "Load Data" to retrieve and display the data.

Use the "Save Report" button to export the displayed data to an Excel file.

Files
database.py: Contains the DatabaseManager class for managing database connections and executing queries.
queries.py: Defines the Queries class, which constructs SQL queries based on specified date ranges.
user_credential.py: Stores database connection credentials (make sure to keep this file secure).
user_interface.py: Implements the GUI using Tkinter and manages user interactions.
Contributing
Contributions are welcome! Please feel free to submit a pull request or create an issue for any suggestions or improvements.

License
This project is licensed under the MIT License - see the LICENSE file for details.
