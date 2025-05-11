import React, { useState } from "react";

interface ChatInputProps {
  onSendMessage: (text: string) => Promise<void>;
}

export const ChatInput = React.forwardRef<HTMLTextAreaElement, ChatInputProps>(
  ({ onSendMessage }, ref) => {
    const [input, setInput] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault();
      if (input.trim()) {
        await onSendMessage(input);
        setInput("");
      }
    };

    return (
      <form onSubmit={handleSubmit} className="message-input mt-4 flex">
        <textarea
          ref={ref}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-grow border rounded-l px-3 py-2"
          placeholder="Type your message..."
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded-r"
        >
          Send
        </button>
      </form>
    );
  }
);

ChatInput.displayName = "ChatInput";
