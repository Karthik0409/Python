import streamlit as st
from parser import analyze_zip

st.set_page_config(
    page_title="AA Migration Analyzer",
    layout="wide"
)

st.title(
    "Automation Anywhere Migration Analyzer"
)

uploaded_file = st.file_uploader(
    "Upload AA ZIP File",
    type=["zip"]
)

if uploaded_file:

    result = analyze_zip(
        uploaded_file
    )

    commands_df = result["commands"]
    variables_df = result["variables"]
    packages_df = result["packages"]

    st.success(
        "Analysis Complete"
    )

    if commands_df.empty:

        st.warning(
            "No commands found."
        )

        st.stop()

    tasks = sorted(
        commands_df[
            "Task Name"
        ].unique()
    )

    st.subheader(
        "Task Summary"
    )

    summary = []

    for task in tasks:

        task_commands = commands_df[
            commands_df[
                "Task Name"
            ] == task
        ]

        task_variables = variables_df[
            variables_df[
                "Task Name"
            ] == task
        ]

        task_packages = packages_df[
            packages_df[
                "Task Name"
            ] == task
        ]

        summary.append(
            {
                "Task Name": task,
                "Lines":
                    len(
                        task_commands
                    ),
                "Variables":
                    task_variables[
                        "Variable Name"
                    ].nunique(),
                "Packages":
                    len(
                        task_packages
                    )
            }
        )

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    for task in tasks:

        st.header(
            f"Task : {task}"
        )

        task_commands = commands_df[
            commands_df[
                "Task Name"
            ] == task
        ]

        task_variables = variables_df[
            variables_df[
                "Task Name"
            ] == task
        ]

        task_packages = packages_df[
            packages_df[
                "Task Name"
            ] == task
        ]

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Lines",
                len(
                    task_commands
                )
            )

        with col2:

            st.metric(
                "Variables",
                task_variables[
                    "Variable Name"
                ].nunique()
            )

        with col3:

            st.metric(
                "Packages",
                len(
                    task_packages
                )
            )

        st.subheader(
            "Packages Used"
        )

        st.write(
            sorted(
                task_packages[
                    "Package Name"
                ].tolist()
            )
        )

        st.subheader(
            "Commands"
        )

        st.dataframe(
            task_commands.sort_values(
                by="Line No"
            ),
            use_container_width=True,
            hide_index=True
        )

        st.subheader(
            "Variables"
        )

        st.dataframe(
            task_variables.sort_values(
                by="Variable Name"
            ),
            use_container_width=True,
            hide_index=True
        )

        st.divider()