#!/usr/bin/env python

##########################################################################################
# Copyright (c) 2023 Nordic Semiconductor ASA. All Rights Reserved.
#
# The information contained herein is confidential property of Nordic Semiconductor ASA.
# The use, copying, transfer or disclosure of such information is prohibited except by
# express written agreement with Nordic Semiconductor ASA.
##########################################################################################

import json
import functools
import subprocess
from websockets.sync.client import connect
from ciatools.logger import get_logger

logger = get_logger()

def send_messages(url, messages):
    with connect(url, origin="foo") as ws:
        data = ws.recv()
        logger.debug(data)
        data = json.loads(data)
        response = []
        if data["message"] != "ready":
            raise RuntimeError(f"Callbox not ready: {data}")
        for i in messages:
            ws.send(json.dumps(i))
            data = ws.recv()
            logger.debug(data)
            data = json.loads(data)
            if "error" in data:
                raise RuntimeError(f"Callbox response error: {data}")
            response.append(data)
        return response

def ue_list_get(url):
    message = {"message": "ue_get"}
    return send_messages(url, [message])

def cell_gain_set(url, cell_id, gain):
    if gain > 0 or gain < -200:
        raise RuntimeError("Gain outside range -200 - 0")
    message = {"message": "cell_gain", "cell_id": cell_id, "gain": gain}
    send_messages(url, [message])

lte_cell_gain_set = functools.partial(cell_gain_set, 1)
nbiot_cell_gain_set = functools.partial(cell_gain_set, 2)

def cell_gain_set_default(url):
    messages = [
        {"message": "cell_gain", "cell_id": 1, "gain": -10},
        {"message": "cell_gain", "cell_id": 2, "gain": -10}
    ]
    send_messages(url, messages)

def ssh_execute(host, commands, skip_host_key_check=False):
    """
    Execute a list of commands on a remote host via SSH.
    
    Args:
        host: Host name or user@hostname for SSH connection
        commands: List of command strings to execute
    
    Returns:
        int: Error code (0 for success, non-zero for failure)
    """
    errcode = 0
    for cmd in commands:
        logger.debug(f"Executing on {host}: {cmd}")
        if skip_host_key_check:
            ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", host, cmd]
        else:
            ssh_cmd = ["ssh", host, cmd]
        try:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True)
            logger.debug(f"Command output: {result.stdout}")
            if result.stderr:
                logger.debug(f"Command stderr: {result.stderr}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with error code {e.returncode}: {e.stderr}")
            errcode = e.returncode
            break
        except Exception as e:
            logger.error(f"SSH execution error: {e}")
            errcode = 1
            break
    return errcode
