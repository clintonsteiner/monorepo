python_sources(
    name="service_a",
)

pex_binary(
    name="bin",
    entry_point="service_a.main",
    output_path="service_a.pex",
)

python_distribution(
    name="dist",
    dependencies=[":service_a"],
    provides=python_artifact(
        name="only-uv-monorepo",
        version="0.1.0",
    ),
)
