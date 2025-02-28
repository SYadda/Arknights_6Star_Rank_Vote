use chrono::{DateTime, Utc};
use sqlx::FromRow;

// 定义Topic结构体
#[derive(Debug, Clone, sqlx::Type)]
#[sqlx(type_name = "topic_type")]
pub enum TopicType {
    SixStarCharacter,
    AnyStarCharacter,
    Collection,
    Custom,
}

impl From<i32> for TopicType {
    fn from(value: i32) -> Self {
        match value {
            0 => TopicType::SixStarCharacter,
            1 => TopicType::AnyStarCharacter,
            2 => TopicType::Collection,
            _ => TopicType::Custom,
        }
    }
}

#[derive(Debug, Clone, sqlx::Type)]
#[sqlx(type_name = "topic_status")]
pub enum TopicStatus {
    Audit,
    Normal,
    Deleted,
    Ended,
}

impl From<i32> for TopicStatus {
    fn from(value: i32) -> Self {
        match value {
            0 => TopicStatus::Audit,
            1 => TopicStatus::Normal,
            2 => TopicStatus::Deleted,
            _ => TopicStatus::Ended,
        }
    }
}

#[derive(Debug, Clone, FromRow)]
pub struct Topic {
    pub id: i32,
    pub name: String,
    pub description: String,
    pub r#type: TopicType,
    pub style: serde_json::Value,
    pub status: TopicStatus,
    pub start_at: DateTime<Utc>,
    pub finish_at: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}
