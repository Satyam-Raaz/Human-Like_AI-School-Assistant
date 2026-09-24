import { useEffect, useRef, useState } from "react";
import { getChatHistory, streamChat } from "../api/api.js";
import { useAuth } from "../context/AuthContext.jsx";

export default function Chat() {
  const { role, token } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState("");
  const scrollRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    getChatHistory(role, token)
      .then((data) => {
        if (Array.isArray(data.messages)) {
          setMessages(data.messages);
        }
      })
      .catch(() => {
        // History failing to load shouldn't block a fresh conversation.
      });
  }, [role, token]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  // Set up SpeechRecognition once
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return; // browser doesn't support it; mic button will just be disabled

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = 0; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      setInput(transcript);
    };

    recognition.onerror = (event) => {
      setError(`Mic error: ${event.error}`);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.stop();
    };
  }, []);

  function toggleMic() {
    const recognition = recognitionRef.current;
    if (!recognition) {
      setError("Speech recognition isn't supported in this browser.");
      return;
    }

    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      setError("");
      setInput("");
      recognition.start();
      setIsListening(true);
    }
  }

  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || isStreaming) return;

    setError("");
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }, { role: "assistant", content: "" }]);
    setIsStreaming(true);

    streamChat(role, text, token, {
      onToken: (token) => {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          updated[updated.length - 1] = { ...last, content: last.content + token };
          return updated;
        });
      },
      onError: (message) => setError(message),
      onDone: () => setIsStreaming(false),
    });
  }

  return (
    <div className="chat-screen">
      <div className="chat-log" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="chat-empty">Ask something to start the conversation.</div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble chat-bubble--${msg.role}`}>
            <span className="chat-bubble__role">{msg.role === "user" ? "You" : "Assistant"}</span>
            <p>{msg.content || (isStreaming && idx === messages.length - 1 ? "…" : "")}</p>
          </div>
        ))}
      </div>

      {error && <div className="form-error chat-error">{error}</div>}

      <form className="chat-input" onSubmit={handleSend}>
        <button
          type="button"
          className={`btn btn--mic ${isListening ? "btn--mic-active" : ""}`}
          onClick={toggleMic}
          disabled={isStreaming}
          title={isListening ? "Stop listening" : "Speak your message"}
        >
          {isListening ? "🎙️…" : "🎤"}
        </button>

        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={isListening ? "Listening..." : "Type a message..."}
          disabled={isStreaming}
        />

        <button type="submit" className="btn btn--primary" disabled={isStreaming || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}