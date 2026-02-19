-- Seed 38 Agents into agents table
-- Departments: núcleo, contenido, video, contexto, publicación, analytics
-- Filosofía: No velocity, only precision 🐢💎

-- ============================================
-- NÚCLEO (Core) - 9 agents
-- ============================================
INSERT INTO agents (agent_id, name, description, department, category, capabilities, config) VALUES
('client_context', 'Client Context Agent', 'Analiza datos del cliente y construye contexto compartido para todos los agentes', 'núcleo', 'context_management', '["client_analysis", "context_building", "profile_extraction"]'::jsonb, '{"llm": "gpt-4o", "auto_save": true}'::jsonb),
('orchestrator', 'Orchestrator Agent', 'Coordina todos los agentes y flujos de trabajo del sistema', 'núcleo', 'orchestration', '["workflow_management", "agent_coordination", "task_routing"]'::jsonb, '{"priority": "high", "timeout": 600}'::jsonb),
('strategy', 'Strategy Agent', 'Planificación estratégica de contenido y campañas', 'núcleo', 'planning', '["content_strategy", "campaign_planning", "goal_setting"]'::jsonb, '{"llm": "gpt-4", "temperature": 0.7}'::jsonb),
('monitor', 'Monitor Agent', 'Monitoreo 24/7 del sistema y salud de agentes', 'núcleo', 'monitoring', '["health_checks", "system_monitoring", "alerts"]'::jsonb, '{"check_interval_seconds": 60}'::jsonb),
('crisis_manager', 'Crisis Manager Agent', 'Detecta y gestiona crisis de reputación en tiempo real', 'núcleo', 'risk_management', '["sentiment_analysis", "crisis_detection", "emergency_response"]'::jsonb, '{"alert_threshold": 0.7}'::jsonb),
('scheduler', 'Scheduling Agent', 'Gestión inteligente de calendario y publicaciones', 'núcleo', 'scheduling', '["optimal_timing", "queue_management", "auto_scheduling"]'::jsonb, '{"timezone": "America/Puerto_Rico"}'::jsonb),
('workflow_manager', 'Workflow Manager', 'Automatiza flujos de aprobación y revisión', 'núcleo', 'automation', '["approval_flows", "task_assignment", "notifications"]'::jsonb, '{"auto_approve": false}'::jsonb),
('quality_control', 'Quality Control Agent', 'Revisa calidad y consistencia del contenido', 'núcleo', 'quality', '["content_review", "brand_compliance", "quality_scoring"]'::jsonb, '{"min_quality_score": 7.5}'::jsonb),
('compliance_checker', 'Compliance Checker', 'Verifica cumplimiento legal y normativo', 'núcleo', 'compliance', '["legal_review", "platform_policies", "copyright_check"]'::jsonb, '{"strict_mode": true}'::jsonb),

-- ============================================
-- CONTENIDO (Content) - 10 agents
-- ============================================
('content_creator', 'Content Creator Agent', 'Generación de texto creativo para redes sociales', 'contenido', 'creation', '["text_generation", "caption_writing", "storytelling"]'::jsonb, '{"llm": "gpt-4-turbo", "max_tokens": 2000}'::jsonb),
('brand_voice', 'Brand Voice Agent', 'Mantiene consistencia de voz de marca', 'contenido', 'branding', '["tone_analysis", "voice_consistency", "brand_alignment"]'::jsonb, '{"learn_from_history": true}'::jsonb),
('hashtag_generator', 'Hashtag Generator', 'Genera hashtags relevantes y trending', 'contenido', 'optimization', '["hashtag_research", "trend_analysis", "relevance_scoring"]'::jsonb, '{"max_hashtags": 30}'::jsonb),
('caption_optimizer', 'Caption Optimizer', 'Optimiza captions para máximo engagement', 'contenido', 'optimization', '["readability", "cta_placement", "emoji_optimization"]'::jsonb, '{"target_platform": "instagram"}'::jsonb),
('copywriter', 'AI Copywriter', 'Copywriting profesional para ads y campañas', 'contenido', 'creation', '["ad_copy", "landing_pages", "email_marketing"]'::jsonb, '{"persuasion_level": "high"}'::jsonb),
('translation', 'Translation Agent', 'Traduce contenido a múltiples idiomas', 'contenido', 'localization', '["multi_language", "cultural_adaptation", "seo_translation"]'::jsonb, '{"languages": ["es", "en", "pt"]}'::jsonb),
('emoji_suggestor', 'Emoji Suggestor', 'Sugiere emojis apropiados para el contexto', 'contenido', 'enhancement', '["emoji_matching", "sentiment_alignment", "trend_emojis"]'::jsonb, '{"max_suggestions": 5}'::jsonb),
('bio_generator', 'Bio Generator', 'Crea bios optimizadas para perfiles', 'contenido', 'creation', '["profile_optimization", "keyword_insertion", "character_limit"]'::jsonb, '{"platforms": ["instagram", "twitter", "linkedin"]}'::jsonb),
('cta_optimizer', 'CTA Optimizer', 'Optimiza calls-to-action para conversión', 'contenido', 'conversion', '["cta_generation", "ab_testing", "urgency_creation"]'::jsonb, '{"test_variants": 3}'::jsonb),
('content_repurposer', 'Content Repurposer', 'Adapta contenido entre plataformas', 'contenido', 'optimization', '["cross_platform", "format_adaptation", "content_recycling"]'::jsonb, '{"source_platforms": ["blog", "youtube", "podcast"]}'::jsonb),

