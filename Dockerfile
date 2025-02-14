# docker build . -t arkvotes:v0.1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /workspace

COPY . .

RUN uv pip install --system -r pyproject.toml

RUN cd /workspace/app/snowflake \
    && mkdir -p snowflake \ 
    && uv run python setup.py build_ext --inplace \
    && cp ./snowflake/*.so ./


CMD [ "uv", "run", "python", "main.py"]

EXPOSE 8000