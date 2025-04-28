FROM python:3.13-slim
RUN echo "export PS1=\"\[\e[33;44m\] \u \[\e[0m\]\[\e[34;43m\] @\h \[\e[0m\]\[\e[33;44m\] \w \[\e[0m\]\[\e[34;43m\]⮕ \[\e[0m\] \"" > /root/.bashrc

WORKDIR /app/code

COPY ./pyproject.toml ./pyproject.toml
COPY ./uv.lock ./uv.lock
# COPY ./toy_django_project/uv.lock ./uv.lock

RUN pip install uv
# Set the python version to the system version (no venv)
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync
RUN uv lock

COPY ./server ./server

COPY --from=chunks ./out/chunks ./data/chunks

EXPOSE 8003