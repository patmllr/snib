import random
import string
import subprocess
import tempfile
from pathlib import Path

import pytest


def random_cs_code():
    return f"""
using UnityEngine;

public class {''.join(random.choices(string.ascii_uppercase, k=6))} : MonoBehaviour
{{
    void Start() {{
        Debug.Log("Hello Unity");
    }}
}}
"""


def create_unity_project_structure(base_path, depth=3, files_per_dir=5):
    dirs_to_create = [
        "Assets/Scripts",
        "Assets/Scenes",
        "Assets/Prefabs",
        "Assets/Materials",
        "ProjectSettings",
    ]
    for d in dirs_to_create:
        dir_path = base_path / d
        dir_path.mkdir(parents=True, exist_ok=True)
        if "Scripts" in d:
            for i in range(files_per_dir):
                file_path = dir_path / f"Script_{i}.cs"
                file_path.write_text(random_cs_code())
        elif "Scenes" in d:
            for i in range(files_per_dir):
                file_path = dir_path / f"Scene_{i}.unity"
                file_path.write_text("// dummy unity scene")
        else:
            for i in range(files_per_dir):
                file_path = dir_path / f"file_{i}.txt"
                file_path.write_text("Dummy content")


def test_stress_unity_project():
    with tempfile.TemporaryDirectory() as tmp_dir:
        project_path = Path(tmp_dir) / "UnityProject"
        project_path.mkdir()
        create_unity_project_structure(project_path, files_per_dir=10)

        # snib init
        result_init = subprocess.run(
            ["snib", "init", "--preset", "unity"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        print(result_init.stdout)
        if result_init.returncode != 0:
            print(result_init.stderr)
            raise RuntimeError("snib init failed")

        # snib scan
        result_scan = subprocess.run(
            ["snib", "scan", "--force"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        print(result_scan.stdout)
        if result_scan.returncode != 0:
            print(result_scan.stderr)
            raise RuntimeError("snib scan failed")


# PASSED pytest tests/test_snib_unity.py -v
