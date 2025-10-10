'use client';

import * as React from 'react';
import { useCallback, useEffect, useState } from 'react';
import { useRoomContext } from '@livekit/components-react';
import { ShieldIcon, StopCircleIcon, SwordIcon } from '@phosphor-icons/react/dist/ssr';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

/**
 * A control bar specifically designed for battle mode interfaces
 */
export function BattleControlBar({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  const room = useRoomContext();
  const [instructions, setInstructions] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [wordCount, setWordCount] = useState(0);
  const [battleStarted, setBattleStarted] = useState(false);

  // Reset battle state when room disconnects
  useEffect(() => {
    if (room.state === 'disconnected') {
      setBattleStarted(false);
      setInstructions('');
      setWordCount(0);
    }
  }, [room.state]);

  const handleInstructionsChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const text = e.target.value;
    const words = text
      .trim()
      .split(/\s+/)
      .filter((w) => w.length > 0);
    const count = words.length;

    if (count <= 20) {
      setInstructions(text);
      setWordCount(count);
    }
  }, []);

  const handleAttack = useCallback(async () => {
    if (isLoading) return;

    setIsLoading(true);
    try {
      // Find the agent participant
      const agent = Array.from(room.remoteParticipants.values()).find((p) => p.isAgent);

      if (!agent) {
        console.error('No agent found in the room');
        return;
      }

      // Call the attack RPC method on the agent with instructions
      await room.localParticipant.performRpc({
        destinationIdentity: agent.identity,
        method: 'attack',
        payload: instructions,
      });

      // Hide attack and protect buttons after attacking
      setBattleStarted(true);
    } catch (error) {
      console.error('Failed to attack:', error);
    } finally {
      setIsLoading(false);
    }
  }, [room, instructions, isLoading]);

  const handleProtect = useCallback(async () => {
    if (isLoading) return;

    setIsLoading(true);
    try {
      // Find the agent participant
      const agent = Array.from(room.remoteParticipants.values()).find((p) => p.isAgent);

      if (!agent) {
        console.error('No agent found in the room');
        return;
      }

      // Call the protect RPC method on the agent with instructions
      await room.localParticipant.performRpc({
        destinationIdentity: agent.identity,
        method: 'protect',
        payload: instructions,
      });

      // Enable the microphone so the user can speak their attack
      await room.localParticipant.setMicrophoneEnabled(true);

      // Hide attack and protect buttons after protecting
      setBattleStarted(true);
    } catch (error) {
      console.error('Failed to protect:', error);
    } finally {
      setIsLoading(false);
    }
  }, [room, instructions, isLoading]);

  const handleInterrupt = useCallback(async () => {
    if (isLoading) return;

    setIsLoading(true);
    try {
      // Disconnect from the room to completely shut down the session
      await room.disconnect();
    } catch (error) {
      console.error('Failed to interrupt:', error);
    } finally {
      setIsLoading(false);
    }
  }, [room, isLoading]);

  return (
    <div
      aria-label="Battle mode controls"
      className={cn(
        'bg-background border-bg2 dark:border-separator1 flex flex-col gap-4 rounded-[31px] border p-6 drop-shadow-md/3',
        className
      )}
      {...props}
    >
      {/* Instructions Input */}
      {!battleStarted && (
        <div className="flex flex-col gap-2">
          <label htmlFor="instructions" className="text-fg1 text-sm font-medium">
            Compliment Instructions (max 20 words)
          </label>
          <input
            id="instructions"
            type="text"
            value={instructions}
            onChange={handleInstructionsChange}
            placeholder="Enter your compliment style or theme..."
            className="border-bg2 dark:border-separator1 bg-background focus:ring-primary w-full rounded-md border px-3 py-2 text-sm focus:ring-2 focus:outline-none"
          />
          <p className="text-fg2 text-right text-xs">{wordCount} / 20 words</p>
        </div>
      )}

      {/* Battle Buttons */}
      <div className="flex flex-col justify-center gap-2 md:flex-row">
        {!battleStarted && (
          <>
            <Button
              variant="default"
              size="xl"
              onClick={handleAttack}
              disabled={isLoading || !instructions.trim()}
              className="flex-1 font-mono md:h-10"
            >
              <SwordIcon weight="bold" className="mr-2" />
              COMPLIMENT
            </Button>

            <Button
              variant="secondary"
              size="xl"
              onClick={handleProtect}
              disabled={isLoading || !instructions.trim()}
              className="flex-1 font-mono md:h-10"
            >
              <ShieldIcon weight="bold" className="mr-2" />
              RESPOND
            </Button>
          </>
        )}

        <Button
          variant="destructive"
          size="xl"
          onClick={handleInterrupt}
          disabled={isLoading}
          className={cn('font-mono md:h-10', !battleStarted && 'flex-1')}
        >
          <StopCircleIcon weight="bold" className="mr-2" />
          SHUTDOWN
        </Button>
      </div>
    </div>
  );
}
