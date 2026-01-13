# -*- coding: utf-8 -*-
"""Top-level package for twinthread."""
import io

from _plotly_utils.utils import PlotlyJSONEncoder

from .jupyter import register_jupyter
from .string_handling import task_string_to_context

__author__ = """Brad Johnson"""
__email__ = "brad.johnson@twinthread.com"
__version__ = "1.5.0"

import re
import json
import simplejson
import requests
import pandas as pd
from io import StringIO
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from datetime import datetime


def subplot_to_fig(subplot):
    if isinstance(subplot, Figure):
        return subplot
    fig = plt.figure()
    fig.axes.append(subplot)
    return fig


def do_login(base_url, username):
    import getpass
    bi_key = getpass.getpass(f"Enter Active BI Key from {base_url}/settings/security-keys: ")
    response = requests.post(
        f"{base_url}/api/Account/TokenExchange",
        json={
            "username": username,
            "key": bi_key
        },
    )
    if response.status_code != 200:
        raise Exception("Invalid credentials")

    print("Login succeeded")

    return response.json()["access_token"]


def select_keys(obj, keys):
    # print("filtered", {k:v for k, v in obj.items() if k not in keys})
    return {k: v for k, v in obj.items() if k in keys}


default_keys = [
    "name",
    "operationId",
    "status",
    "modelId",
    "assetModelId",
    "taskId",
    "description",
    "executionLevel",
    "isActive",
    "type",
]

import os


def mkdir(name):
    try:
        os.stat(name)
    except Exception as e:
        os.mkdir(name)


def plotlyfig2json(fig, fpath=None, context_parameters={}):
    """
    Serialize a plotly figure object to JSON so it can be persisted to disk.
    Figures persisted as JSON can be rebuilt using the plotly JSON chart API:

    http://help.plot.ly/json-chart-schema/

    If `fpath` is provided, JSON is written to file.

    Modified from https://github.com/nteract/nteract/issues/1229
    """
    redata = json.loads(json.dumps(fig["data"], cls=PlotlyJSONEncoder))
    relayout = json.loads(json.dumps(fig["layout"], cls=PlotlyJSONEncoder))
    context_parameters = simplejson.dumps(context_parameters, ignore_nan=True)
    fig_json = json.dumps(
        {"data": redata, "layout": relayout, "contextParameters": context_parameters}
    )

    if fpath:
        with open(fpath, "w") as outfile:
            json.dump(fig_json, outfile)
    else:
        return fig_json


def filter_results(results, search_text="", keys=default_keys):
    return [
        select_keys(result, keys)
        for result in results
        if search_text.lower() in result["name"].lower()
    ]


