# coding: utf-8

"""
    DB Analytics Tools: Airflow REST API Client

    This module provides a class for interacting with the Apache Airflow REST API.
"""

import urllib
import datetime
import json
import os

import requests
from requests.auth import HTTPBasicAuth
import pandas as pd


class AirflowRESTAPIV1:
    """
    A client for interacting with the Apache Airflow REST API.
    Supports retrieving DAGs, fetching DAG details, and triggering DAG runs.
    """

    headers = {"Content-Type": "application/json"}

    def __init__(self, api_url, username, password):
        """
        Initializes the AirflowRESTAPI instance with API credentials.

        :param api_url: Base URL of the Airflow API.
        :param username: Airflow API username.
        :param password: Airflow API password.
        """
        self.api_url = api_url
        self.username = username
        self.password = password
        self.auth = HTTPBasicAuth(username, password)

    def get(self, endpoint):
        """
        Sends a GET request to the specified API endpoint.

        :param endpoint: API endpoint to query.
        :return: Parsed JSON response or an empty dictionary on failure.
        """
        url = urllib.parse.urljoin(self.api_url, endpoint)
        response = requests.get(url, headers=self.headers, auth=self.auth)

        if response.status_code == 200:
            return response.json()

        print(f"Error {response.status_code}: {response.text}")
        return {}

    def post(self, endpoint, data):
        """
        Sends a POST request to the specified API endpoint.

        :param endpoint: API endpoint to send data to.
        :param data: Dictionary containing the request payload.
        :return: Parsed JSON response or an empty dictionary on failure.
        """
        url = urllib.parse.urljoin(self.api_url, endpoint)
        response = requests.post(url, json=data, headers=self.headers, auth=self.auth)

        if response.status_code in [200, 201]:
            return response.json()

        print(f"Error {response.status_code}: {response.text}")
        return {}

    def get_dags_list(self, include_all=False):
        """
        Retrieves the list of DAGs from the Airflow API.

        :param include_all: If True, returns all DAGs; otherwise, filters by the current user.
        :return: Pandas DataFrame containing DAG details.
        """
        columns = [
            "dag_id", "description", "fileloc", "owners", "is_active", "is_paused",
            "timetable_description", "last_parsed_time", "next_dagrun", "tags"
        ]

        endpoint = "dags"
        response = self.get(endpoint).get("dags", [])

        if not response:
            print("No DAGs found.")
            return pd.DataFrame(columns=columns)

        df = pd.DataFrame(response)[columns]
        df["tags"] = df["tags"].apply(lambda x: [elt["name"] for elt in x])  # Convert tags to list format

        if include_all:
            return df.sort_values(by="dag_id")

        # Filter DAGs owned by the current user
        return (
            df[df["owners"].apply(lambda owners: self.username in owners)]
            .reset_index(drop=True)
            .sort_values(by="dag_id")
        )

    def get_dag_details(self, dag_id, include_tasks=False):
        """
        Fetches detailed information for a specific DAG.

        :param dag_id: ID of the DAG to retrieve.
        :param include_tasks: If True, includes task details in the response.
        :return: Dictionary containing DAG details.
        """
        endpoint = f"dags/{dag_id}"
        dag = self.get(endpoint)

        endpoint = f"dags/{dag_id}/details"
        details = self.get(endpoint)

        endpoint = f"dags/{dag_id}/tasks"
        tasks = self.get(endpoint)

        num_tasks = len(tasks.get("tasks", []))  # Handle potential missing "tasks" key

        response = dag | details  # Merge dictionaries (Python 3.9+)
        response["num_tasks"] = num_tasks

        if include_tasks:
            response["tasks"] = tasks.get("tasks", [])

        return response

    def get_dag_tasks(self, dag_id):
        """
        Retrieves the list of tasks for a specific DAG.

        :param dag_id: ID of the DAG.
        :return: Pandas DataFrame containing task details.
        """
        columns = [
            "task_id", "operator_name", "owner", "params", "depends_on_past",
            "downstream_task_ids", "wait_for_downstream", "trigger_rule"
        ]

        endpoint = f"dags/{dag_id}/tasks"
        tasks = self.get(endpoint)

        return pd.DataFrame(tasks.get("tasks", []), columns=columns)

    def trigger_dag(self, dag_id, start_date, end_date):
        """
        Triggers a DAG run with the specified start and end dates.

        :param dag_id: ID of the DAG to trigger.
        :param start_date: Start date in YYYY-MM-DD format.
        :param end_date: End date in YYYY-MM-DD format.
        :return: Dictionary containing the API response.
        """
        endpoint = f"dags/{dag_id}/dagRuns"

        start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
        end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)

        data = {
            "conf": {},
            "dag_run_id": f"manual_run_{start_dt.strftime('%Y%m%dT%H%M%S')}",
            "data_interval_start": start_dt.isoformat(),
            "data_interval_end": end_dt.isoformat(),
            "logical_date": end_dt.isoformat(),
            "note": f"{self.username} triggered {dag_id} from {start_date} to {end_date}",
        }

        return self.post(endpoint, data=data)


