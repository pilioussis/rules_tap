FROM python:3.11-slim
ENV UV_SYSTEM_PYTHON=1
ENV UV_PROJECT_ENVIRONMENT=system
COPY ./misc/.bashrc /root/.bashrc

WORKDIR /app
COPY . .

# Install UV
RUN pip install uv
RUN uv sync --locked

EXPOSE 8000

CMD ["uv", "manage.py", "runserver", "0.0.0.0:8000"] 