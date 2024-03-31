import socket
from typing import List

import requests
from rich import print
from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.panel import Panel
from rich.theme import Theme

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
env_ip = host_ip.split('.')[1]

# TODO: loop through yml setting
# K8S kschema service external IP
ip_map = {
    "60": "10.60.128.33:8081",     # dev/wu
    "120": "10.120.128.33:8081",   # stg/wu
    "180": "10.180.128.33:8081",   # prod/wu
    "181": "10.181.129.40:8081",   # prod/we
    "182": "10.182.128.131:8081",  # prod/uks
    "183": "10.183.129.98:8081",   # prod/auc
    "184": "10.184.129.98:8081",   # prod/sas
    "185": "10.185.128.91:8081",   # prod/jpe
    "186": "10.186.129.11:8081",   # prod/cac
    "187": "10.187.128.149:8081",  # prod/cin
    "188": "10.188.129.78:8081",   # prod/uaen
}

# base_url = f"http://{ip_map[env_ip]}/subjects/"
base_url = f"http://localhost:8080/subjects/"


class RecordHighlighter(RegexHighlighter):
    base_style = "schema."
    # TODO: fstring = f".*com.{company}.{team}.avro.(?P<record>(.*))ver.*"
    highlights = [r".*com.trendmicro.jaguar.avro.(?P<record>(.*))ver.*"]


class TopicHighlighter(RegexHighlighter):
    base_style = "schema."
    highlights = [r"\d+ (?P<topic>(.*))\-value.*"]


def request_kschema(url, kind: str):
    response = requests.get(url)
    response.encoding = "utf-8"
    if kind == "schema":
        result: List = eval(response.text)
    elif kind == "version":
        result: int = eval(response.text)
    else:
        raise NotImplementedError
    return result


def grab_version(origin_list: List) -> List:
    for idx, t in enumerate(origin_list):
        version = request_kschema(f"{base_url}{t}/versions", kind="version")
        padding = " " * (63 - len(t))
        origin_list[idx] = f"{t}{padding}ver: [bold green]{version[-1]}[/bold green]"
    return origin_list


def separate_schema(origin_list) -> (List, List):
    origin_list.sort()
    prefix = "com.trendmicro.jaguar"
    topic_based = []
    record_based = []

    for t in origin_list:
        if t.startswith(prefix):
            record_based.append(t)
        else:
            topic_based.append(t)
    return topic_based, record_based


def print_result(schema_topic: List, schema_record: List):
    theme = Theme({"schema.record": "bold violet", "schema.topic": "bold violet"})
    console = Console(highlighter=TopicHighlighter(), theme=theme)
    padding = "  "

    # TODO: Dynamic Paging
    print(Panel.fit(
        f"                         [bold orange3]Topic-Based[/bold orange3] Schema                          "))
    for idx, t in enumerate(schema_topic):
        if idx > 8:
            padding = " "
        console.print(f"[bold cyan]{idx + 1}[/bold cyan]{padding}{t}")

    console.highlighter = RecordHighlighter()
    padding = "  "
    print(Panel.fit(
        f"                         [bold orange3]Record-Based[/bold orange3] Schema                         "))
    for idx, t in enumerate(schema_record):
        if idx > 8:
            padding = " "
        console.print(f"[bold cyan]{idx + 1}[/bold cyan]{padding}{t}")


if __name__ == "__main__":
    content = request_kschema(base_url, kind="schema")
    grab_version(content)
    p, q = separate_schema(content)
    print_result(p, q)
