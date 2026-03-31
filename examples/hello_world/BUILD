python_sources(
    sources=["**/*.py", "!*_test.py", "!test_*.py"],
)

python_tests(
    name="tests",
    sources=["*_test.py", "test_*.py"],
)

pex_binary(
    name="pex",
    entry_point="main.py",
    output_path="hello_world.pex",
)
