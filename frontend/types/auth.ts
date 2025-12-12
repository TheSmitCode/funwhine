// types/auth.ts
/**
 * Frontend auth types matching backend User schema.
 */

export interface User {
  id: number;
  username: string;
  email?: string;
  display_name?: string;
  is_active: boolean;
  created_at?: string;

  // UI preferences
  ui_theme: string;
  ui_sidebar: boolean;
  ui_navbar: boolean;
  ui_font_scale: string;
  ui_simple_mode: boolean;
  ui_features: Record<string, boolean>;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id?: number;
  username?: string;
}
