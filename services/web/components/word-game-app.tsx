'use client';

import { useEffect, useMemo, useState } from 'react';
import { Room, RoomEvent } from 'livekit-client';
import { motion } from 'motion/react';
import { RoomAudioRenderer, RoomContext, useVoiceAssistant } from '@livekit/components-react';
import { toastAlert } from '@/components/alert-toast';
import { WordGameSessionView } from '@/components/word-game-session-view';
import { WordGameWelcome } from '@/components/word-game-welcome';
import { Toaster } from '@/components/ui/sonner';
import useConnectionDetails from '@/hooks/useConnectionDetails';
import type { AppConfig } from '@/lib/types';
import { SpeakerHigh } from '@phosphor-icons/react/dist/ssr';

const MotionWordGameWelcome = motion.create(WordGameWelcome);
const MotionWordGameSessionView = motion.create(WordGameSessionView);

interface WordGameAppProps {
    appConfig: AppConfig;
}

export function WordGameApp({ appConfig }: WordGameAppProps) {
    const room = useMemo(() => new Room(), []);
    const [sessionStarted, setSessionStarted] = useState(false);
    const [audioStarted, setAudioStarted] = useState(false);
    const { refreshConnectionDetails, existingOrRefreshConnectionDetails } =
        useConnectionDetails(appConfig);

    // Custom function to start audio
    const startAudio = () => {
        // Set audio as started - the user interaction (click) satisfies browser autoplay policy
        // The RoomAudioRenderer will handle the actual audio playback
        setAudioStarted(true);
    };

    useEffect(() => {
        const onDisconnected = () => {
            setSessionStarted(false);
            refreshConnectionDetails();
        };
        const onMediaDevicesError = (error: Error) => {
            toastAlert({
                title: 'Encountered an error with your media devices',
                description: `${error.name}: ${error.message}`,
            });
        };
        room.on(RoomEvent.MediaDevicesError, onMediaDevicesError);
        room.on(RoomEvent.Disconnected, onDisconnected);
        return () => {
            room.off(RoomEvent.Disconnected, onDisconnected);
            room.off(RoomEvent.MediaDevicesError, onMediaDevicesError);
        };
    }, [room, refreshConnectionDetails]);

    useEffect(() => {
        let aborted = false;
        if (sessionStarted && room.state === 'disconnected') {
            Promise.all([
                room.localParticipant.setMicrophoneEnabled(true, undefined, {
                    preConnectBuffer: appConfig.isPreConnectBufferEnabled,
                }),
                existingOrRefreshConnectionDetails().then((connectionDetails) =>
                    room.connect(connectionDetails.serverUrl, connectionDetails.participantToken)
                ),
            ]).catch((error) => {
                if (aborted) {
                    return;
                }

                toastAlert({
                    title: 'There was an error connecting to the agent',
                    description: `${error.name}: ${error.message}`,
                });
            });
        }
        return () => {
            aborted = true;
            room.disconnect();
        };
    }, [room, sessionStarted, appConfig.isPreConnectBufferEnabled, existingOrRefreshConnectionDetails]);

    return (
        <main>
            <MotionWordGameWelcome
                key="word-game-welcome"
                onStartGame={() => {
                    setSessionStarted(true);
                    startAudio();
                }}
                disabled={sessionStarted}
                initial={{ opacity: 1 }}
                animate={{ opacity: sessionStarted ? 0 : 1 }}
                transition={{ duration: 0.5, ease: 'linear', delay: sessionStarted ? 0 : 0.5 }}
            />

            <RoomContext.Provider value={room}>
                <RoomAudioRenderer />

                {/* Audio start button - shown only if audio hasn't been started */}
                {!audioStarted && sessionStarted && (
                    <button
                        onClick={startAudio}
                        className="fixed bottom-4 right-4 z-[100] flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-lg hover:bg-primary-hover md:bottom-12 md:right-12"
                    >
                        <SpeakerHigh weight="fill" className="size-4" />
                        Enable Audio
                    </button>
                )}

                <MotionWordGameSessionView
                    key="word-game-session-view"
                    disabled={!sessionStarted}
                    sessionStarted={sessionStarted}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: sessionStarted ? 1 : 0 }}
                    transition={{
                        duration: 0.5,
                        ease: 'linear',
                        delay: sessionStarted ? 0.5 : 0,
                    }}
                />
            </RoomContext.Provider>

            <Toaster />
        </main>
    );
}
