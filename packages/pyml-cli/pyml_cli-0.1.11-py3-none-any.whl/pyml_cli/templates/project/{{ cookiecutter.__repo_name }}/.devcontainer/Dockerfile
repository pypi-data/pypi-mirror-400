FROM ghcr.io/prefix-dev/pixi:0.41.4 AS build

# copy source code, pixi.toml and pixi.lock to the container
WORKDIR /app
COPY . .
# install dependencies to `/app/.pixi/envs/api`
# use `--locked` to ensure the lockfile is up to date with pixi.toml
RUN pixi install --locked -e api
# create the shell-hook bash script to activate the environment
RUN pixi shell-hook -e api -s bash > /shell-hook
RUN echo "#!/bin/bash" > /app/entrypoint.sh
RUN cat /shell-hook >> /app/entrypoint.sh
# extend the shell-hook script to run the command passed to the container
RUN echo 'exec "$@"' >> /app/entrypoint.sh

FROM ubuntu:24.04 AS production
WORKDIR /app
# only copy the production environment into prod container
# please note that the "prefix" (path) needs to stay the same as in the build container
COPY --from=build /app/.pixi/envs/api /app/.pixi/envs/api
COPY --from=build --chmod=0755 /app/entrypoint.sh /app/entrypoint.sh
# copy your project code into the container as well
COPY ./{{ cookiecutter.__package_name }} /app/{{ cookiecutter.__package_name }}

EXPOSE 8000
ENTRYPOINT [ "/app/entrypoint.sh" ]
# run your app inside the pixi environment
CMD [ "uvicorn", "{{ cookiecutter.__package_name }}.scripts.app:app", "--host", "0.0.0.0" ]