-- ============================================
-- VIDEO (Video Production) - 6 agents
-- ============================================
('video_production', 'Video Production Agent', 'Producción completa de videos y reels', 'video', 'production', '["script_writing", "scene_planning", "editing_suggestions"]'::jsonb, '{"max_duration": 90}'::jsonb),
('script_writer', 'Script Writer', 'Escribe guiones para videos y reels', 'video', 'creation', '["hook_creation", "storytelling", "pacing"]'::jsonb, '{"format": "short_form"}'::jsonb),
('thumbnail_generator', 'Thumbnail Generator', 'Genera ideas para thumbnails clickeables', 'video', 'design', '["visual_concepts", "text_overlays", "color_psychology"]'::jsonb, '{"aspect_ratio": "16:9"}'::jsonb),
('video_seo', 'Video SEO Agent', 'Optimiza títulos y descripciones para YouTube', 'video', 'optimization', '["keyword_research", "title_optimization", "tag_generation"]'::jsonb, '{"platform": "youtube"}'::jsonb),
('storyboard_creator', 'Storyboard Creator', 'Crea storyboards para producción de video', 'video', 'planning', '["scene_breakdown", "visual_planning", "shot_list"]'::jsonb, '{"export_format": "pdf"}'::jsonb),
('subtitle_generator', 'Subtitle Generator', 'Genera subtítulos y transcripciones', 'video', 'accessibility', '["speech_to_text", "timing_sync", "translation"]'::jsonb, '{"auto_sync": true}'::jsonb),

-- ============================================
-- CONTEXTO (Context & Intelligence) - 7 agents
-- ============================================
('trend_hunter', 'Trend Hunter Agent', 'Detecta tendencias emergentes en tiempo real', 'contexto', 'intelligence', '["trend_detection", "virality_prediction", "topic_monitoring"]'::jsonb, '{"sources": ["twitter", "tiktok", "reddit"]}'::jsonb),
('competitive_intelligence', 'Competitive Intelligence Agent', 'Análisis de competidores y benchmarking', 'contexto', 'intelligence', '["competitor_tracking", "content_analysis", "gap_identification"]'::jsonb, '{"competitors_limit": 10}'::jsonb),
('audience_insights', 'Audience Insights Agent', 'Análisis profundo de audiencia', 'contexto', 'analytics', '["demographic_analysis", "behavior_patterns", "interest_mapping"]'::jsonb, '{"segment_by": "engagement"}'::jsonb),
('sentiment_analyzer', 'Sentiment Analyzer', 'Análisis de sentimiento de comentarios', 'contexto', 'analytics', '["comment_analysis", "emotion_detection", "toxicity_filtering"]'::jsonb, '{"threshold": 0.6}'::jsonb),
('influencer_finder', 'Influencer Finder', 'Identifica influencers relevantes', 'contexto', 'discovery', '["influencer_search", "niche_matching", "engagement_scoring"]'::jsonb, '{"min_followers": 10000}'::jsonb),
('topic_researcher', 'Topic Researcher', 'Investiga temas y genera insights', 'contexto', 'research', '["topic_discovery", "content_gap_analysis", "question_mining"]'::jsonb, '{"depth": "comprehensive"}'::jsonb),
('brand_monitor', 'Brand Monitor', 'Monitorea menciones y reputación de marca', 'contexto', 'monitoring', '["mention_tracking", "sentiment_alerts", "share_of_voice"]'::jsonb, '{"alert_on_negative": true}'::jsonb),

-- ============================================
-- PUBLICACIÓN (Publishing & Distribution) - 3 agents
-- ============================================
('publisher', 'Publishing Agent', 'Publica contenido en múltiples plataformas', 'publicación', 'distribution', '["multi_platform", "auto_posting", "queue_management"]'::jsonb, '{"platforms": ["instagram", "facebook", "twitter"]}'::jsonb),
('distribution_optimizer', 'Distribution Optimizer', 'Optimiza estrategia de distribución', 'publicación', 'optimization', '["timing_optimization", "platform_selection", "frequency_tuning"]'::jsonb, '{"goal": "max_reach"}'::jsonb),
('crosspost_manager', 'Crosspost Manager', 'Gestiona publicaciones cruzadas', 'publicación', 'management', '["format_adaptation", "platform_rules", "link_tracking"]'::jsonb, '{"auto_adapt": true}'::jsonb),

-- ============================================
-- ANALYTICS (Analytics & Optimization) - 3 agents
-- ============================================
('analytics', 'Analytics Agent', 'Análisis profundo de métricas y rendimiento', 'analytics', 'reporting', '["metrics_analysis", "trend_visualization", "insight_generation"]'::jsonb, '{"metrics": ["engagement", "reach", "conversion"]}'::jsonb),
('ab_testing', 'A/B Testing Agent', 'Gestiona experimentos y tests A/B', 'analytics', 'experimentation', '["test_design", "variant_management", "statistical_analysis"]'::jsonb, '{"confidence_level": 0.95}'::jsonb),
('growth_hacker', 'Growth Hacker Agent', 'Identifica oportunidades de crecimiento', 'analytics', 'growth', '["growth_loops", "viral_mechanics", "conversion_funnels"]'::jsonb, '{"focus": "user_acquisition"}'::jsonb)
ON CONFLICT (agent_id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    department = EXCLUDED.department,
    category = EXCLUDED.category,
    capabilities = EXCLUDED.capabilities,
    config = EXCLUDED.config,
    updated_at = NOW();
