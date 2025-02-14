class Snowflake:
    datacenter_id: int
    worker_id: int
    sequence: int
    timestamp: int

    def __init__(self, datacenter_id: int, worker_id: int) -> None: ...
    def next_value(self) -> int: ...

# 获取数据中心ID和机器ID
def get_divice_id(snowflake_id: int) -> tuple[int, int]: ...

# 获取时间戳
def get_timestamp(snowflake_id: int) -> int: ...

# 获取创建ID时的时间戳
def get_gen_timestamp(snowflake_id: int) -> int: ...

# 获取序列号
def get_sequence(snowflake_id: int) -> int: ...