class AirflowRESTAPI:
    """
    A client for interacting with the Apache Airflow REST API.
    Supports retrieving DAGs, fetching DAG details, and triggering DAG runs.
    """

    headers = {
        'Content-Type': 'application/json'
    }

    def __init__(self, base_url, api_endpoint, username, password):
        """
        Initializes the AirflowRESTAPI instance with API credentials.

        :param api_url: Base URL of the Airflow API.
        :param username: Airflow API username.
        :param password: Airflow API password.
        """
        self.base_url = base_url
        self.api_url = urllib.parse.urljoin(base_url, api_endpoint)
        self.username = username
        self.password = password
        
        self.auth = HTTPBasicAuth(username, password)
        self.data = {"username": self.username, "password": self.password}
        self.token = self.get_token(endpoint="auth/token")
        self.headers["Authorization"] = f"Bearer {self.token}"

    def get_token(self, endpoint):
        """
        Retrieves a bearer token for API authentication.
        :return: The token string if successful, otherwise None.
        """
        url = urllib.parse.urljoin(self.base_url, endpoint)
        
        # Send the POST request
        response = requests.post(url, headers=self.headers, data=json.dumps(self.data))
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        
        # If the request was successful, parse the JSON response
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        if access_token:
            print("Authentication successful! Token received.")
            return access_token
        else:
            print("Authentication failed: 'access_token' not found in response.")
    
    def get(self, endpoint):
        """
        Sends a GET request to the specified API endpoint.

        :param endpoint: API endpoint to query.
        :return: Parsed JSON response or an empty dictionary on failure.
        """
        url = urllib.parse.urljoin(self.api_url, endpoint)
        response = requests.get(url, headers=self.headers, data=json.dumps(self.data))

        if response.status_code == 200:
            return response.json()

        print(f"Error {response.status_code}: {response.text}")
        return {}

    def post(self, endpoint, data):
        """
        Sends a POST request to the specified API endpoint.

        :param endpoint: API endpoint to send data to.
        :param data: Dictionary containing the request payload.
        :return: Parsed JSON response or an empty dictionary on failure.
        """
        url = urllib.parse.urljoin(self.api_url, endpoint)
        # response = requests.post(url, json=data, headers=self.headers, auth=self.auth)
        # response = requests.post(url, json=data, headers=self.headers, data=json.dumps(self.data))
        response = requests.post(url, json=data, headers=self.headers)

        if response.status_code in [200, 201]:
            return response.json()

        print(f"Error {response.status_code}: {response.text}")
        return {}

    def get_dags_list(self, include_all=False):
        """
        Retrieves the list of DAGs from the Airflow API.

        :param include_all: If True, returns all DAGs; otherwise, filters by the current user.
        :return: Pandas DataFrame containing DAG details.
        """
        columns = [
            "dag_id", "description", "fileloc", "owners", "is_paused",
            "timetable_description", "last_parsed_time", "next_dagrun_logical_date", "tags"
        ]

        endpoint = "dags"
        response = self.get(endpoint).get("dags", [])

        if not response:
            print("No DAGs found.")
            return pd.DataFrame(columns=columns)

        df = pd.DataFrame(response)[columns]
        df["tags"] = df["tags"].apply(lambda x: [elt["name"] for elt in x])  # Convert tags to list format

        if include_all:
            return df.sort_values(by="dag_id")

        # Filter DAGs owned by the current user
        return (
            df[df["owners"].apply(lambda owners: self.username in owners)]
            .reset_index(drop=True)
            .sort_values(by="dag_id")
        )

    def get_dag_details(self, dag_id, include_tasks=False):
        """
        Fetches detailed information for a specific DAG.

        :param dag_id: ID of the DAG to retrieve.
        :param include_tasks: If True, includes task details in the response.
        :return: Dictionary containing DAG details.
        """
        endpoint = f"dags/{dag_id}"
        dag = self.get(endpoint)

        endpoint = f"dags/{dag_id}/details"
        details = self.get(endpoint)

        endpoint = f"dags/{dag_id}/tasks"
        tasks = self.get(endpoint)

        num_tasks = len(tasks.get("tasks", []))  # Handle potential missing "tasks" key

        response = dag | details  # Merge dictionaries (Python 3.9+)
        response["num_tasks"] = num_tasks

        if include_tasks:
            response["tasks"] = tasks.get("tasks", [])

        response = pd.DataFrame([response])
        response = response.T.reset_index().rename(columns={"index": "Key", 0: "Value"})

        return response

    def get_dag_tasks(self, dag_id):
        """
        Retrieves the list of tasks for a specific DAG.

        :param dag_id: ID of the DAG.
        :return: Pandas DataFrame containing task details.
        """
        columns = [
            "task_id", "operator_name", "owner", "params", "depends_on_past",
            "downstream_task_ids", "wait_for_downstream", "trigger_rule"
        ]

        endpoint = f"dags/{dag_id}/tasks"
        tasks = self.get(endpoint)

        return pd.DataFrame(tasks.get("tasks", []), columns=columns)

    def trigger_dag(self, dag_id, start_date, end_date):
        """
        Triggers a DAG run with the specified start and end dates.

        :param dag_id: ID of the DAG to trigger.
        :param start_date: Start date in YYYY-MM-DD format.
        :param end_date: End date in YYYY-MM-DD format.
        :return: Dictionary containing the API response.
        """
        endpoint = f"dags/{dag_id}/dagRuns"

        start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
        end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)

        data = {
            "conf": {},
            "dag_run_id": f"manual_run_{start_dt.strftime('%Y%m%dT%H%M%S')}",
            "data_interval_start": start_dt.isoformat(),
            "data_interval_end": end_dt.isoformat(),
            "logical_date": end_dt.isoformat(),
            "note": f"{self.username} triggered {dag_id} from {start_date} to {end_date}",
        }

        try:
            response = self.post(endpoint, data=data)
        except Exception as e:
            response = e
        
        return response

    def backfill_dag(self, dag_id, start_date, end_date, max_active_runs=1, run_backwards=False, dag_run_conf={}, reprocess_behavior=None):
        """
        Triggers a backfill for a DAG over a specified date range.

        :param dag_id: ID of the DAG to trigger.
        :param start_date: Start date in YYYY-MM-DD format.
        :param end_date: End date in YYYY-MM-DD format.
        :param max_active_runs: The number of DAG runs that can be active at once.
        :param run_backwards: If True, DAG runs are scheduled from the end date backwards.
        :param dag_run_conf: A JSON object containing configuration for the DAG run.
        :param reprocess_behavior: Behavior when a date has already been run. Options are 'rerun', 'clear', or 'dry_run'.
        :return: Dictionary containing the API response.
        """
        endpoint = f"backfills"

        start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
        end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)

        data = {
            "dag_id": dag_id,
            "from_date": start_dt.isoformat(),
            "to_date": end_dt.isoformat(),
            "run_backwards": run_backwards,
            "dag_run_conf": dag_run_conf,
            "reprocess_behavior": reprocess_behavior,
            "max_active_runs": max_active_runs,
        }

        try:
            response = self.post(endpoint, data=data)
        except Exception as e:
            response = e
        
        return response


