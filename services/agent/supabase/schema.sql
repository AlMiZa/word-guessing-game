-- Word pairs table for vocabulary practice
-- Stores English words and their translations in various target languages

CREATE TABLE IF NOT EXISTS word_pairs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    english_word TEXT NOT NULL,
    translated_word TEXT NOT NULL,
    target_language TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(english_word, translated_word, target_language)
);

-- Create index on target_language for faster queries by language
CREATE INDEX IF NOT EXISTS idx_word_pairs_target_language ON word_pairs(target_language);

-- Enable Row Level Security (optional, for multi-tenant scenarios)
ALTER TABLE word_pairs ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all reads (for the agent to fetch words)
CREATE POLICY "Allow read access to word_pairs"
    ON word_pairs FOR SELECT
    USING (true);

-- Insert sample Portuguese word pairs for testing
INSERT INTO word_pairs (english_word, translated_word, target_language) VALUES
    ('dog', 'cachorro', 'Portuguese'),
    ('cat', 'gato', 'Portuguese'),
    ('house', 'casa', 'Portuguese'),
    ('water', 'água', 'Portuguese'),
    ('hello', 'olá', 'Portuguese'),
    ('goodbye', 'adeus', 'Portuguese'),
    ('thank you', 'obrigado', 'Portuguese'),
    ('please', 'por favor', 'Portuguese'),
    ('yes', 'sim', 'Portuguese'),
    ('no', 'não', 'Portuguese'),
    ('food', 'comida', 'Portuguese'),
    ('book', 'livro', 'Portuguese'),
    ('car', 'carro', 'Portuguese'),
    ('friend', 'amigo', 'Portuguese'),
    ('love', 'amor', 'Portuguese')
ON CONFLICT (english_word, translated_word, target_language) DO NOTHING;
