FROM python:3.13-slim
COPY ./toy_django_project/.bashrc /root/.bashrc

WORKDIR /app/toy_django_project

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential gcc gfortran python3-dev postgresql-client \
 && rm -rf /var/lib/apt/lists/*

COPY ./toy_django_project/pyproject.toml ./pyproject.toml
# COPY ./toy_django_project/uv.lock ./uv.lock

# Install deps with UV
RUN pip install uv

# Set the python version to the system version (no venv)
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync
# Save lock file
RUN uv lock

COPY . .

RUN ln -s /app/rules_tap /usr/local/lib/python3.13/site-packages/

# EXPOSE 8000

# CMD ["uv", "manage.py", "runserver", "0.0.0.0:8000"] 