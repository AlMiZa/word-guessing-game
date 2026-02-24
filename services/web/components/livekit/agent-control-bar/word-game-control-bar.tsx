'use client';

import * as React from 'react';
import { useCallback, useEffect, useState } from 'react';
import { useRoomContext } from '@livekit/components-react';
import { GameController, StopCircleIcon, TranslateIcon } from '@phosphor-icons/react/dist/ssr';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

// Available languages for the word game
const LANGUAGES = [
    { value: 'Portuguese', label: 'Portuguese' },
    { value: 'Spanish', label: 'Spanish' },
    { value: 'French', label: 'French' },
    { value: 'Italian', label: 'Italian' },
    { value: 'German', label: 'German' },
    { value: 'Belarusian', label: 'Belarusian' },
];

/**
 * Control bar for the word guessing game.
 * Features language selection, start/stop game buttons, and score display.
 */
export function WordGameControlBar({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
    const room = useRoomContext();
    const [isLoading, setIsLoading] = useState(false);
    const [gameStarted, setGameStarted] = useState(false);
    const [selectedLanguage, setSelectedLanguage] = useState('Portuguese');
    const [score, setScore] = useState({ correct: 0, total: 0 });

    // Reset game state when room disconnects
    useEffect(() => {
        if (room.state === 'disconnected') {
            setGameStarted(false);
            setScore({ correct: 0, total: 0 });
        }
    }, [room.state]);

    const handleStartGame = useCallback(async () => {
        if (isLoading) return;

        setIsLoading(true);
        try {
            // Find the agent participant
            const agent = Array.from(room.remoteParticipants.values()).find((p) => p.isAgent);

            if (!agent) {
                console.error('No agent found in the room');
                return;
            }

            // Call the start_game RPC method on the agent with the selected language
            await room.localParticipant.performRpc({
                destinationIdentity: agent.identity,
                method: 'start_game',
                payload: selectedLanguage,
            });

            setGameStarted(true);
            setScore({ correct: 0, total: 0 });
        } catch (error) {
            console.error('Failed to start game:', error);
        } finally {
            setIsLoading(false);
        }
    }, [room, selectedLanguage, isLoading]);

    const handleStopGame = useCallback(async () => {
        if (isLoading) return;

        setIsLoading(true);
        try {
            // Find the agent participant
            const agent = Array.from(room.remoteParticipants.values()).find((p) => p.isAgent);

            if (!agent) {
                console.error('No agent found in the room');
                return;
            }

            // Call the stop_game RPC method on the agent
            await room.localParticipant.performRpc({
                destinationIdentity: agent.identity,
                method: 'stop_game',
                payload: '',
            });

            setGameStarted(false);
        } catch (error) {
            console.error('Failed to stop game:', error);
        } finally {
            setIsLoading(false);
        }
    }, [room, isLoading]);

    const accuracy = score.total > 0 ? Math.round((score.correct / score.total) * 100) : 0;

    return (
        <div
            aria-label="Word game controls"
            className={cn(
                'bg-background border-bg2 dark:border-separator1 flex flex-col gap-4 rounded-[31px] border p-6 drop-shadow-md/3',
                className
            )}
            {...props}
        >
            {/* Language Selector */}
            {!gameStarted && (
                <div className="flex flex-col gap-2">
                    <label htmlFor="language-select" className="text-fg1 flex items-center gap-2 text-sm font-medium">
                        <TranslateIcon weight="bold" className="size-4" />
                        Target Language
                    </label>
                    <select
                        id="language-select"
                        value={selectedLanguage}
                        onChange={(e) => setSelectedLanguage(e.target.value)}
                        disabled={isLoading || gameStarted}
                        className="border-bg2 dark:border-separator1 bg-background focus:ring-primary w-full rounded-md border px-3 py-2 text-sm focus:ring-2 focus:outline-none disabled:opacity-50"
                    >
                        {LANGUAGES.map((lang) => (
                            <option key={lang.value} value={lang.value}>
                                {lang.label}
                            </option>
                        ))}
                    </select>
                </div>
            )}

            {/* Score Display */}
            {gameStarted && (
                <div className="flex items-center justify-between rounded-md border border-bg2 bg-bg1 px-4 py-3">
                    <div className="text-fg2 text-sm">Score</div>
                    <div className="text-fg1 text-xl font-bold">
                        {score.correct} / {score.total}
                        <span className="text-fg2 ml-2 text-sm font-normal">({accuracy}%)</span>
                    </div>
                </div>
            )}

            {/* Game Control Buttons */}
            <div className="flex flex-col justify-center gap-2 md:flex-row">
                {!gameStarted ? (
                    <Button
                        variant="default"
                        size="xl"
                        onClick={handleStartGame}
                        disabled={isLoading}
                        className="flex-1 font-mono md:h-10"
                    >
                        <GameController weight="bold" className="mr-2" />
                        START GAME
                    </Button>
                ) : (
                    <>
                        <div className="text-fg2 text-sm text-center">
                            Playing in <span className="font-semibold text-fg1">{selectedLanguage}</span>
                        </div>
                        <Button
                            variant="destructive"
                            size="xl"
                            onClick={handleStopGame}
                            disabled={isLoading}
                            className="flex-1 font-mono md:h-10"
                        >
                            <StopCircleIcon weight="bold" className="mr-2" />
                            STOP GAME
                        </Button>
                    </>
                )}
            </div>
        </div>
    );
}
