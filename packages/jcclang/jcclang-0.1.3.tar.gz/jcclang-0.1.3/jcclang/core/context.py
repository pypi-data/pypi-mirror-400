import argparse
import os
import time
import uuid

_forced_platform = None

parser = argparse.ArgumentParser(description='env')
parser.add_argument("--CURRENT_PLATFORM", help="platform name", default="None")
parser.add_argument("--GATEWAY_ADDR", help="url", default="None")
parser.add_argument("--USER_ID", help="userID", default="None")
parser.add_argument("--JCS_ADDR", help="JCS_ADDR", default="None")
parser.add_argument("--JCS_AK", help="JCS_AK", default="None")
parser.add_argument("--JCS_SK", help="JCS_SK", default="None")

parser.add_argument("--JOBHUB_ADDR", help="JOBHUB_ADDR", default="None")
parser.add_argument("--JOBHUB_PORT", help="JOBHUB_PORT", default="None")
parser.add_argument("--JOBHUB_JOBSET_ID", help="JOBHUB_JOBSET_ID", default="None")
parser.add_argument("--JOBHUB_JOB_ID", help="JOBHUB_JOB_ID", default="None")
parser.add_argument("--JOBHUB_SECRET", help="JOBHUB_SECRET", default="None")
args, unknown = parser.parse_known_args()


def default_context():
    return {
        "trace_id": str(uuid.uuid4()),
        "timestamp": int(time.time()),
        "logger": None  # 可注入 get_logger("task-name")
    }


def set_forced_platform(name: str):
    global _forced_platform
    _forced_platform = name


def get_platform():
    if _forced_platform:
        return _forced_platform
    if args.CURRENT_PLATFORM != "None":
        return args.CURRENT_PLATFORM
    return _forced_platform or os.environ.get("CURRENT_PLATFORM", "local")


def get_gateway_addr():
    if args.GATEWAY_ADDR != "None":
        return args.GATEWAY_ADDR
    return os.environ.get("GATEWAY_ADDR", "")


def get_jcs_addr():
    if args.JCS_ADDR != "None":
        return args.JCS_ADDR
    return os.environ.get("JCS_ADDR", "")


def get_jcs_ak():
    if args.JCS_AK != "None":
        return args.JCS_AK
    return os.environ.get("JCS_AK", "")


def get_jcs_sk():
    if args.JCS_SK != "None":
        return args.JCS_SK
    return os.environ.get("JCS_SK", "")


def get_user_id():
    if args.USER_ID != "None":
        return args.USER_ID
    return os.environ.get("USER_ID", 0)


def get_jobhub_addr():
    if args.JOBHUB_ADDR != "None":
        return args.JOBHUB_ADDR
    return os.environ.get("JOBHUB_ADDR", "")


def get_jobhub_port():
    if args.JOBHUB_PORT != "None":
        return args.JOBHUB_PORT
    return os.environ.get("JOBHUB_PORT", 0)


def get_jobhub_jobset_id():
    if args.JOBHUB_JOBSET_ID != "None":
        return args.JOBHUB_JOBSET_ID
    return os.environ.get("JOBHUB_JOBSET_ID", "")


def get_jobhub_job_id():
    if args.JOBHUB_JOB_ID != "None":
        return args.JOBHUB_JOB_ID
    return os.environ.get("JOBHUB_JOB_ID", "")


def get_jobhub_secret():
    secret = os.environ.get("JOBHUB_SECRET", "")
    if args.JOBHUB_SECRET != "None":
        secret = args.JOBHUB_SECRET
    return bytes(secret, "utf-8")
