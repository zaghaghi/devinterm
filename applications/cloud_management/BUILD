resources(name="styles", sources=["*.tcss"])

python_sources(
    name="sources",
    sources=["**/*.py"],
    dependencies=["3rdparty/python:default#textual", "3rdparty/python:default#boto3", ":styles"],
)

pex_binary(
    name="cloud-management-terminal", dependencies=[":sources", ":styles"], entry_point="cloud_management.app:main"
)
