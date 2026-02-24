import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { BookOpenText } from '@phosphor-icons/react/dist/ssr';

interface WordGameWelcomeProps {
    disabled: boolean;
    onStartGame: () => void;
}

export const WordGameWelcome = ({
    disabled,
    onStartGame,
    ref,
}: React.ComponentProps<'div'> & WordGameWelcomeProps) => {
    return (
        <section
            ref={ref}
            inert={disabled}
            className={cn(
                'bg-background fixed inset-0 mx-auto flex h-svh flex-col items-center justify-center text-center',
                disabled ? 'z-10' : 'z-20'
            )}
        >
            <BookOpenText weight="fill" className="text-primary mb-4 size-20" />

            <h1 className="mb-4 text-4xl font-bold">
                Welcome to <br /> WordPan!
            </h1>

            <p className="text-fg1 p2-1 font-large max-w-prose leading-12">
                Practice your vocabulary through voice.<br />
                Listen to the English word and say the translation!
            </p>

            <div className="mt-6 flex flex-col gap-3">
                <Button variant="default" size="xl" onClick={onStartGame} className="w-64 font-mono">
                    START PRACTICING
                </Button>
            </div>

            <div className="mt-8 text-fg2 flex flex-col gap-2 text-sm">
                <p>How it works:</p>
                <ol className="text-fg2 ml-6 list-decimal text-left">
                    <li>Select your target language</li>
                    <li>Listen to the English word</li>
                    <li>Say the translation aloud</li>
                    <li>Get instant feedback!</li>
                </ol>
            </div>
        </section>
    );
};
