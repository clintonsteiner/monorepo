files(
    name="sql",
    sources=["sql/*.sql"],
)

files(
    name="dockerfile",
    sources=["Dockerfile.db"],
)

docker_image(
    name="docker",
    dependencies=[":sql"],
    image_tags=["latest", "{build_args.VERSION}"],
    repository="ercot-db",
)
