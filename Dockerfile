FROM python:3.11-slim
COPY ./misc/.bashrc /root/.bashrc

WORKDIR /app
COPY . .

# Install UV
ENV UV_SYSTEM_PYTHON=1
ENV UV_PROJECT_ENVIRONMENT=system
RUN pip install uv
RUN uv sync --locked

# Link rules_tap to django_app
RUN ln -s /app/rules_tap /app/system/lib/python3.13/site-packages

EXPOSE 8000

CMD ["uv", "manage.py", "runserver", "0.0.0.0:8000"] 