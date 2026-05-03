import { FormEvent, useState } from "react";
import { Send, Sparkles } from "lucide-react";
import { askQuestion } from "../api/client";
import type { ChatResponse, RailFeature } from "../types";
import { SourceCard } from "./SourceCard";

type ChatPanelProps = {
  selectedFeature: RailFeature | null;
};

const PRESET_PROMPTS = [
  "Explain this feature.",
  "Why did it close?",
  "Can it still be seen legally?",
  "What current subway services are nearby?",
];

export function ChatPanel({ selectedFeature }: ChatPanelProps) {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submitQuestion(nextQuestion: string) {
    if (!nextQuestion.trim()) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const answer = await askQuestion(nextQuestion.trim(), selectedFeature?.properties.id ?? null);
      setResponse(answer);
      setQuestion("");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Chat request failed.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submitQuestion(question);
  }

  return (
    <section className="panel-section chat-panel">
      <div className="chat-heading">
        <Sparkles size={19} aria-hidden="true" />
        <h2>Local AI Guide</h2>
      </div>

      <div className="prompt-row">
        {PRESET_PROMPTS.map((prompt) => (
          <button key={prompt} type="button" onClick={() => void submitQuestion(prompt)} disabled={isLoading}>
            {prompt}
          </button>
        ))}
      </div>

      <form className="chat-form" onSubmit={handleSubmit}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder={selectedFeature ? `Ask about ${selectedFeature.properties.name}` : "Ask across the local corpus"}
          aria-label="Question for Ghost Rails NYC"
          rows={3}
        />
        <button type="submit" disabled={isLoading || !question.trim()} aria-label="Send question">
          <Send size={18} aria-hidden="true" />
        </button>
      </form>

      {isLoading && <p className="muted">Retrieving local sources...</p>}
      {error && <p className="inline-error">{error}</p>}

      {response && (
        <div className="answer-block">
          <p>{response.answer}</p>
          <div className="answer-meta">
            <span>Confidence: {response.confidence}</span>
            {response.safety_note && <span>{response.safety_note}</span>}
          </div>
          {response.sources.length > 0 && (
            <div className="sources">
              <h3>Sources</h3>
              {response.sources.map((source) => (
                <SourceCard source={source} key={source.chunk_id} />
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}

