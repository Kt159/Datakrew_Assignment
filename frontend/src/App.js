import React, { useState, useEffect, useRef } from "react";
import ChatWindow from "./ChatWindow";
import Message from "./Message";
import MessageInput from "./MessageInput";
import "./App.css";

// --- LoginPage Component ---
function LoginPage({ onLoginSuccess }) {
  const [fleetName, setFleetName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (!fleetName.trim()) {
      setError("Please enter your fleet name.");
      setLoading(false);
      return;
    }

    try {
      // Authenticate the fleet_name and return a JWT token.
      const response = await fetch("http://localhost:8000/get-token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: fleetName }),
      });

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({ message: "Login failed." }));
        throw new Error(
          errorData.message || `Login failed with status: ${response.status}`
        );
      }

      const data = await response.json();
      const jwtToken = data.access_token;

      if (jwtToken) {
        localStorage.setItem("jwt", jwtToken);
        onLoginSuccess();
      } else {
        setError("Login successful, but no token received from backend.");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError(
        `Login failed: ${err.message || "Please check your fleet name."}`
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-6">
          Fleet Login
        </h2>
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label
              htmlFor="fleetName"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Fleet Name
            </label>
            <input
              type="text"
              id="fleetName"
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              value={fleetName}
              onChange={(e) => setFleetName(e.target.value)}
              placeholder="E.g. GreenGo"
              required
            />
          </div>
          {error && <p className="text-red-600 text-sm text-center">{error}</p>}
          <button
            type="submit"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            disabled={loading}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

// App Component (Modified)
function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check for JWT on component mount
  useEffect(() => {
    const token = localStorage.getItem("jwt");
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
    setMessages([]);
  };

  const handleLogout = () => {
    localStorage.removeItem("jwt");
    setIsLoggedIn(false);
    setMessages([]); // Clear messages on logout
  };

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    const token = localStorage.getItem("jwt"); // Retrieve the JWT
    if (!token) {
      console.error("No JWT token found. User not authenticated.");
      const errorMessage = {
        sender: "bot",
        text: "User not authenticated. Please log in with your official fleet name",
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
      setLoading(false);
      return;
    }

    const newUserMessage = { sender: "user", text: text };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`, // Include JWT in Authorization header
        },
        body: JSON.stringify({ question: text }),
      });

      if (!response.ok) {
        console.error(
          "Backend response not OK. Status:",
          response.status,
          response.statusText
        );
        if (response.status === 401 || response.status === 403) {
          console.error(
            "Authentication failed or token expired. Please log in again."
          );
          handleLogout();
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log(data);
      const botMessage = { sender: "bot", text: data.reply };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        sender: "bot",
        text: "Oops! Something went wrong. Please try again.",
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      {isLoggedIn ? (
        <>
          <header className="App-header flex justify-between items-center px-4 py-2">
            <h1 className="text-2xl font-bold">Datakrew Chatbot</h1>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-3 rounded-md text-sm"
            >
              Logout
            </button>
          </header>
          <div className="chat-container flex flex-col h-[calc(100vh-64px)]">
            <ChatWindow messages={messages} loading={loading} />
            <MessageInput onSendMessage={sendMessage} loading={loading} />
          </div>
        </>
      ) : (
        <LoginPage onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;
