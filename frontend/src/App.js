import React, { useState, useEffect } from "react";
import styled from "styled-components";
import ChatInterface from "./components/ChatInterface";
import Avatar from "./components/Avatar";
import Header from "./components/Header";
import { motion } from "framer-motion";

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  color: #ffffff;
`;

const MainContent = styled.div`
  display: flex;
  flex: 1;
  overflow: hidden;
`;

const ChatSection = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
`;

const AvatarSection = styled.div`
  width: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
`;

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [avatarMood, setAvatarMood] = useState("neutral");

  const handleSendMessage = async (message) => {
    const userMessage = {
      id: Date.now(),
      type: "user",
      content: message,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setAvatarMood("thinking");

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: data.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
      setAvatarMood("happy");
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: "bot",
        content: "申し訳ございません。エラーが発生しました。",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setAvatarMood("sad");
    } finally {
      setIsLoading(false);
      setTimeout(() => setAvatarMood("neutral"), 2000);
    }
  };

  return (
    <AppContainer>
      <Header />
      <MainContent>
        <ChatSection>
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </ChatSection>
        <AvatarSection>
          <Avatar mood={avatarMood} />
        </AvatarSection>
      </MainContent>
    </AppContainer>
  );
}

export default App;