def fetch_data(query, connection_id, output_file, html_file):
    """
    Fetches data from a database and saves it to a CSV file and an HTML file.
    :param query: SQL query to execute.
    :param connection_id: Database client.
    :param output_file: Path to the output CSV file.
    :param html_file: Path to the output HTML file.
    """
    # Get data
    print("Get data")
    df = connection_id.get_pandas_df(query)
    print("Data ok")
    df["color"] = df["nb_missing_dates"].apply(lambda x: "green" if x == 0 else "red")
    
    # Save data
    df.to_csv(output_file, index=False, sep=";")
    
    # Generate HTML Table Rows
    html = "\n".join([
        f"""
        <tr>
            <td>{row.check_date}</td>
            <td style="text-align: center;">{row.tableid}</td>
            <td>bibox.{row.tablename}</td>
            <td>{row.last_date}</td>
            <td>{row.load_date}</td>
            <td style="text-align: center; font-weight: bold; color: {row.color};">{row.status}</td>
            <td style="text-align: center;">{row.nb_missing_dates}</td>
        </tr>"""
        for _, row in df.iterrows()
    ])
    # Save HTML
    with open(html_file, "w") as f:
        f.write(html)


def extract_table_to_csv(table, connection_id):
    """
    Exports data from a source database table to a CSV file.
    
    :param table: Dictionary containing table information (src_table, dest_filename, sep).
    :param connection_id: Database client.
    """    
    
    # Get data
    print("Get Data...")
    df = connection_id.get_pandas_df(table["src_table"])
    
    # Save data
    print("Save Data...", table["dest_filename"])
    df.to_csv(table["dest_filename"], index=False, sep=table["sep"])


