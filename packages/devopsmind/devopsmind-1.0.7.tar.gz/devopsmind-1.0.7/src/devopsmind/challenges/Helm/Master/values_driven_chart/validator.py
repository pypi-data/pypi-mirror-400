#!/usr/bin/env python3
import os
import yaml
import re

def validate():
    values_path = "mychart/values.yaml"
    deploy_path = "mychart/templates/deployment.yaml"

    if not os.path.exists(values_path):
        return False, "values.yaml missing."
    if not os.path.exists(deploy_path):
        return False, "deployment.yaml missing."

    try:
        values = yaml.safe_load(open(values_path))
    except Exception as e:
        return False, f"Invalid YAML in values.yaml: {e}"

    # Validate values.yaml content
    if values.get("replicaCount") != 3:
        return False, "replicaCount must be 3."

    image = values.get("image", {})
    if image.get("repository") != "nginx" or image.get("tag") != "alpine":
        return False, "image.repository must be nginx and tag alpine."

    content = open(deploy_path).read()

    # Replica count must reference values
    if not re.search(r"\.Values\.replicaCount", content):
        return False, "replicas must be driven from .Values.replicaCount."

    # Image must be values-driven (repository + tag)
    if not (
        re.search(r"\.Values\.image\.repository", content)
        and re.search(r"\.Values\.image\.tag", content)
    ):
        return False, "Image must be templated using values.yaml (repository and tag)."

    # Deployment name must be chart-derived
    if not (
        re.search(r"\.Chart\.Name", content)
        or re.search(r"include\s+\".*fullname.*\"", content)
    ):
        return False, "Deployment name must be derived from chart name."

    return True, "Helm Master challenge passed!"
