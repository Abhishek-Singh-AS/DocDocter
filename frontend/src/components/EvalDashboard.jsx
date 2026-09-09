import { useState } from "react";
import { runLiveEvaluation } from "../api/client";

function EvalDashboard({ messages }) {
  const [isRunning, setIsRunning] = useState(false);
  const [summary, setSummary] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleRunEvaluation() {
    setIsRunning(true);
    setErrorMessage("");

    try {
      // Send exactly what's currently in the chat -- the real
      // questions, real answers, and real retrieved chunks for
      // whatever document is currently loaded.
      const qaPairs = messages.map((m) => ({
        question: m.question,
        answer: m.answer,
        chunks: m.chunks || [],
      }));

      const data = await runLiveEvaluation(qaPairs);
      setSummary(data);
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setIsRunning(false);
    }
  }

  function scoreColor(score) {
    if (score === null || score === undefined) return "#6b7280";
    if (score >= 4) return "#22c55e";
    if (score >= 3) return "#eab308";
    return "#f43f5e";
  }

  return (
    <div>
      <h2 className="section-heading">Quality Check</h2>
      <p style={{ color: "#9ca3af", marginTop: "-8px", marginBottom: "20px" }}>
        Grades the real questions you've asked in the Ask tab, checking whether each answer is actually backed by your document.
      </p>

      {messages.length === 0 ? (
        <div className="card">
          <p style={{ margin: 0, color: "#9ca3af" }}>
            No questions asked yet. Go to the <strong>Ask</strong> tab, ask a few things about your document, then come back here to check quality.
          </p>
        </div>
      ) : (
        <>
          <button className="primary-button" onClick={handleRunEvaluation} disabled={isRunning}>
            {isRunning ? "Grading answers..." : `▶ Check Quality of ${messages.length} Question${messages.length > 1 ? "s" : ""}`}
          </button>

          {errorMessage && (
            <div className="card" style={{ marginTop: "16px", borderColor: "#f43f5e" }}>
              <strong style={{ color: "#f43f5e" }}>⚠️ {errorMessage}</strong>
            </div>
          )}

          {summary && (
            <div style={{ marginTop: "24px" }}>
              <div style={{ display: "flex", gap: "12px", marginBottom: "24px" }}>
                <div className="card" style={{ flex: 1, textAlign: "center" }}>
                  <div style={{ fontSize: "0.8rem", color: "#9ca3af" }}>Faithfulness</div>
                  <div style={{ fontSize: "1.8rem", fontWeight: 700, color: scoreColor(summary.avg_faithfulness) }}>
                    {summary.avg_faithfulness !== null ? `${summary.avg_faithfulness}/5` : "N/A"}
                  </div>
                </div>

                <div className="card" style={{ flex: 1, textAlign: "center" }}>
                  <div style={{ fontSize: "0.8rem", color: "#9ca3af" }}>Relevance</div>
                  <div style={{ fontSize: "1.8rem", fontWeight: 700, color: scoreColor(summary.avg_relevance) }}>
                    {summary.avg_relevance !== null ? `${summary.avg_relevance}/5` : "N/A"}
                  </div>
                </div>
              </div>

              <h3 style={{ color: "#e7e9f5", fontSize: "1rem", marginBottom: "12px" }}>
                Question-by-question results ({summary.num_questions} graded)
              </h3>

              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {summary.results.map((r, index) => (
                  <div key={index} className="card">
                    <p style={{ margin: 0, fontWeight: 600 }}>{r.question}</p>
                    <p style={{ margin: "6px 0", color: "#9ca3af", fontSize: "0.9rem" }}>
                      <strong>Answer:</strong> {r.actual_answer}
                    </p>
                    <div style={{ display: "flex", gap: "16px", fontSize: "0.85rem", marginTop: "8px" }}>
                      <span style={{ color: scoreColor(r.faithfulness) }}>
                        Faithfulness: {r.faithfulness ?? "N/A"}/5
                      </span>
                      <span style={{ color: scoreColor(r.relevance) }}>
                        Relevance: {r.relevance ?? "N/A"}/5
                      </span>
                      <span style={{ color: r.had_context ? "#22c55e" : "#eab308" }}>
                        {r.had_context ? "✅ Had context" : "⚠️ No context found"}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default EvalDashboard;