python_sources(name="sources", dependencies=["3rdparty/python:default#awscli"])

shell_command(
    name="aws_py",
    command="python main.py",
    tools=["python"],
    execution_dependencies=[":sources"],
    output_files=["aws.py"],
)
