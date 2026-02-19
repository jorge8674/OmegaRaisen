-- Migration: Add agent_assigned column to scheduled_posts
-- Purpose: Track which agent (if any) created/assigned the scheduled post
-- Default: 'manual' for user-created posts

ALTER TABLE scheduled_posts
ADD COLUMN IF NOT EXISTS agent_assigned TEXT DEFAULT 'manual';

-- Add index for filtering by agent
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_agent_assigned
ON scheduled_posts(agent_assigned);

-- Add comment
COMMENT ON COLUMN scheduled_posts.agent_assigned IS
'Agent that created/assigned this post. Default: manual for user-created posts. Examples: content_creator, strategy, engagement, manual';