def bulk_insert_dataframe(table, rundt, source_connection_id, destination_connection_id, mount_base_dir, win_base_dir, na_rep="", rollback_days=0):
    """
    Bulk insert data from source to destination database table using a temporary CSV file.
    
    :param table: Dictionary containing table information (src_table, dest_table, operation, date_column, format_file, is_daily, stratify).
    :param rundt: The run date for data extraction.
    :param source_connection_id: Source database client.
    :param destination_connection_id: Destination database client.
    :param mount_base_dir: Base directory for temporary file storage (Linux/Mac).
    :param win_base_dir: Base directory for temporary file storage (Windows).
    :param na_rep: Representation for missing values in the CSV file.
    :param rollback_days: Number of days to roll back for monthly data extraction.
    """    
    
    # Build Queries
    print(f"\nTable : {table['src_table']} -> {table['dest_table']}")
    if table["operation"] == "replace":
        src_query = f"select * from {table['src_table']}"
        dest_query = f"TRUNCATE TABLE {table['dest_table']};"
    else:
        if table.get('is_daily'):
            src_query = f"select * from {table['src_table']} where {table['date_column']} = '{rundt}'::date"
            dest_query = f"DELETE FROM {table['dest_table']} WHERE {table['date_column']} = cast('{rundt}' as DATE);"
        else:
            src_query = f"select * from {table['src_table']} where {table['date_column']} = date_trunc('month', '{rundt}'::date)::date"
            # dest_query = f"DELETE FROM {table['dest_table']} WHERE {table['date_column']} = DATEADD(DAY, 1, EOMONTH(DATEADD(DAY, {rollback_days}, cast('{rundt}' as DATE)), -1));"
            dest_query = f"DELETE FROM {table['dest_table']} WHERE {table['date_column']} = DATEADD(month, DATEDIFF(month, 0, cast('{rundt}' as DATE)), 0);"

    # Get data
    print("Get data")
    print("Source query:", src_query)
    if table.get('stratify'):
        # Read data
        uniques_sql = f"select distinct {table['stratify']} from ({src_query}) foo;"
        uniques = source_connection_id.get_pandas_df(uniques_sql)
        uniques = uniques[table['stratify']].tolist()

        for i, v in enumerate(uniques):
            src_query_sub = f"select * from ({src_query}) foo where {table['stratify']} = '{v}'"
            print(src_query_sub)
            df = source_connection_id.get_pandas_df(src_query_sub)

            # Export data to CSV
            print("Export data to CSV")
            temp_filename = os.path.join(mount_base_dir, "tmp_" + table['dest_table'].split(".")[-1] + ".txt")
            windows_temp_filename = os.path.join(win_base_dir, os.path.split(temp_filename)[-1])
            if i == 0:
                df.astype(str).to_csv(temp_filename, index=False, header=True, sep=";", lineterminator="\r\n", encoding="utf-8", na_rep=na_rep)
            else:
                df.astype(str).to_csv(temp_filename, index=False, header=False, sep=";", lineterminator="\r\n", encoding="utf-8", mode="a", na_rep=na_rep)
    else:
        # Read data
        df = source_connection_id.get_pandas_df(src_query)

        # Export data to CSV
        print("Export data to CSV")
        temp_filename = os.path.join(mount_base_dir, "tmp_" + table['dest_table'].split(".")[-1] + ".txt")
        windows_temp_filename = os.path.join(win_base_dir, os.path.split(temp_filename)[-1])
        df.astype(str).to_csv(temp_filename, index=False, header=True, sep=";", lineterminator='\r\n', encoding="utf-8", na_rep=na_rep)
    
    # Delete existing data
    print("Delete existing data")
    destination_connection_id.run(dest_query)
    
    # Insert data
    print("Insert data")
    sql = f"""
    BULK INSERT {table['dest_table']}
    FROM '{windows_temp_filename}'
    WITH
    (
        FORMATFILE = '{os.path.join(win_base_dir, table['format_file'])}',
        FIRSTROW = 2,
        TABLOCK
    )
    """
    destination_connection_id.run(sql)
    
    # Clean up temporary file
    try:
        os.remove(temp_filename)
    except OSError as e:
        print(f"Error: {temp_filename} : {e.strerror}")


