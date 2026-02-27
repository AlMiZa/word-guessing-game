'use client';

import React, { useEffect } from 'react';
import { motion } from 'motion/react';
import { type AgentState, useRoomContext, useVoiceAssistant } from '@livekit/components-react';
import { toastAlert } from '@/components/alert-toast';
import { WordGameControlBar } from '@/components/livekit/agent-control-bar/word-game-control-bar';
import { MediaTiles } from '@/components/livekit/media-tiles';
import { useDebugMode } from '@/hooks/useDebug';
import { cn } from '@/lib/utils';

function isAgentAvailable(agentState: AgentState) {
    return agentState == 'listening' || agentState == 'thinking' || agentState == 'speaking';
}

interface WordGameSessionViewProps {
    disabled: boolean;
    sessionStarted: boolean;
}

export const WordGameSessionView = ({
    disabled,
    sessionStarted,
    ref,
}: React.ComponentProps<'div'> & WordGameSessionViewProps) => {
    const { state: agentState } = useVoiceAssistant();
    const room = useRoomContext();

    useDebugMode({
        enabled: process.env.NODE_END !== 'production',
    });

    useEffect(() => {
        if (sessionStarted) {
            const timeout = setTimeout(() => {
                if (!isAgentAvailable(agentState)) {
                    const reason =
                        agentState === 'connecting'
                            ? 'Agent did not join the room. '
                            : 'Agent connected but did not complete initializing. ';

                    toastAlert({
                        title: 'Session ended',
                        description: (
                            <p className="w-full">
                                {reason}
                                <a
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    href="https://docs.livekit.io/agents/start/voice-ai/"
                                    className="whitespace-nowrap underline"
                                >
                                    See quickstart guide
                                </a>
                                .
                            </p>
                        ),
                    });
                    room.disconnect();
                }
            }, 20_000);

            return () => clearTimeout(timeout);
        }
    }, [agentState, sessionStarted, room]);

    return (
        <section ref={ref} inert={disabled} className={cn('opacity-0')}>
            <div className="bg-background mp-12 fixed top-0 right-0 left-0 h-32 md:h-36">
                {/* skrim */}
                <div className="from-background absolute bottom-0 left-0 h-12 w-full translate-y-full bg-gradient-to-b to-transparent" />
            </div>

            {/* Word Game Title */}
            <div className="fixed top-0 right-0 left-0 z-30 flex items-center justify-center pt-8">
                <div className="text-center">
                    <h1 className="text-fg1 text-2xl font-bold md:text-4xl">WordPan Word Game</h1>
                    <p className="text-fg2 mt-1 text-sm md:text-base">
                        Practice your vocabulary through voice
                    </p>
                </div>
            </div>

            <MediaTiles chatOpen={false} />

            <div className="bg-background fixed right-0 bottom-0 left-0 z-50 px-3 pt-2 pb-3 md:px-12 md:pb-12">
                <motion.div
                    key="word-game-control-bar"
                    initial={{ opacity: 0, translateY: '100%' }}
                    animate={{
                        opacity: sessionStarted ? 1 : 0,
                        translateY: sessionStarted ? '0%' : '100%',
                    }}
                    transition={{ duration: 0.3, delay: sessionStarted ? 0.5 : 0, ease: 'easeOut' }}
                >
                    <div className="relative z-10 mx-auto w-full max-w-2xl">
                        <WordGameControlBar />
                    </div>
                    {/* skrim */}
                    <div className="from-background border-background absolute top-0 left-0 h-12 w-full -translate-y-full bg-gradient-to-t to-transparent" />
                </motion.div>
            </div>
        </section>
    );
};
