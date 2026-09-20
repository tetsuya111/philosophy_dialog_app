import { ApiError, matchingRequest } from '@/lib/api-client';

export type RandomCallStatus = 'none' | 'waiting' | 'matched' | 'in_call';

/** GET /api/matching/status/ などが返すユーザーの状態 */
export interface RandomCallState {
  status: RandomCallStatus;
  /** サーバーの現在時刻。端末時刻とのずれの補正に使う */
  server_time: string;
  /** status が waiting のときのみ */
  waiting?: { since: string; expires_at: string };
  /** status が matched / in_call のときのみ */
  room?: { room_name: string; expires_at: string };
  /** エラー時（409 / 404 / 410）の説明 */
  detail?: string;
}

export const getStatus = () => matchingRequest<RandomCallState>('GET', 'status/');
export const joinQueue = () => matchingRequest<RandomCallState>('POST', 'join/');
export const cancelQueue = () => matchingRequest<RandomCallState>('POST', 'cancel/');
export const enterCall = () => matchingRequest<RandomCallState>('POST', 'call/enter/');
export const leaveCall = () => matchingRequest<RandomCallState>('POST', 'call/leave/');

/** 409 / 404 / 410 のレスポンスは現在の状態を含むので、それを取り出す */
export function stateFromError(error: unknown): RandomCallState | null {
  if (error instanceof ApiError && typeof error.body === 'object' && error.body !== null && 'status' in error.body) {
    return error.body as RandomCallState;
  }
  return null;
}
