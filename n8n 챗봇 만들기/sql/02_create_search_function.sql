-- ================================================
-- 벡터 검색 RPC 함수 생성
-- 원본 테이블과 JOIN하여 결과 반환
-- ================================================

CREATE OR REPLACE FUNCTION search_aihub_vector(
    query_embedding vector(768),
    match_threshold FLOAT DEFAULT 0.3,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    item_type TEXT,
    title TEXT,
    one_liner TEXT,
    url TEXT,
    tags TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.item_type,
        c.title,
        c.one_liner,
        c.url,
        c.tags,
        1 - (e.embedding <=> query_embedding) AS similarity
    FROM aihub_embeddings e
    INNER JOIN aihub_content_catalog_v1 c 
        ON e.content_id = c.item_id
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 확인
SELECT 'search_aihub_vector 함수 생성 완료!' as status;
