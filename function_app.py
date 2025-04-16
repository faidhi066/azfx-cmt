import logging
import azure.functions as func
from utils import (
    fetch_all_users_concurrently,
    generate_access_token,
    install_all_users_concurrently,
)
from store_into_azuresql import insert_user_details

app = func.FunctionApp()


# TODO: 1. To make .env team_id, channel_id
# TODO: 2. To make .env all sensitive info i.e db, storage
# TODO: 3. To generate access token
@app.timer_trigger(
    schedule="*/10 * * * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False,
)
def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")

    access_token = generate_access_token()
    users = fetch_all_users_concurrently(
        team_id="your_team_id",
        channel_id="your_channel_id",
        access_token=access_token,
    )
    insert_user_details(users)
    response_list = []
    error_list = []
    install_all_users_concurrently(
        users,
        response_list,
        error_list,
        "your_teams_app_id",
        access_token=access_token,
    )

    logging.info("Python timer trigger function executed.")
