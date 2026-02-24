# Supabase Setup for Word Game

This directory contains the database schema and setup instructions for the Word Game's word pairs database.

## Setup Instructions

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Choose a region close to your users
3. Set a secure password for your database

### 2. Run the Schema

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy the contents of `schema.sql` and paste it into the editor
5. Click **Run** to execute the schema

This will create the `word_pairs` table and insert sample Portuguese vocabulary.

### 3. Get Your Credentials

1. Go to **Project Settings** > **API** in your Supabase dashboard
2. Copy the following values:
   - **Project URL** → `SUPABASE_URL`
   - **service_role key** → `SUPABASE_KEY` (use service_role, not anon key, for backend access)

### 4. Configure Environment Variables

Add these to your `.env` file in the project root:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key_here
```

### 5. Adding More Words

You can add more word pairs via the Supabase dashboard:

1. Go to **Table Editor** > **word_pairs**
2. Click **Insert row** to add new words
3. Or use SQL Editor with批量 inserts:

```sql
INSERT INTO word_pairs (english_word, translated_word, target_language) VALUES
    ('school', 'escola', 'Portuguese'),
    ('teacher', 'professor', 'Portuguese'),
    ('student', 'estudante', 'Portuguese')
ON CONFLICT (english_word, translated_word, target_language) DO NOTHING;
```

## Schema Overview

### `word_pairs` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `english_word` | TEXT | The English word to translate |
| `translated_word` | TEXT | The translated word |
| `target_language` | TEXT | The target language name |
| `created_at` | TIMESTAMPTZ | Creation timestamp |

A unique constraint ensures no duplicate word pairs for the same language combination.

## Multiple Languages

The schema supports multiple target languages. Add words for any language:

```sql
INSERT INTO word_pairs (english_word, translated_word, target_language) VALUES
    ('hello', 'bonjour', 'French'),
    ('hello', 'hola', 'Spanish'),
    ('hello', 'ciao', 'Italian')
ON CONFLICT (english_word, translated_word, target_language) DO NOTHING;
```
