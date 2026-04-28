python_requirements(
    name="reqs",
    source="pyproject.toml",
)

python_requirement(
    name="pytest",
    requirements=["pytest>=9.0.2"],
)

python_distribution(
    name="ercot_lmp_monitor_dist",
    dependencies=[
        "//ercot_lmp",
        "//lib_ercot",
    ],
    provides=python_artifact(
        name="ercot-lmp-monitor",
        version="0.1.0",
    ),
)
