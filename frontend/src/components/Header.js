import React from "react";
import styled from "styled-components";

const HeaderContainer = styled.header`
  background: rgba(0, 0, 0, 0.3);
  padding: 1rem 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
`;

const Title = styled.h1`
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const CloudIcon = styled.span`
  font-size: 1.8rem;
`;

const Subtitle = styled.p`
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
`;

function Header() {
  return (
    <HeaderContainer>
      <Title>
        <CloudIcon>☁️</CloudIcon>
        Multi-Cloud Info Agent
      </Title>
      <Subtitle>AWS と Azure のリソース情報を自然言語で確認</Subtitle>
    </HeaderContainer>
  );
}

export default Header;
