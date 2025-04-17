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
  const wordRefs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    if (Array.isArray(sentence.scrambledWords)) {
      const cleanedWords = sentence.scrambledWords.map(word => word.trim());
      setWords(cleanedWords);
      wordRefs.current = Array(cleanedWords.length).fill(null);
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
    }
  };

  const handleSubmit = () => {
    // Join without spaces for Japanese
    const constructedSentence = words.join('').trim();
    console.log(`Submitting: ${constructedSentence}, original: ${sentence.originalSentence}`);
    onSubmit(constructedSentence);
  };

  if (!sentence || !Array.isArray(sentence.scrambledWords)) {
    return (
      <Card className="mb-4 p-6">
        <p className="text-red-600">Error: Unable to load sentence. Please try again.</p>
      </Card>
    );
  }

  return (
    <Card className="mb-4 p-6">
      <h2 className="text-xl font-semibold mb-4">Rearrange the Words</h2>
      <div
        className="flex flex-wrap gap-2 p-4 border-dashed border-2 border-gray-300 rounded min-h-[60px]"
        onDragOver={e => e.preventDefault()}
      >
        {words.length > 0 ? (
          words.map((word, index) => (
            <div
              key={`${word}-${index}-${sentence.sentenceId}`}
              ref={el => {
                wordRefs.current[index] = el;
              }}
              className="bg-blue-100 p-2 rounded cursor-move select-none min-w-[60px] text-center hover:scale-105 transition-transform"
              draggable="true"
            >
              {word}
            </div>
          ))
        ) : (
          <p className="text-gray-500">No words to arrange</p>
        )}
      </div>
      <div className="flex gap-4 justify-center mt-4">
        <Button onClick={handleSubmit} variant="primary" disabled={words.length === 0}>
          Submit
        </Button>
        <Button onClick={handleReset} variant="outline">
          Reset
        </Button>
      </div>
    </Card>
  );
}

export default ScrambledSentence;