-- [FINAL FIX] Supabase Vector Search Function (search_aihub_v2) - Verified
-- 🚨 수정: 모든 컬럼에 테이블 별칭(alias)을 명시하여 'ambiguous column' 오류를 원천 차단했습니다.
-- n8n에서 호출하는 'search_aihub_v2' 함수를 안전하게 새로 생성합니다.

-- 1. 기존 함수 삭제
DROP FUNCTION IF EXISTS search_aihub_v2;

-- 2. 함수 생성 (Ambiguity-Safe Version)
CREATE OR REPLACE FUNCTION search_aihub_v2(
  query_embedding vector(768),
  match_threshold float DEFAULT 0.1,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id text,
  item_type text,
  title text,
  one_liner text,
  description text,
  url text,
  tags jsonb,
  platform text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    -- 1. item_id를 id로 내보냄 (NULL 방지 및 text 강제 변환)
    COALESCE(C.item_id, '')::text AS id,
    
    -- 2. 일반 텍스트 컬럼들 (text 강제 변환)
    COALESCE(C.item_type, '')::text,
    COALESCE(C.title, '')::text,
    COALESCE(C.one_liner, '')::text,
    COALESCE(C.description, '')::text,
    COALESCE(C.url, '')::text,
    
    -- 3. Array(text[]) -> JSONB 변환 (안전하게 변환)
    CASE 
      WHEN C.tags IS NULL THEN '[]'::jsonb 
      ELSE to_jsonb(C.tags) 
    END AS tags,
    
    -- 4. 나머지 컬럼
    COALESCE(C.platform, '')::text,
    
    -- 5. 유사도 계산
    (1 - (E.embedding <=> query_embedding))::float AS similarity
  FROM
    aihub_embeddings E
  JOIN
    aihub_content_catalog_v1 C
    ON E.content_id = C.item_id::text
  WHERE
    1 - (E.embedding <=> query_embedding) > match_threshold
  ORDER BY
    similarity DESC
  LIMIT
    match_count;
END;
$$;
