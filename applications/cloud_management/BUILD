python_sources(
    name="sources", sources=["*.py"], dependencies=["3rdparty/python:default#textual", "3rdparty/python:default#boto3"]
)
resources(name="styles", sources=["*.tcss"])

pex_binary(name="aws-terminal", dependencies=[":sources", ":styles"], entry_point="aws_terminal.app:main")
