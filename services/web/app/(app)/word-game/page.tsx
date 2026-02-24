import { headers } from 'next/headers';
import { WordGameApp } from '@/components/word-game-app';
import { getAppConfig } from '@/lib/utils';

export default async function WordGamePage() {
    const hdrs = await headers();
    const appConfig = await getAppConfig(hdrs);

    return <WordGameApp appConfig={appConfig} />;
}
