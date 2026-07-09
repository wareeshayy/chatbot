"use client";

interface Props {
  questions: { id: string; question: string }[];
  onSelect: (question: string) => void;
  disabled?: boolean;
}

export function SuggestedQuestions({ questions, onSelect, disabled }: Props) {
  if (!questions.length) return null;

  return (
    <div className="mb-4">
      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
        Suggested questions
      </p>
      <div className="flex flex-wrap gap-2">
        {questions.map((q) => (
          <button
            key={q.id}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(q.question)}
            className="rounded-full border border-[#d4a843]/30 bg-white px-3 py-1.5 text-left text-xs text-[#0a1628] transition hover:border-[#d4a843] hover:bg-[#d4a843]/10 disabled:opacity-50"
          >
            {q.question}
          </button>
        ))}
      </div>
    </div>
  );
}
