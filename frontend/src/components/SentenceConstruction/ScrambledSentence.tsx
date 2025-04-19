import { useState, useEffect, useRef } from 'react';
import { draggable, dropTargetForElements } from '@atlaskit/pragmatic-drag-and-drop/element/adapter';
import { Card } from '../Common/Card';
import { Button } from '../Common/Button';
import { SentenceData } from '../../types/sentence';

interface ScrambledSentenceProps {
  sentence: SentenceData;
  onSubmit: (constructedSentence: string) => void;
}

function ScrambledSentence({ sentence, onSubmit }: ScrambledSentenceProps) {
  const [words, setWords] = useState<string[]>(() => {
    if (!Array.isArray(sentence.scrambledWords)) {
      console.error('Invalid scrambledWords:', sentence.scrambledWords);
      return [];
    }
    return sentence.scrambledWords.map(word => word.trim());
  });
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [visibleHints, setVisibleHints] = useState<number>(0);
  const wordRefs = useRef<(HTMLDivElement | null)[]>([]);
  const submitRef = useRef(false);

  // Validate hints to ensure they match expected format
  const validatedHints = Array.isArray(sentence.hints)
    ? sentence.hints.filter(
        (hint): hint is { text: string; usefulness: number } =>
          typeof hint === 'object' && 'text' in hint && 'usefulness' in hint
      )
    : [];

  useEffect(() => {
    if (Array.isArray(sentence.scrambledWords)) {
      const cleanedWords = sentence.scrambledWords.map(word => word.trim());
      setWords(cleanedWords);
      wordRefs.current = Array(cleanedWords.length).fill(null);
      setHasSubmitted(false);
      setVisibleHints(0);
    }
  }, [sentence.scrambledWords]);

  useEffect(() => {
    console.log('Setting up drag-and-drop for words:', words);
    const cleanupFunctions: (() => void)[] = [];

    words.forEach((word, index) => {
      const element = wordRefs.current[index];
      if (!element) {
        console.warn(`No ref for word: ${word} at index: ${index}`);
        return;
      }

      console.log(`Attaching draggable to word: ${word} at index: ${index}`);
      const draggableCleanup = draggable({
        element,
        getInitialData: () => ({ index }),
        onDragStart: () => console.log(`Started dragging: ${word} at ${index}`),
      });

      const dropTargetCleanup = dropTargetForElements({
        element,
        getData: () => ({ index }),
        onDragEnter: () => console.log(`Drag entered: ${word} at ${index}`),
        onDrop: ({ source, self }) => {
          const sourceIndex = source.data.index as number;
          const destinationIndex = self.data.index as number;
          console.log(`Dropped from ${sourceIndex} to ${destinationIndex}`);
          if (sourceIndex !== destinationIndex) {
            const newWords = [...words];
            const [movedWord] = newWords.splice(sourceIndex, 1);
            newWords.splice(destinationIndex, 0, movedWord);
            setWords(newWords);
          }
        },
      });

      cleanupFunctions.push(draggableCleanup, dropTargetCleanup);
    });

    return () => {
      console.log('Cleaning up drag-and-drop');
      cleanupFunctions.forEach(cleanup => cleanup());
    };
  }, [words]);

  const handleReset = () => {
    console.log('Resetting words');
    if (Array.isArray(sentence.scrambledWords)) {
      setWords(sentence.scrambledWords.map(word => word.trim()));
      setVisibleHints(0);
    }
  };

  const handleSubmit = () => {
    if (submitRef.current || hasSubmitted) {
      console.warn('Submit already in progress or already submitted, ignoring');
      return;
    }
    submitRef.current = true;
    setHasSubmitted(true);
    const constructedSentence = words.join('').trim();
    console.log(`Submitting: ${constructedSentence}, original: ${sentence.originalSentence}`);
    onSubmit(constructedSentence);
    setTimeout(() => {
      submitRef.current = false;
    }, 100);
  };

  const handleRevealHint = () => {
    if (visibleHints < validatedHints.length) {
      setVisibleHints(prev => prev + 1);
      console.log(`Revealing hint ${visibleHints + 1}`);
    }
  };

  if (!sentence || !Array.isArray(sentence.scrambledWords)) {
    return (
      <Card className="mb-4 p-6 bg-white shadow-md">
        <p className="text-red-600">Error: Unable to load sentence. Please try again.</p>
      </Card>
    );
  }

  return (
    <Card className="mb-4 p-6 bg-white shadow-md">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Rearrange the Words</h2>
      {validatedHints.length > 0 && (
        <div className="mb-4">
          <h3 className="text-lg font-medium text-gray-700">Hints from Language Pal</h3>
          <ul className="list-disc pl-5 text-gray-600">
            {validatedHints.slice(0, visibleHints).map((hint, index) => (
              <li key={index}>{hint.text}</li>
            ))}
          </ul>
          {visibleHints < validatedHints.length && !hasSubmitted && (
            <Button
              onClick={handleRevealHint}
              variant="outline"
              className="mt-2 border-gray-300 text-gray-700 hover:bg-gray-100"
            >
              Reveal Next Hint
            </Button>
          )}
        </div>
      )}
      <div
        className="flex flex-wrap gap-2 p-4 border-dashed border-2 border-gray-300 rounded min-h-[60px]"
        style={{ borderColor: '#d1d5db' }}
      >
        {words.length > 0 ? (
          words.map((word, index) => (
            <div
              key={`${word}-${index}-${sentence.sentenceId}`}
              ref={el => {
                wordRefs.current[index] = el;
              }}
              className="bg-blue-100 p-2 rounded cursor-move select-none min-w-[60px] text-center hover:scale-105 transition-transform"
              style={{ backgroundColor: '#dbeafe' }}
              draggable={!hasSubmitted}
            >
              {word}
            </div>
          ))
        ) : (
          <p className="text-gray-500">No words to arrange</p>
        )}
      </div>
      <div className="flex gap-4 justify-center mt-4">
        <Button
          onClick={handleSubmit}
          variant="primary"
          className="bg-blue-500 text-white hover:bg-blue-600"
          disabled={words.length === 0 || hasSubmitted}
        >
          Submit
        </Button>
        <Button
          onClick={handleReset}
          variant="outline"
          className="border-gray-300 text-gray-700 hover:bg-gray-100"
          disabled={hasSubmitted}
        >
          Reset
        </Button>
      </div>
    </Card>
  );
}

export default ScrambledSentence;