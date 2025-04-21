import React, { useEffect, useState } from 'react';
import { Button } from '../components/Common/Button';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { useDialogue } from '../hooks/useDialogue';
import { Message } from '../types/dialogue';

interface SimulatedDialogueProps {
  lessonId: number;
  onComplete: () => void;
}

const SimulatedDialogue: React.FC<SimulatedDialogueProps> = ({ lessonId, onComplete }) => {
  const {
    dialogue,
    feedback,
    translations,
    dialogueLoading,
    submitLoading,
    translateLoading,
    error,
    fetchDialogue,
    submitDialogue,
    submitFinalDialogue,
    translateMessage,
    reset,
  } = useDialogue();
  const [userMessage, setUserMessage] = useState('');
  const [messageCount, setMessageCount] = useState(0);

  useEffect(() => {
    reset();
    fetchDialogue(lessonId);
  }, [lessonId, fetchDialogue, reset]);

  const handleSendMessage = async () => {
    if (!dialogue || !userMessage.trim() || messageCount >= 3) return;
    const newConversation: Message[] = [
      ...dialogue.conversation,
      { id: `user-${messageCount}`, speaker: 'user', text: userMessage },
    ];
    await submitDialogue(dialogue.dialogue_id, newConversation);
    setMessageCount((prev) => prev + 1);
    setUserMessage('');
  };

  const handleSubmitFinal = async () => {
    if (!dialogue) return;
    await submitFinalDialogue(dialogue.dialogue_id, dialogue.conversation);
  };

  if (error) {
    return (
      <div className="text-red-600 text-center p-6">
        {error}
        <Button onClick={() => fetchDialogue(lessonId)} className="mt-4">
          Try Again
        </Button>
      </div>
    );
  }

  if (dialogueLoading || !dialogue) {
    return <LoadingSpinner message="Loading dialogue..." />;
  }

  return (
    <div className="p-6">
      <h3 className="text-lg font-semibold text-[#252B2F] mb-4">Simulated Dialogue</h3>
      <p className="text-[#252B2F] mb-4">
        <strong>Situation:</strong> {dialogue.situation}
      </p>
      <div className="max-h-64 overflow-y-auto mb-4">
        {dialogue.conversation.map((msg) => (
          <div
            key={msg.id}
            className={`mb-2 ${msg.speaker === 'user' ? 'text-right' : 'text-left'}`}
          >
            <p className="inline-block bg-[#DAE1EA] p-2 rounded text-[#252B2F]">
              <strong>{msg.speaker}:</strong> {msg.text}
            </p>
            {msg.speaker === 'AI' && (
              <button
                className="text-[#1079F1] text-sm ml-2 hover:bg-[#0EBE75] hover:text-[#FFFFFF] p-1 rounded"
                onClick={() => translateMessage(msg.id, msg.text)}
                disabled={translateLoading}
              >
                Translate
              </button>
            )}
            {translations[msg.id] && (
              <p className="text-sm text-[#252B2F] mt-1">{translations[msg.id]}</p>
            )}
          </div>
        ))}
      </div>
      {feedback ? (
        <div className="mb-4">
          <p className={`font-semibold ${feedback.is_correct ? 'text-[#0EBE75]' : 'text-red-600'}`}>
            {feedback.is_correct ? 'Satisfactory!' : 'Needs Improvement'}
          </p>
          <p className="text-[#252B2F]">{feedback.feedback}</p>
          <Button className="mt-4" onClick={onComplete}>
            Finish
          </Button>
        </div>
      ) : (
        <div className="flex">
          <textarea
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            className="flex-1 p-2 border border-[#1079F1] rounded-l-lg text-[#252B2F]"
            placeholder="Type your response..."
            disabled={messageCount >= 3 || submitLoading}
          />
          <Button
            onClick={handleSendMessage}
            className="rounded-l-none"
            disabled={!userMessage.trim() || messageCount >= 3 || submitLoading}
          >
            Send
          </Button>
          {messageCount >= 1 && (
            <Button
              onClick={handleSubmitFinal}
              className="ml-2 border border-[#1079F1] bg-[#FFFFFF] text-[#1079F1] hover:bg-[#1079F1] hover:text-[#FFFFFF]"
              disabled={submitLoading}
            >
              Submit Early
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default SimulatedDialogue;