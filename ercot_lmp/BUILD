# Python sources for the ercot_lmp module
python_sources(
    sources=["**/*.py"],
)

# PEX binary for the main application
pex_binary(
    name="pex",
    entry_point="scripts/main.py",
    output_path="ercot_lmp.pex",
)

# Docker image: ercot_lmp:latest
# Includes ercot_lmp, lib_ercot, and hello_world packages
docker_image(
    name="docker",
    source="Dockerfile",
    dependencies=[
        ":pex",
        ":ercot_lmp",
        "//hello_world:pex",
        "//hello_world:hello_world",
        "//lib_ercot:lib_ercot",
    ],
    image_tags=["latest"],
)
