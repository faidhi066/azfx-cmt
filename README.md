# Azure Functions Project: `azfx-cmt`

This project is an **Azure Functions** application designed to manage user data, interact with the **Microsoft Graph API**, and store user details in an **Azure SQL Database**. It includes functionality for fetching user details, installing Microsoft Teams apps, and performing scheduled database operations.

---

## 📁 Project Structure

| File/Folder              | Description                                                                                           |
| ------------------------ | ----------------------------------------------------------------------------------------------------- |
| `function_app.py`        | Main entry point. Contains the timer-triggered function that orchestrates the workflow.               |
| `utils.py`               | Utility functions for Microsoft Graph API operations (e.g., fetching user details, app installation). |
| `store_into_azuresql.py` | Database operations (e.g., inserting user details using TVP).                                         |
| `.vscode/`               | VS Code configuration for debugging and automation.                                                   |
| `requirements.txt`       | List of Python dependencies.                                                                          |
| `host.json`              | Azure Functions runtime configuration.                                                                |
| `.gitignore`             | Files/directories to be excluded from Git version control.                                            |
| `.funcignore`            | Files/directories to be excluded from Azure Functions deployment.                                     |

---

## 🛠 Prerequisites

- ✅ **Azure Account** – Required for deployment and resource management
- ✅ **Python 3.8+**
- ✅ **Azure Functions Core Tools**
- ✅ **Azure SQL Database** – With appropriate schema and stored procedures

---

## 🚀 Getting Started

1. Clone the Repository

```bash
git clone <repo-url>
cd azfx-cmt
```

2. Create & Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Dependencies

```bash
pip install -r requirements.txt
```

4. Set Up Environment Variables
   Create a .env file in the root directory with the following contents:

```bash
CLIENT_ID=your-client-id
TENANT_ID=your-tenant-id
CLIENT_SECRET=your-client-secret
SQL_CONNECTION_STRING=your-sql-connection-string
APP_ID=your-teams-app-id
```

5. Run the Application Locally

```bash
func start
```

6. Debugging
   Use the VS Code debugger configuration provided in .vscode/launch.json.

## 🔑 Key Features

### ✅ Fetch User Details

• Retrieves user details from Microsoft Teams channels using the Microsoft Graph API
• Supports concurrent requests for improved performance

### ✅ Install Teams Apps

• Installs a specified Microsoft Teams app for all users in a channel

### ✅ Store User Data

• Inserts user details into an Azure SQL database using a Table-Valued Parameter (TVP) approach

### ✅ Timer Trigger

• Executes the workflow periodically based on the cron schedule defined in function_app.py

## 🚢 Deployment

1. Deploy to Azure

Use Azure Functions Core Tools:

```bash
func azure functionapp publish <YOUR_FUNCTION_APP_NAME>
```

2. Configure Application Settings in Azure

In the Azure Portal, navigate to your Function App:

Settings > Configuration

Add the following environment variables:
• CLIENT_ID
• TENANT_ID
• CLIENT_SECRET
• SQL_CONNECTION_STRING
• APP_ID

## ⚠️ Notes

• Never commit sensitive information such as secrets or connection strings. Use environment variables and .env files locally, and Azure Key Vault in production.
• The .gitignore and .funcignore files are configured to exclude sensitive files and unnecessary deployment artifacts.
