# docker build . -t arkvotes:v0.1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /workspace

COPY . .

RUN uv sync


RUN cd /workspace/app/snowflake \
    && mkdir -p snowflake \ 
    && uv run python setup.py build_ext --inplace \
    && cp ./snowflake/*.so ./


EXPOSE 8080

