import { FileText } from "lucide-react";
import type { SourceSnippet } from "../types";

export function SourceCard({ source }: { source: SourceSnippet }) {
  return (
    <article className="source-card">
      <div className="source-title">
        <FileText size={16} aria-hidden="true" />
        <strong>{source.title}</strong>
      </div>
      <p>{source.snippet}</p>
    </article>
  );
}

