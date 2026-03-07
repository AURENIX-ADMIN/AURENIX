import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://localhost:54321';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJh...'; // Placeholder

// Note: In a real app, use environment variables.
// For this local setup, we might need to proxy or ensure env vars are set.
export const supabase = createClient(supabaseUrl, supabaseKey);
