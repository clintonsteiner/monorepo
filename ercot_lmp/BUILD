python_sources(
    sources=["**/*.py"],
)

pex_binary(
    name="pex",
    entry_point="scripts/main.py",
    output_path="ercot_lmp.pex",
)

files(
    name="dockerfile",
    sources=["Dockerfile"],
)

docker_image(
    name="docker",
    dependencies=[
        ":pex",
        "//hello_world:pex",
        ":ercot_lmp",
        "//lib_ercot:lib_ercot",
        "//hello_world:hello_world",
    ],
    image_tags=["latest", "{build_args.VERSION}"],
)