class TwinThreadClient:
    def __init__(self, base_url="https://dev.twinthread.com"):
        self.__access_token = "UNAUTHORIZED"
        self.__base_url = base_url
        self.__context = {}

        self.__files = []
        self.__request_id = None
        self.__input_data = None
        self.__username = None
        self.__topics_df = None

    def login(self, username):
        self.__access_token = do_login(self.__base_url, username)
        self.__username = username

    def __auth_check(self):
        if self.__access_token == "UNAUTHORIZED":
            raise Exception("Client must be authorized for this action.")
        return True

    def __post_base(self, route, body):
        self.__auth_check()
        user_agent = f"twinthread-pip/{__version__} user: {self.__username}"
        headers = {"Authorization": f"Bearer {self.__access_token}",
                   "User-Agent": user_agent}
        data = {**self.__context, **body}
        response = requests.post(
            f"{self.__base_url}/api{route}", json=data, headers=headers
        )

        if response.status_code != 200:
            raise Exception("Request failed")

        return response

    def __post_request(self, route, data):
        self.__auth_check()
        url = f"{self.__base_url}/api{route}"
        user_agent = f"twinthread-pip/{__version__} user: {self.__username}"
        headers = {"Authorization": f"Bearer {self.__access_token}",
                   "User-Agent": user_agent}
        response = requests.post(
            url, json=data, headers=headers
        )
        if response.status_code != 200:
            raise Exception("Request failed")
        return response

    def __post(self, route, body):
        response = self.__post_base(route, body)
        try:
            return response.json()
        except:
            raise Exception("Invalid server response. Please check query.")

    def __post_data(self, route, body):
        response = self.__post_base(route, body)
        return pd.read_csv(StringIO(response.text))

    def __require_model_context(self):
        if "modelId" not in self.__context:
            raise Exception(
                "Context Required: Please set API context to a model or pass one in as an argument to this function."
            )
        return True

    def __require_instance_context(self):
        if "assetModelId" not in self.__context or "modelId" not in self.__context:
            raise Exception(
                "Context Required: Please set API context to a model instance or pass one in as an argument to this function."
            )
        return True

    def __require_operation_context(self):
        if (
                "assetModelId" not in self.__context
                or "modelId" not in self.__context
                or "operationId" not in self.__context
        ):
            raise Exception(
                "Context Required: Please set API context to a model instance or pass one in as an argument to this function."
            )
        return True

    def __require_task_context(self):
        if (
                "assetModelId" not in self.__context
                or "modelId" not in self.__context
                or "operationId" not in self.__context
                or "taskId" not in self.__context
        ):
            raise Exception(
                "Context Required: Please set API context to a task or pass one in as an argument to this function."
            )
        return True

    def set_context(self, context):
        if isinstance(context, str):
            try:
                context = task_string_to_context(context)
            except Exception as e:
                print(e)
                pass

        # if context.get("name", False):
        #     print("Set context to:", context["name"])
        # else:
        #     print("Context set.")
        self.__context = context

    def get_context(self):
        return self.__context

    def __get_operation(self):
        self.__require_operation_context()
        return self.__post("/Model/Index", {})

    def get_org(self):
        self.__require_operation_context()
        return self.__post("/Model/Index", {})

    def get_output_topics(self):
        context = self.get_context()
        data = {
            'assetModelId': context['assetModelId'],
            'showAll': True

        }
        route = '/Model/ListTopics'
        response = self.__post_request(route, data)

        topics_ls = response.json()
        topics_df = pd.DataFrame(topics_ls)
        view = ['topicName', 'topicId', 'IsActive']
        if len(topics_df) > 0 and len(set(topics_df.columns).intersection(view)) == len(view):
            output_mask = topics_df['topicType'] == 12
            active_mask = topics_df['IsActive'] == True
            output_topics_df = topics_df[view].loc[output_mask & active_mask]
            self.__topics_df = output_topics_df
            return output_topics_df
        print('no model output topics available')
        self.__topics_df = topics_df
        return topics_df

    def list_models(self, search_text=""):
        models = self.__post("/Model/List", {})
        return filter_results(models, search_text)

    def list_model_instances(self, model, search_text=""):
        instances = self.__post("/Search/ListModelInstances", model)
        return filter_results(instances, search_text)

    def list_instance_operations(self, instance, search_text=""):
        operations = self.__post("/Model/ListOperations", instance)
        return filter_results(operations, search_text)

    def get_tasks(self, search_text="", filter=True):
        operation = self.__get_operation()
        tasks = operation.get("tasks", [])
        if filter:
            return filter_results(tasks, search_text)
        else:
            return tasks

    def get_task(self, context):
        operation = self.__post("/Model/Index", context)

        matches = [
            t for t in operation.get("tasks", []) if t["taskId"] == context["taskId"]
        ]
        if len(matches) > 0:
            return matches[0]

        raise Exception("Could not find task.")

    def get_instance_content(self):
        self.__require_instance_context()
        return self.__post("/Model/ListContent", {})

    def _update_task_code(self, task, code):
        configuration = json.loads(task["configuration"])
        configuration["pythonCode"] = code
        task["configuration"] = json.dumps(configuration)
        return self.__post("/Model/UpdateTask", task)

    def get_input_data(self, task={}):
        if self.__input_data is not None:
            return self.__input_data

        if isinstance(task, str):
            task = task_string_to_context(task)

        return self.__post_data(
            "/Model/ExportPortData",
            {**task, "portId": "input,dataset", "useAttachment": False},
        )

    def get_output_data(self, task={}):
        if isinstance(task, str):
            task = task_string_to_context(task)
        self.__require_task_context()
        return self.__post_data(
            "/Model/ExportPortData",
            {**task, "portId": "dataset", "useAttachment": False},
        )

    def _store_trained_model(self, model):
        import dill
        self.__trained_model = dill.dumps(model)

    def _get_trained_model_str(self):
        if not self.__trained_model:
            return None
        return self.__trained_model

    def _get_trained_model(self):
        import dill
        if not self.__trained_model:
            return None
        return dill.loads(self.__trained_model)

    def _register_model_class(self, ModelClass):
        self.__ModelClass = ModelClass

    def _get_registered_model_class(self):
        return self.__ModelClass

    def _start_run(self, request_id, input_data):
        self.__request_id = request_id
        self.__files = []
        self.__input_data = input_data

    def _get_files(self):
        return self.__files

    def __get_response_type(self, type):
        return (
            "text/csv"
            if type is "table"
            else "application/json"
            if type is "json"
            else "arraybuffer"
        )

    def __get_file_suffix(self, file_type):
        return ".json" if file_type == "json" else ".png" if file_type == "png" else ""

    def __write_file_contents(self, file_type, filename, contents):
        response_type = self.__get_response_type(file_type)

        content_type = "b" if response_type is "arraybuffer" else ""
        file = open(filename, "w" + content_type)
        try:
            file.write(contents.read())
        except Exception as e:
            file.write(contents)
        file.close()

    def __save_local_file(self, file_type, name, contents):
        filename = re.sub(r"\W+", "", name).lower()
        print(filename)
        mkdir("./tasks")
        mkdir(f"./tasks/{self.__request_id}")
        path = f"./tasks/{self.__request_id}/{filename}"

        self.__write_file_contents(file_type, path, contents)
        self.__files.append((file_type, name, path))

    def __save_remote_file(self, file_type, name, contents):
        blob_name = re.sub(r"\W+", "", name).lower()
        file_suffix = (
            ".json" if file_type == "json" else ".png" if file_type == "png" else ""
        )
        filename = f"{blob_name}{file_suffix}"
        blob_name = f"{self.__context['assetModelId']}_{self.__context['taskId']}_{blob_name}_org_i0{file_suffix}"

        self.__auth_check()

        self.__write_file_contents(file_type, filename, contents)

        from requests_toolbelt import MultipartEncoder

        fields = {
            "assetModelId": str(self.__context["assetModelId"]),
            "taskId": str(self.__context["taskId"]),
            "name": blob_name,
            "description": name,
            "file": (blob_name, open(filename, "rb"), "text/csv"),
        }
        print(fields)
        m = MultipartEncoder(
            fields=fields
        )

        headers = {
            "Authorization": f"bearer {self.__access_token}",
            "Content-Type": m.content_type,
        }

        p = requests.post(
            f"{self.__base_url}/api/Model/ImportTaskData", data=m, headers=headers
        )

    def save_plotly(self, fig, name=""):
        json = plotlyfig2json(fig)
        if self.__request_id is not None:
            self.__save_local_file("json", name, json)
        else:
            self.__save_remote_file("json", name, json)

        print("Saved plotly", name)

    def save_image(self, fig, name=""):
        fig = subplot_to_fig(fig)
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)

        if self.__request_id is not None:
            self.__save_local_file("png", name, buf)
        else:
            self.__save_remote_file("png", name, buf)

        print("Saved image", name)

    def save_table(self, table, name=""):
        if not isinstance(table, pd.DataFrame):
            raise ValueError("Table must be a pandas dataframe, not " + type(table))

        if name == "":
            name = "dataset"

        if self.__request_id is not None:
            self.__save_local_file("table", name, table.to_csv(index=False))
        else:
            self.__save_remote_file("table", name, table.to_csv(index=False))

        print("Saved table", name)

    def save_output_dataset(self, table):
        self.save_table(table, "dataset")

    def get_current_utc_time(self):
        utc_now = datetime.utcnow()
        return utc_now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def format_utc_timestamp(self, timestamp_str):
        try:
            # Parse the input timestamp string into a datetime object
            parsed_time = datetime.fromisoformat(timestamp_str)
        except ValueError:
            try:
                # Attempt to parse with other common formats
                parsed_time = datetime.strptime(timestamp_str, "%a, %d %b %Y %H:%M:%S %Z")
            except ValueError:
                raise ValueError("Input string is not a valid UTC timestamp.")

        # Format the datetime object to the desired string format
        return parsed_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def validate_output_property(self, property_id):
        if self.__topics_df is None:
            topics_df = self.get_output_topics()
        else:
            topics_df = self.__topics_df

        if property_id not in topics_df['topicId'].map(int).to_list():
            raise ValueError(
                f'Invalid PropertyId: {property_id} is not a model output topic. See available topics by running client.get_output_topics()')

    def update_output_property_value(self, property_id, value, utc_timestamp_str=None):

        if utc_timestamp_str is None:
            utc_timestamp_str = self.get_current_utc_time()

        utc_timestamp_str = self.format_utc_timestamp(utc_timestamp_str)

        self.validate_output_property(property_id)

        data = {
            "PropertyId": f"{property_id}",
            "Value": f"{value}",
            "Timestamp": utc_timestamp_str
        }
        route = '/property/UpdateValue'

        response = self.__post_request(route, data)
        property_name = self.__topics_df.set_index('topicId').loc[property_id]['topicName']
        if response.status_code == 200:
            print(f'Updated Property {property_name} to {value} at {utc_timestamp_str}')
        else:
            print(f'Failed to update Property {property_name} to {value} at {utc_timestamp_str} | Response Code: {response.status_code}')


