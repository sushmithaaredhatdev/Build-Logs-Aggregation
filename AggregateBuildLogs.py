import subprocess
import json
from pandas.io.json import json_normalize
import requests
import numpy as np


def get_builds():
    """Used to get the total list of builds from a openshift project."""
    subprocess.getoutput("oc get builds --output=json > allbuildsfromproject1.json")
    with open("allbuildsfromproject1.json", "r") as read_file:
        data = json.load(read_file)
    tabular_data = json_normalize(data['items'])
    build_pod_names = (tabular_data['metadata.annotations.openshift.io/build.pod-name']).tolist()
    api_version_list = []
    kind_list = []
    meta_data_list = []
    for i in data['items']:
        api_version = i['apiVersion']
        api_version_list.append(api_version)
        kind = i['kind']
        kind_list.append(kind)
        meta_data_list.append(i)
    return build_pod_names, api_version_list, kind_list, meta_data_list


def get_logs():
    """The method gets the list of log files of every build and posts them to the API."""
    get_build_info = get_builds()
    pod_list=get_build_info[0]
    api_version_list = get_build_info[1]
    kind_list = get_build_info[2]
    meta_data_list = get_build_info[3]
    build_logs_endpoint_url = "http://user-api-thoth-test-core.cloud.paas.upshift.redhat.com/api/v1/buildlog"
    clean_pod_list = ['N/A' if x is np.nan else x for x in pod_list]
    for index, pod in enumerate(clean_pod_list):
        logs = subprocess.getoutput("oc logs "+pod)
        log_info = {'log': logs, 'apiVersion': api_version_list[index], 'kind': kind_list[index], 'metadata': meta_data_list[index] }
        response = requests.post(build_logs_endpoint_url, json=log_info)
        print(response.status_code)
        print(response.json())
        break
    return "success"


get_logs()
