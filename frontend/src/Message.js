import React from "react";
import "./App.css";

function Message({ sender, text }) {
  const messageClass = sender === "user" ? "user-message" : "bot-message";
  return (
    <div className={`message ${messageClass}`}>
      <p>{text}</p>
    </div>
  );
}

export default Message;
