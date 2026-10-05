import api from "@/api/client";

export interface DeveloperToken {
  id: number;
  name: string;
  jti: string;
  scopes: string[];
  created_at: string;
  revoked_at: string | null;
}

export interface MintedToken {
  id: number;
  jti: string;
  token: string;
}

export async function listTokens(): Promise<DeveloperToken[]> {
  const { data } = await api.get<DeveloperToken[]>("/developer-tokens");
  return data;
}

export async function mintToken(name: string, scopes: string[]): Promise<MintedToken> {
  const { data } = await api.post<MintedToken>("/developer-tokens", { name, scopes });
  return data;
}

export async function revokeToken(id: number): Promise<void> {
  await api.post(`/developer-tokens/${id}/revoke`);
}