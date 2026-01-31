-- ================================================
-- AIHub 벡터 검색을 위한 Supabase 설정
-- 기존 테이블은 수정하지 않습니다!
-- ================================================

-- 1. 임베딩 저장 테이블 생성
CREATE TABLE IF NOT EXISTS aihub_embeddings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content_id TEXT NOT NULL,           -- aihub_content_catalog_v1의 item_id
    item_type TEXT,                      -- guide, preset_agent 등
    content_text TEXT NOT NULL,          -- 임베딩 생성에 사용된 텍스트
    embedding vector(768),               -- Google embedding 벡터 (768차원)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 인덱스 생성 (검색 속도 향상)
CREATE INDEX IF NOT EXISTS aihub_embeddings_embedding_idx 
ON aihub_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10);

-- 3. content_id 인덱스
CREATE INDEX IF NOT EXISTS aihub_embeddings_content_id_idx 
ON aihub_embeddings (content_id);

-- 확인: 테이블이 잘 생성되었는지
SELECT 'aihub_embeddings 테이블 생성 완료!' as status;
