# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False

ctypedef unsigned long long uint64_t
ctypedef unsigned long DWORD

cdef uint64_t POCH = <uint64_t>1631482056000

cdef short TIMESTAMP_BITS = <short>41
cdef short DATA_CENTER_ID_BITS = <short>5
cdef short WORKER_ID_BITS = <short>5
cdef short SEQUENCE_BITS = <short>12

cdef uint64_t MAX_TIMESTAMP = <uint64_t>(-1 ^ (-1 << TIMESTAMP_BITS))
cdef short MAX_WORKER_ID = <short>(-1 ^ (-1 << WORKER_ID_BITS))
cdef short MAX_DATA_CENTER_ID = <short>(-1 ^ (-1 << DATA_CENTER_ID_BITS))

cdef short SEQUENCE_MASK = <short>(-1 ^ (-1 << SEQUENCE_BITS))

cdef short WORKER_ID_SHIFT = SEQUENCE_BITS + 1
cdef short DATA_CENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + 1
cdef short TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATA_CENTER_ID_BITS + 1

cdef extern from *:
    """
    #if defined(_WIN32) || defined(MS_WINDOWS) || defined(_MSC_VER)
      #include <Windows.h>
      static const uint64_t FILETIME_TO_UNIX_EPOCH = 116444736000000000;
      inline uint64_t get_milliseconds() {
        FILETIME ft;
        uint64_t timestamp;

        GetSystemTimeAsFileTime(&ft);

        timestamp = ((uint64_t)ft.dwHighDateTime << 32) | ft.dwLowDateTime;
        timestamp -= FILETIME_TO_UNIX_EPOCH;
        timestamp /= 10000;
        return timestamp;
      }
    #else
      #include <sys/time.h>
      inline uint64_t get_milliseconds() {
        struct timespec ts;
        clock_gettime(CLOCK_REALTIME, &ts);
        return (uint64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
      }
    #endif
    """
    uint64_t get_milliseconds "get_milliseconds"() nogil

cdef class Snowflake:
    cdef readonly short datacenter_id
    cdef readonly short worker_id
    cdef readonly short sequence

    cdef readonly uint64_t timestamp


    def __cinit__(self, short datacenter_id, short worker_id):
        if worker_id > MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f"worker id can't be greater than {MAX_WORKER_ID} or less than 0")

        if datacenter_id > MAX_DATA_CENTER_ID or datacenter_id < 0:
            raise ValueError(f"datacenter id can't be greater than {MAX_DATA_CENTER_ID} or less than 0")

        self.datacenter_id = datacenter_id
        self.worker_id = worker_id

        self.timestamp = <uint64_t>0
        self.sequence = <short>0


    cdef inline uint64_t til_next_millis(self, uint64_t last_timestamp) nogil:
        cdef uint64_t timestamp
        timestamp = get_milliseconds()
        while timestamp <= last_timestamp:
            timestamp = get_milliseconds()
        return timestamp

    cpdef next_value(self):
        cdef uint64_t now

        now = get_milliseconds()

        if now < self.timestamp:
            raise ValueError("Clock moved backwards. Refusing to generate id.")
        
        if now == self.timestamp:
            self.sequence = (self.sequence + 1) & SEQUENCE_MASK
            if self.sequence == 0:
                now = self.til_next_millis(now)
        else:
            self.sequence = <short>0

        if (now - POCH) > MAX_TIMESTAMP:
            raise ValueError("Timestamp is greater than the maximum timestamp")

        self.timestamp = now

        return (((now - POCH) << TIMESTAMP_LEFT_SHIFT) 
            | (self.datacenter_id << DATA_CENTER_ID_SHIFT) 
            | (self.worker_id << WORKER_ID_SHIFT) 
            | self.sequence)

cpdef get_divice_id(uint64_t snowflake_id):
    cdef short datacenter_id
    cdef short worker_id

    datacenter_id = (snowflake_id >> DATA_CENTER_ID_SHIFT) & MAX_DATA_CENTER_ID
    worker_id = (snowflake_id >> WORKER_ID_SHIFT) & MAX_WORKER_ID

    return datacenter_id, worker_id

cpdef get_timestamp(uint64_t snowflake_id):
    return (snowflake_id >> TIMESTAMP_LEFT_SHIFT) & MAX_TIMESTAMP

cpdef get_gen_timestamp(uint64_t snowflake_id):
    return get_timestamp(snowflake_id) + POCH

cpdef get_sequence(uint64_t snowflake_id):
    return snowflake_id & SEQUENCE_MASK