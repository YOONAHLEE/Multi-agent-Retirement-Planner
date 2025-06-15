-- chat_messages 테이블
CREATE TABLE public.chat_messages (
    id SERIAL PRIMARY KEY,
    session_id TEXT,
    sender TEXT,
    message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE
);
-- chat_sessions 테이블
CREATE TABLE public.chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    session_id TEXT,
    started_at TIMESTAMP WITHOUT TIME ZONE
);
-- users 테이블
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE
);