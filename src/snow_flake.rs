use std::thread::sleep;
use std::{
    sync::atomic::{AtomicI64, Ordering},
    time::{Duration, SystemTime, UNIX_EPOCH},
};

use thiserror::Error;

#[derive(Error, Debug)]
pub enum SnowflakeError {
    #[error("Clock moved backwards")]
    ClockBackwards,

    #[error("Worker ID out of range")]
    WorkerIdOutOfRange,

    #[error("Datacenter ID out of range")]
    DatacenterIdOutOfRange,
}

#[derive(Debug)]
pub struct Snowflake {
    worker_id: i64,
    datacenter_id: i64,
    sequence: AtomicI64,
    last_timestamp: AtomicI64,
}

impl Snowflake {
    const EPOCH: i64 = 1609459200000;
    const WORKER_ID_BITS: i64 = 5;
    const DATACENTER_ID_BITS: i64 = 5;
    const SEQUENCE_BITS: i64 = 12;

    const MAX_WORKER_ID: i64 = (1 << Self::WORKER_ID_BITS) - 1;
    const MAX_DATACENTER_ID: i64 = (1 << Self::DATACENTER_ID_BITS) - 1;
    const MAX_SEQUENCE: i64 = (1 << Self::SEQUENCE_BITS) - 1;

    const WORKER_ID_SHIFT: i64 = Self::SEQUENCE_BITS;
    const DATACENTER_ID_SHIFT: i64 = Self::SEQUENCE_BITS + Self::WORKER_ID_BITS;
    const TIMESTAMP_LEFT_SHIFT: i64 =
        Self::SEQUENCE_BITS + Self::WORKER_ID_BITS + Self::DATACENTER_ID_BITS;

    pub fn new(worker_id: i64, datacenter_id: i64) -> Result<Self, SnowflakeError> {
        if !(0..=Self::MAX_WORKER_ID).contains(&worker_id) {
            return Err(SnowflakeError::WorkerIdOutOfRange);
        }
        if !(0..=Self::MAX_DATACENTER_ID).contains(&datacenter_id) {
            return Err(SnowflakeError::DatacenterIdOutOfRange);
        }

        Ok(Snowflake {
            worker_id,
            datacenter_id,
            sequence: AtomicI64::new(0),
            last_timestamp: AtomicI64::new(0),
        })
    }

    pub fn next_id(&self) -> Result<i64, SnowflakeError> {
        let mut timestamp = Self::get_timestamp();
        let last_timestamp = self.last_timestamp.load(Ordering::SeqCst);

        if timestamp < last_timestamp {
            let offset = last_timestamp - timestamp;
            sleep(Duration::from_millis(offset as u64));
            timestamp = Self::get_timestamp();
            if timestamp < last_timestamp {
                return Err(SnowflakeError::ClockBackwards);
            }
        }

        let sequence = if timestamp == last_timestamp {
            let mut current_sequence = self.sequence.load(Ordering::SeqCst);
            loop {
                let next_sequence = (current_sequence + 1) & Self::MAX_SEQUENCE;
                match self.sequence.compare_exchange(
                    current_sequence,
                    next_sequence,
                    Ordering::SeqCst,
                    Ordering::SeqCst,
                ) {
                    Ok(_) => {
                        if next_sequence == 0 {
                            return self.wait_next_millis();
                        } else {
                            break next_sequence;
                        }
                    }
                    Err(current) => current_sequence = current,
                }
            }
        } else {
            self.sequence.store(0, Ordering::SeqCst);
            0
        };

        self.last_timestamp.store(timestamp, Ordering::SeqCst);

        let id = ((timestamp - Self::EPOCH) << Self::TIMESTAMP_LEFT_SHIFT)
            | (self.datacenter_id << Self::DATACENTER_ID_SHIFT)
            | (self.worker_id << Self::WORKER_ID_SHIFT)
            | sequence;
        Ok(id)
    }

    fn wait_next_millis(&self) -> Result<i64, SnowflakeError> {
        let mut timestamp = Self::get_timestamp();
        let last_timestamp = self.last_timestamp.load(Ordering::SeqCst);
        while timestamp <= last_timestamp {
            timestamp = Self::get_timestamp();
        }
        self.next_id()
    }

    fn get_timestamp() -> i64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as i64
    }
}

#[cfg(test)]
mod tests {
    use std::collections::HashSet;

    use super::*;

    #[test]
    fn test_snowflake() {
        let snowflake = Snowflake::new(1, 1).unwrap();
        let mut ids = HashSet::new();

        for _ in 0..1000 {
            let id = snowflake.next_id().unwrap();
            assert!(!ids.contains(&id));
            ids.insert(id);
        }
    }
}