def bulk_insert_dataframe_db_to_db(table, rundt, source_connection_id, destination_connection_id, chunksize=10000):
    """
    Bulk insert data from source to destination database table using pandas DataFrame.
    
    :param table: Dictionary containing table information (src_table, dest_table, operation, date_column, format_file, is_daily, stratify).
    :param rundt: The run date for data extraction.
    :param source_connection_id: Source database client.
    :param destination_connection_id: Destination database client.
    :param chunksize: Number of rows per batch to insert.
    """
    # Build Queries
    print(f"\nTable : {table['src_table']} -> {table['dest_table']}")
    if table["operation"] == "replace":
        src_query = f"select * from {table['src_table']}"
        dest_query = f"truncate {table['dest_table']};"
    else:
        if table.get('is_daily'):
            src_query = f"select * from {table['src_table']} where {table['date_column']} = '{rundt}'::date"
            dest_query = f"delete from {table['dest_table']} WHERE {table['date_column']} = '{rundt}'::date;"
        else:
            src_query = f"select * from {table['src_table']} where {table['date_column']} = date_trunc('month', '{rundt}'::date)::date"
            dest_query = f"delete from {table['dest_table']} WHERE {table['date_column']} = date_trunc('month', '{rundt}'::date)::date;"

    if table.get('stratify'):
        # Get data
        print("Get data")
        print("Source query:", src_query)
        uniques_sql = f"select distinct {table['stratify']} from ({src_query}) foo;"
        uniques = source_connection_id.get_pandas_df(uniques_sql)
        uniques = uniques[table['stratify']].tolist()

        for i, v in enumerate(uniques):
            src_query_sub = f"select * from ({src_query}) foo where {table['stratify']} = '{v}'"
            print(src_query_sub)
            df = source_connection_id.get_pandas_df(src_query_sub)
            
            # Delete existing data
            print("Delete existing data")
            destination_connection_id.run(dest_query)
    
            # Insert data
            df.to_sql(
                name=table['dest_table'].split(".")[1],
                schema=table['dest_table'].split(".")[0],
                con=destination_connection_id.get_sqlalchemy_engine(),
                if_exists="append", ## Ensure table is truncated if needed
                chunksize=table.get('chunksize', chunksize),
                method="multi",
                index=False
            )
            
    else:
        # Get data
        print("Get data")
        print("Source query:", src_query)
        df = source_connection_id.get_pandas_df(src_query)
        
        # Delete existing data
        print("Delete existing data")
        destination_connection_id.run(dest_query)
    
        # Insert data
        df.to_sql(
            name=table['dest_table'].split(".")[1],
            schema=table['dest_table'].split(".")[0],
            con=destination_connection_id.get_sqlalchemy_engine(),
            if_exists="append", ## Ensure table is truncated if needed
            chunksize=table.get('chunksize', chunksize),
            method="multi",
            index=False
        )
