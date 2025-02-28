CREATE TYPE user_status AS ENUM (
    'active',
    'inactive',
    'pending',
    'deleted'
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL,
    spm VARCHAR(255),
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    ip INET,
    avatar VARCHAR(255),
    status user_status,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_uuid ON users(uuid);
CREATE INDEX idx_users_username ON users(username);

CREATE TYPE ballot_status AS ENUM (
    'Created',
    'Processed',
    'Invalid',
    'Discarded' 
);

CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),

    topic_id SMALLINT NOT NULL,
    ballot_code VARCHAR(255) NOT NULL,
    fingerprint VARCHAR(255) NOT NULL,
    ip INET,
    is_mobile BOOLEAN NOT NULL,
    process_info JSONB,
    options INTEGER[] NOT NULL,
    selected_options INTEGER[] NOT NULL,
    excluded_options INTEGER[] NOT NULL,
    status ballot_status NOT NULL,
    multiplier INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX votes_user_id_index ON votes(user_id);
CREATE INDEX votes_topic_id_index ON votes(topic_id);

CREATE TYPE topic_type AS ENUM (
    'SixStarCharacter',
    'AnyStarCharacter',
    'Collection',
    'Custom'
);

CREATE TYPE topic_status AS ENUM (
    'Audit',
    'Normal',
    'Deleted',
    'Ended'
);

CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    type topic_type NOT NULL,
    style JSONB,
    status topic_status NOT NULL,
    start_at TIMESTAMP WITH TIME ZONE NOT NULL,
    finish_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);