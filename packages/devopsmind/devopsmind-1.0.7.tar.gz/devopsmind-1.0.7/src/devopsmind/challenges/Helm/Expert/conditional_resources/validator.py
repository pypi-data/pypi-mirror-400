#!/usr/bin/env python3
import os
import yaml
import re

def validate():
    values_path = "mychart/values.yaml"
    cm_path = "mychart/templates/configmap.yaml"

    if not os.path.exists(values_path):
        return False, "values.yaml missing."
    if not os.path.exists(cm_path):
        return False, "configmap.yaml missing."

    try:
        values = yaml.safe_load(open(values_path))
    except Exception as e:
        return False, f"Invalid YAML in values.yaml: {e}"

    cfg = values.get("config", {})
    if cfg.get("enabled") is not True:
        return False, "config.enabled must be true."
    if cfg.get("message") != "Hello Helm":
        return False, "config.message must be 'Hello Helm'."

    content = open(cm_path).read()

    # Must be conditionally rendered based on config.enabled
    if not re.search(r"if\s+.*\.Values\.config\.enabled", content):
        return False, "ConfigMap must be conditionally rendered using config.enabled."

    # Must reference config.message
    if not re.search(r"\.Values\.config\.message", content):
        return False, "ConfigMap must reference .Values.config.message."

    # Name must be derived from chart name
    if not (
        re.search(r"\.Chart\.Name", content)
        or re.search(r"include\s+\".*fullname.*\"", content)
    ):
        return False, "ConfigMap name must be derived from chart name."

    return True, "Helm Expert challenge passed!"
