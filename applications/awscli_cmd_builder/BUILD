relocated_files(
    name="aws_py",
    files_targets=["tools/autocomplete-scraper:aws_py"],
    src="tools/autocomplete-scraper",
    dest="awscli_cmd_builder",
)

python_sources(
    name="sources",
    sources=["*.py"],
    dependencies=["3rdparty/python:default#textual", "3rdparty/python:default#awscli", ":aws_py"],
)

python_distribution(
    name="lib",
    dependencies=[
        ":sources",
    ],
    provides=python_artifact(
        name="aws-cli-builder-lib",
        version="0.1.0",
    ),
    generate_setup=True,
)

pyoxidizer_binary(
    name="awscli-builder-pyoxi",
    dependencies=[":lib"],
    entry_point="awscli_cmd_builder.app",
)
