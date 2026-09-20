import { clearClientId, getStoredClientId, saveClientId } from '@/lib/client-id';

// 接続先は frontend/.env の EXPO_PUBLIC_API_BASE_URL で指定する。
// Androidからは `adb reverse tcp:8000 tcp:8000` でホストのバックエンドにつなぐ（docs/frontend.md参照）
const API_BASE_URL = (process.env.EXPO_PUBLIC_API_BASE_URL ?? 'http://localhost:8000').replace(/\/+$/, '');

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly body: unknown
  ) {
    super(`API error: ${status}`);
  }
}

async function issueClientId(): Promise<string> {
  const res = await fetch(`${API_BASE_URL}/api/matching/client/`, { method: 'POST' });
  if (!res.ok) {
    throw new ApiError(res.status, await readJson(res));
  }
  const { client_id: clientId } = (await res.json()) as { client_id: string };
  await saveClientId(clientId);
  return clientId;
}

async function readJson(res: Response): Promise<unknown> {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

/**
 * ランダムコールのAPIを利用者識別子付きで呼び出す。
 * 識別子が未発行なら発行し、401（サーバー側に該当なし）なら発行し直して1回だけ再試行する。
 */
export async function matchingRequest<T>(method: 'GET' | 'POST', path: string): Promise<T> {
  const send = async (clientId: string) =>
    fetch(`${API_BASE_URL}/api/matching/${path}`, {
      method,
      headers: { 'X-Client-Id': clientId },
    });

  let res = await send((await getStoredClientId()) ?? (await issueClientId()));
  if (res.status === 401) {
    await clearClientId();
    res = await send(await issueClientId());
  }

  const body = await readJson(res);
  if (!res.ok) {
    throw new ApiError(res.status, body);
  }
  return body as T;
}
