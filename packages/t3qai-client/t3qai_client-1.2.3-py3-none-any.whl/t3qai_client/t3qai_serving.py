# coding: utf-8
# Copyright [t3q]
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
t3qai_serving
-------------
Source that starts when the inference model is deployed
"""

import os
import io
import sys
import json
import filetype
import logging
import zipfile
import importlib
import re

import pandas as pd
from urllib import parse
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Request, Response, Body  # type: ignore
from fastapi.responses import StreamingResponse, PlainTextResponse  # type: ignore

from t3qai_client.t3qai_helper import DownloadFile as DownloadFile
from t3qai_client.t3qai_helper import inference_set_logger

SERVING_PARAMS_FILE = "serving_params.json"
POD_VOLUME_PATH = "/cache"

inference_set_logger()

app = FastAPI()


def robust_data_parser(data):
    def fix_quotes(s):
        # Replace single quotes with double quotes for keys
        s = re.sub(r"'([^']+)':", r'"\1":', s)

        # Replace single-quoted string values and escape double quotes and backslashes within them
        def replace_value(match):
            value = match.group(1)
            # Escape backslashes and double quotes in the value
            value = value.replace("\\", "\\\\").replace('"', '\\"')
            return ': "{}"'.format(value)

        s = re.sub(r":\s*'([^']*)'", replace_value, s)
        # Replace None with null
        s = s.replace(": None", ": null")
        return s

    def recursive_parse(data):
        if isinstance(data, str):
            data = data.strip()
            # Attempt to parse as JSON
            try:
                return recursive_parse(json.loads(data))
            except json.JSONDecodeError:
                return data
        elif isinstance(data, list):
            return [recursive_parse(item) for item in data]
        elif isinstance(data, dict):
            # Ensure specific fields remain as strings
            for key in data:
                if isinstance(data[key], str):
                    data[key] = str(recursive_parse(data[key]))
                else:
                    data[key] = recursive_parse(data[key])
            return data
        else:
            return data

    try:
        # 1. Data decoding
        if data is None or data == "":
            raise ValueError("Input data is empty.")
        if isinstance(data, bytes):
            try:
                decoded_data = data.decode("utf-8")
            except UnicodeDecodeError:
                raise ValueError("Failed to decode data with UTF-8 encoding.")
            # 2. String preprocessing
            cleaned_data = fix_quotes(decoded_data)
            # 3. JSON parsing attempt
            try:
                parsed_data = json.loads(cleaned_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse data with json.loads: {str(e)}")
        elif isinstance(data, str):
            # 2. String preprocessing
            cleaned_data = fix_quotes(data)
            # 3. JSON parsing attempt
            try:
                parsed_data = json.loads(cleaned_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse data with json.loads: {str(e)}")
        elif isinstance(data, dict) or isinstance(data, list):
            # Data is already parsed; proceed to recursive parsing
            parsed_data = data
        else:
            raise ValueError("Unsupported data type.")

        # 4. Recursively parse nested strings
        parsed_data = recursive_parse(parsed_data)

        return parsed_data

    except ValueError as ve:
        print(f"Value error occurred: {str(ve)}")
        return None
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        return None


@app.post("/inference")
async def inference(request: Request):
    """
    Receive json and proceed with inference

    Parameters
    ----------
    json data from request body
    """

    print("inference async")

    results = None

    try:
        data = await request.body()
        data = robust_data_parser(data.decode())
        try:
            if "test_data" in data:
                test_data = data["test_data"]
                if isinstance(test_data, dict):
                    if test_data.get("columns"):
                        test_data["values"] = robust_data_parser(
                            test_data.get("values")
                        )
                        if test_data.get("columns") and test_data.get("values"):
                            test_data = pd.DataFrame(
                                test_data.get("values"),
                                columns=test_data.get("columns"),
                            )
                    elif test_data.get("values"):
                        test_data = robust_data_parser(test_data.get("values"))
                else:
                    test_data = robust_data_parser(test_data)
        except Exception as data_e:
            test_data = test_data
        # inference_ai_module = importlib.import_module(inference_service_module)
        results = getattr(inference_ai_module, inference_dataframe_function)(
            test_data, model_info_dict
        )

    except Exception as e:
        logging.exception(e)
        results = {"result": "error", "msg": str(e)}
    return results


@app.post("/inference_file")
async def inference_file(
    files: List[UploadFile] = File(...), data: Optional[str] = Body(None)
):
    """
    Receive the file and proceed with inference along with additional parameters.

    Parameters
    ----------
    files: list of UploadFile objects
    data: dictionary containing additional parameters
    """

    # inference_ai_module = importlib.import_module(inference_service_module)

    # decode filename
    files_length = len(files)

    for i in range(files_length):
        files[i].filename = parse.unquote(files[i].filename)

    # Pass the additional data parameters to the inference function
    if data is None:
        results = getattr(inference_ai_module, inference_file_function)(
            files, model_info_dict
        )
    else:
        test_data = robust_data_parser(data)
        results = getattr(inference_ai_module, inference_file_function)(
            files, model_info_dict, test_data
        )

    # 1. inference result = 1 file
    if isinstance(results, DownloadFile):
        download_file = results
        file_contents = download_file.file_obj.read()

        if _is_image_file(file_contents):
            # print('decoded file name =', download_file.file_name.decode('iso-8859-1'))
            return _make_image_response(file_contents, download_file.file_name)
        else:
            return _make_binary_response(file_contents, download_file.file_name)

    # 2. inference result >= 2 file
    elif (
        isinstance(results, list)
        and len(results) > 0
        and isinstance(results[0], DownloadFile)
    ):
        # multi file to zip
        zip_buffer = io.BytesIO()

        # result_zip = zipfile.ZipFile(zip_buffer, 'w')
        with zipfile.ZipFile(zip_buffer, "w") as result_zip:
            for result in results:
                result_zip.writestr(result.file_name, result.file_obj.read())
        # result_zip.close()
        res = _make_zip_response(zip_buffer.getvalue())
        return res

    # 3. inference result = data (not file)
    else:
        results = str(results)
        return PlainTextResponse(results)


def _is_image_file(file_contents):
    file_bytes = io.BytesIO(file_contents)
    guess = filetype.guess(file_bytes)
    if guess:
        return guess.mime.startswith("image")


def _make_image_response(file_contents, file_name):
    file_bytes = io.BytesIO(file_contents)
    res = StreamingResponse(content=file_bytes, media_type="image/png")
    url_file_name = parse.quote(file_name)
    res.headers["X-filename"] = url_file_name
    return res


def _make_binary_response(file_contents, file_name):
    res = Response(content=file_contents, media_type="application/octet-stream")
    url_file_name = parse.quote(file_name)
    res.headers["X-filename"] = url_file_name
    return res


def _make_zip_response(file_contents):
    res = Response(content=file_contents, media_type="application/x-zip-compressed")
    today_date = datetime.now().strftime("%Y%m%d%H%M%S")
    res.headers["X-filename"] = "inference_results_" + today_date + ".zip"
    return res


file_path = f"{POD_VOLUME_PATH}/{SERVING_PARAMS_FILE}"

file_exsit = os.path.isfile(file_path)
params = None
if file_exsit:
    with open(file_path, "r") as f:
        params = json.loads(f.read())

model_id = params["model_id"]
log_path = params["log_path"]
workspace = params["workspace"]
algo_path = params["algo_path"]


# config 파일의 env 정보 받기
inference_service_module = os.getenv("inference_service_module", "inference_service")
init_model_function = os.getenv("init_model_function", "init_model")
inference_dataframe_function = os.getenv(
    "inference_dataframe_function", "inference_dataframe"
)
inference_file_function = os.getenv("inference_file_function", "inference_file")

sys.path.append(algo_path)

inference_ai_module = importlib.import_module(inference_service_module)
model_info_dict = getattr(inference_ai_module, init_model_function)()
