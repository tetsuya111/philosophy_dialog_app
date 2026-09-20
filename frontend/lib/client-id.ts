import AsyncStorage from '@react-native-async-storage/async-storage';

// ログインなしでランダムコールを使うための利用者識別子（.kiro/specs/random-call/）。
// サーバーが発行した値を端末（Web版ではブラウザのlocalStorage）に保存し、以降のAPI呼び出しに使う。
const STORAGE_KEY = 'randomCall.clientId';

let cached: string | null = null;

export async function getStoredClientId(): Promise<string | null> {
  if (cached === null) {
    cached = await AsyncStorage.getItem(STORAGE_KEY);
  }
  return cached;
}

export async function saveClientId(clientId: string): Promise<void> {
  cached = clientId;
  await AsyncStorage.setItem(STORAGE_KEY, clientId);
}

export async function clearClientId(): Promise<void> {
  cached = null;
  await AsyncStorage.removeItem(STORAGE_KEY);
}
