import React from "react";
import styled from "styled-components";
import { motion } from "framer-motion";

const AvatarContainer = styled(motion.div)`
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
`;

const AvatarFace = styled.div`
  font-size: 4rem;
  transition: all 0.3s ease;
`;

const StatusIndicator = styled(motion.div)`
  position: absolute;
  top: 20px;
  right: 20px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: ${(props) => {
    switch (props.status) {
      case "thinking":
        return "#ffa500";
      case "happy":
        return "#00ff00";
      case "sad":
        return "#ff0000";
      default:
        return "#00bfff";
    }
  }};
  box-shadow: 0 0 10px
    ${(props) => {
      switch (props.status) {
        case "thinking":
          return "#ffa500";
        case "happy":
          return "#00ff00";
        case "sad":
          return "#ff0000";
        default:
          return "#00bfff";
      }
    }};
`;

function Avatar({ mood = "neutral" }) {
  const getAvatarEmoji = () => {
    switch (mood) {
      case "thinking":
        return "🤔";
      case "happy":
        return "😊";
      case "sad":
        return "😔";
      default:
        return "🤖";
    }
  };

  const getStatusColor = () => {
    switch (mood) {
      case "thinking":
        return "thinking";
      case "happy":
        return "happy";
      case "sad":
        return "sad";
      default:
        return "neutral";
    }
  };

  return (
    <AvatarContainer
      animate={{
        scale: mood === "thinking" ? [1, 1.1, 1] : 1,
        rotate: mood === "happy" ? [0, 5, -5, 0] : 0,
      }}
      transition={{
        duration: mood === "thinking" ? 1 : 0.5,
        repeat: mood === "thinking" ? Infinity : 0,
      }}
    >
      <AvatarFace>{getAvatarEmoji()}</AvatarFace>
      <StatusIndicator
        status={getStatusColor()}
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.7, 1, 0.7],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
        }}
      />
    </AvatarContainer>
  );
}

export default Avatar;
