import requests
import concurrent.futures
import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # Import tqdm for progress tracking
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def generate_access_token():
    url = f"https://login.microsoftonline.com/{os.getenv("TENANT_ID")}/oauth2/v2.0/token"

    payload = {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }
    files = []
    headers = {
        "Cookie": "fpc=ApSI8ZH3pBxHhBIw0hWn9ryNF7I9AQAAAE3Ckd8OAAAA; stsservicecookie=estsfd; x-ms-gateway-slice=estsfd"
    }
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print(response.text)


def fetch_user_batch(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    users = data.get("value", [])
    next_link = data.get("@odata.nextLink")
    return users, next_link


def fetch_user_department(user_id, headers):
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}?$select=department"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data.get("department", "")


def fetch_all_users_concurrently(team_id, channel_id, access_token):
    base_url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/members"
    headers = {"Authorization": f"Bearer {access_token}"}

    # Initial request to get the first batch of users
    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    data = response.json()
    all_users = {}
    next_link = data.get("@odata.nextLink")

    # Process the first batch of users
    for user in data.get("value", []):
        user_id = user.get("userId")
        if user_id:
            all_users[user_id] = {
                "userId": user_id,
                "displayName": user.get("displayName", ""),
                "email": user.get("email", ""),
            }

    visited_urls = set()
    batch_urls = [next_link] if next_link else []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        while batch_urls:
            futures = {
                executor.submit(fetch_user_batch, url, headers): url
                for url in batch_urls
                if url and url not in visited_urls
            }
            visited_urls.update(batch_urls)
            batch_urls = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    users, next_link = future.result()
                    for user in users:
                        user_id = user.get("userId")
                        if user_id:
                            all_users[user_id] = {
                                "userId": user_id,
                                "displayName": user.get("displayName", ""),
                                "email": user.get("email", ""),
                            }
                    if next_link and next_link not in visited_urls:
                        batch_urls.append(next_link)
                except Exception as e:
                    print(f"Batch processing failed: {e}")
        # Fetch department for each user concurrently
        department_futures = {
            executor.submit(fetch_user_department, user_id, headers): user_id
            for user_id in all_users
        }
        for future in concurrent.futures.as_completed(department_futures):
            user_id = department_futures[future]
            try:
                department = future.result()
                all_users[user_id]["department"] = department
            except Exception as e:
                print(f"Failed to fetch department for user {user_id}: {e}")
    return list(all_users.values())


# This function will be used by each thread to process a user
def install_app_for_user(user_dict, access_token, error_list, teamsAppId):
    url = f"https://graph.microsoft.com/v1.0/users/{user_dict['userId']}/teamwork/installedApps"
    payload = json.dumps(
        {
            "teamsApp@odata.bind": f"https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/{teamsAppId}",
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        if response.status_code == 201:
            return f"App installed for user {user_dict['userId']}"
        else:
            return f"Unexpected status code: {response.status_code} for user {user_dict['displayName']}"
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 403:
            error_list.append(
                {"userId": user_dict["userId"], "displayName": user_dict["displayName"]}
            )
        return f"HTTP error occurred for user {user_dict['displayName']}: {http_err}"
    except Exception as err:
        return f"An error occurred for user {user_dict['displayName']}: {err}"


def install_all_users_concurrently(
    users_dict, response_list, error_list, teamsAppId, access_token
):
    # Define the number of workers, adjust based on your needs and system capability
    max_workers = 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks and collect future objects
        futures = {
            executor.submit(
                install_app_for_user, user, access_token, error_list, teamsAppId
            ): user
            for user in users_dict
        }
        # Use tqdm to display a progress bar
        with tqdm(total=len(futures), desc="Installing Apps", unit="user") as pbar:
            for future in as_completed(futures):
                response_list.append(future.result())
                pbar.update(1)  # Update the progress bar
