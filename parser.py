import zipfile
import tempfile
import json
import pandas as pd


def analyze_zip(uploaded_file):

    command_rows = []
    variable_rows = []
    package_rows = []
    tasks_found = []

    with tempfile.NamedTemporaryFile(delete=False) as tmp:

        tmp.write(uploaded_file.read())

        with zipfile.ZipFile(tmp.name, "r") as zip_ref:

            files = zip_ref.namelist()

            for file_name in files:

                short_name = file_name.split("/")[-1]

                if not short_name:
                    continue

                # Process only task files (no extension)
                if "." in short_name:
                    continue

                try:

                    content = zip_ref.read(
                        file_name
                    ).decode(
                        "utf-8",
                        errors="ignore"
                    )

                    data = json.loads(content)

                    task_name = short_name

                    tasks_found.append(
                        {
                            "file": file_name
                        }
                    )

                    # Variables
                    extract_variable_definitions(
                        data,
                        task_name,
                        variable_rows
                    )

                    # Commands
                    process_nodes(
                        data.get(
                            "nodes",
                            []
                        ),
                        task_name,
                        command_rows,
                        [1]
                    )

                    # Packages
                    package_set = set()

                    collect_all_packages(
                        data,
                        package_set
                    )

                    for pkg in package_set:

                        package_rows.append(
                            {
                                "Task Name": task_name,
                                "Package Name": pkg
                            }
                        )

                except Exception as ex:

                    tasks_found.append(
                        {
                            "file": file_name,
                            "error": str(ex)
                        }
                    )

    commands_df = pd.DataFrame(
        command_rows,
        columns=[
            "Task Name",
            "Line No",
            "Command Name",
            "Package Name"
        ]
    )

    variables_df = pd.DataFrame(
        variable_rows,
        columns=[
            "Task Name",
            "Variable Name",
            "Type",
            "Input",
            "Output"
        ]
    )

    packages_df = pd.DataFrame(
        package_rows,
        columns=[
            "Task Name",
            "Package Name"
        ]
    )

    if not variables_df.empty:

        variables_df = (
            variables_df
            .drop_duplicates(
                subset=[
                    "Task Name",
                    "Variable Name",
                    "Type"
                ]
            )
        )

    if not packages_df.empty:

        packages_df = (
            packages_df
            .drop_duplicates()
        )

    return {
        "commands": commands_df,
        "variables": variables_df,
        "packages": packages_df,
        "tasks_found": tasks_found
    }


def process_nodes(
    nodes,
    task_name,
    command_rows,
    line_counter
):

    if not isinstance(nodes, list):
        return

    for node in nodes:

        if not isinstance(node, dict):
            continue

        # Skip disabled commands
        if node.get("disabled", False):
            continue

        command_name = node.get(
            "commandName",
            ""
        )

        package_name = node.get(
            "packageName",
            ""
        )

        if command_name or package_name:

            command_rows.append(
                {
                    "Task Name": task_name,
                    "Line No": line_counter[0],
                    "Command Name": command_name,
                    "Package Name": package_name
                }
            )

            line_counter[0] += 1

        # Process children

        process_nodes(
            node.get(
                "children",
                []
            ),
            task_name,
            command_rows,
            line_counter
        )

        # Process branches

        branches = node.get(
            "branches",
            []
        )

        if isinstance(branches, list):

            for branch in branches:

                if not isinstance(
                    branch,
                    dict
                ):
                    continue

                if branch.get(
                    "disabled",
                    False
                ):
                    continue

                process_nodes(
                    [branch],
                    task_name,
                    command_rows,
                    line_counter
                )

def extract_variable_definitions(
    data,
    task_name,
    variable_rows
):

    sections = [
        "variables",
        "inputVariables",
        "outputVariables",
        "botVariables",
        "localVariables"
    ]

    for section in sections:

        variables = data.get(
            section,
            []
        )

        if not isinstance(
            variables,
            list
        ):
            continue

        for var in variables:

            if var.get(
                "disabled",
                False
            ):
                continue

            if not isinstance(
                var,
                dict
            ):
                continue

            variable_rows.append(
                {
                    "Task Name": task_name,
                    "Variable Name": var.get(
                        "name",
                        ""
                    ),
                    "Type": var.get(
                        "type",
                        ""
                    ),
                    "Input":
                        "✓"
                        if var.get(
                            "input",
                            False
                        )
                        else "",
                    "Output":
                        "✓"
                        if var.get(
                            "output",
                            False
                        )
                        else ""
                }
            )


def collect_all_packages(
    obj,
    package_set
):

    if isinstance(
        obj,
        dict
    ):

        # Ignore disabled nodes
        if obj.get(
            "disabled",
            False
        ):
            return

        for key, value in obj.items():

            if key == "packageName":

                package_name = str(
                    value
                ).strip()

                if package_name:

                    package_set.add(
                        package_name
                    )

            collect_all_packages(
                value,
                package_set
            )

    elif isinstance(
        obj,
        list
    ):

        for item in obj:

            collect_all_packages(
                item,
                package_set
            )