"use client";

import { useState, useRef, useEffect } from "react";

const dummyReplies = [
  "That's a clause for concern! 📜",
  "I'm not a lawyer, but I play one on this chat. ",
  "This contract is tighter than a miser's wallet! ",
  "Let me parse that for you... parsing complete! ",
  "In legalee, that means 'don't do that'. ",
  "I'd sue for more coffee breaks in this agreement. ",
  "This provision is so bindig, it's practically handcuffs! ",
  "Your document has more loopholes than a swiss cheese factory! ",
  "That's not just fine prit, it's microscopic! ",
  "I'd need a law degree and a crystal ball to fully analyze this. ",
];

export default function ChatView() {
  const [messages, setMessages] = useState([
    {
      text: "Hey there! I'm your legal document assistant. Ask me ",
      sender: "bot",
    },
  ]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMessage = { text: input, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // Simulate bot reply after a delay
    setTimeout(() => {
      const randomReply =
        dummyReplies[Math.floor(Math.random() * dummyReplies.length)];
      const botMessage = { text: randomReply, sender: "bot" };
      setMessages((prev) => [...prev, botMessage]);
    }, 1000 + Math.random() * 2000); // Random delay between 1-3 seconds
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div className="absolute inset-0 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl h-[calc(100vh-120px)] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-green-100 text-gray-800 border border-green-200"
                }`}
              >
                {message.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your legal question..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={sendMessage}
              className="px-6 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
