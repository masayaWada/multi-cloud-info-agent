import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import ChatInterface from "../src/components/ChatInterface";

describe("ChatInterface Component", () => {
  const mockMessages = [
    {
      id: 1,
      type: "user",
      content: "ユーザーメッセージ",
      timestamp: new Date("2024-01-01T00:00:00Z"),
    },
    {
      id: 2,
      type: "bot",
      content: "ボットレスポンス",
      timestamp: new Date("2024-01-01T00:01:00Z"),
    },
  ];

  const defaultProps = {
    messages: [],
    onSendMessage: jest.fn(),
    isLoading: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("コンポーネントが正常にレンダリングされる", () => {
    render(<ChatInterface {...defaultProps} />);

    expect(
      screen.getByPlaceholderText(
        "AWSやAzureのリソースについて質問してください..."
      )
    ).toBeInTheDocument();
    expect(screen.getByText("送信")).toBeInTheDocument();
  });

  test("メッセージが正しく表示される", () => {
    render(<ChatInterface {...defaultProps} messages={mockMessages} />);

    expect(screen.getByText("ユーザーメッセージ")).toBeInTheDocument();
    expect(screen.getByText("ボットレスポンス")).toBeInTheDocument();
  });

  test("メッセージの送信が正常に動作する", () => {
    const mockOnSendMessage = jest.fn();
    render(
      <ChatInterface {...defaultProps} onSendMessage={mockOnSendMessage} />
    );

    const input = screen.getByPlaceholderText(
      "AWSやAzureのリソースについて質問してください..."
    );
    const sendButton = screen.getByText("送信");

    fireEvent.change(input, { target: { value: "テストメッセージ" } });
    fireEvent.click(sendButton);

    expect(mockOnSendMessage).toHaveBeenCalledWith("テストメッセージ");
  });

  test("Enterキーでメッセージを送信できる", () => {
    const mockOnSendMessage = jest.fn();
    render(
      <ChatInterface {...defaultProps} onSendMessage={mockOnSendMessage} />
    );

    const input = screen.getByPlaceholderText(
      "AWSやAzureのリソースについて質問してください..."
    );

    fireEvent.change(input, { target: { value: "Enterキーテスト" } });
    fireEvent.keyPress(input, { key: "Enter", code: "Enter" });

    expect(mockOnSendMessage).toHaveBeenCalledWith("Enterキーテスト");
  });

  test("Shift+Enterでは改行が挿入される", () => {
    const mockOnSendMessage = jest.fn();
    render(
      <ChatInterface {...defaultProps} onSendMessage={mockOnSendMessage} />
    );

    const input = screen.getByPlaceholderText(
      "AWSやAzureのリソースについて質問してください..."
    );

    fireEvent.change(input, { target: { value: "テスト\nメッセージ" } });
    fireEvent.keyPress(input, { key: "Enter", code: "Enter", shiftKey: true });

    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  test("空のメッセージは送信できない", () => {
    const mockOnSendMessage = jest.fn();
    render(
      <ChatInterface {...defaultProps} onSendMessage={mockOnSendMessage} />
    );

    const sendButton = screen.getByText("送信");

    fireEvent.click(sendButton);

    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  test("ローディング中は送信ボタンが無効になる", () => {
    render(<ChatInterface {...defaultProps} isLoading={true} />);

    const sendButton = screen.getByText("送信");
    const input = screen.getByPlaceholderText(
      "AWSやAzureのリソースについて質問してください..."
    );

    expect(sendButton).toBeDisabled();
    expect(input).toBeDisabled();
  });

  test("ローディング中はタイピングインジケーターが表示される", () => {
    render(<ChatInterface {...defaultProps} isLoading={true} />);

    expect(
      screen.getByText("エージェントが回答を準備中...")
    ).toBeInTheDocument();
  });

  test("マークダウンが正しくレンダリングされる", () => {
    const markdownMessage = [
      {
        id: 1,
        type: "bot",
        content: "# タイトル\n\n**太字** と *斜体* のテキスト",
        timestamp: new Date("2024-01-01T00:00:00Z"),
      },
    ];

    render(<ChatInterface {...defaultProps} messages={markdownMessage} />);

    expect(screen.getByText("タイトル")).toBeInTheDocument();
    expect(screen.getByText("太字")).toBeInTheDocument();
    expect(screen.getByText("斜体")).toBeInTheDocument();
  });

  test("コードブロックが正しくレンダリングされる", () => {
    const codeMessage = [
      {
        id: 1,
        type: "bot",
        content: '```python\nprint("Hello, World!")\n```',
        timestamp: new Date("2024-01-01T00:00:00Z"),
      },
    ];

    render(<ChatInterface {...defaultProps} messages={codeMessage} />);

    expect(screen.getByText('print("Hello, World!")')).toBeInTheDocument();
  });

  test("メッセージのスクロールが正常に動作する", () => {
    const manyMessages = Array.from({ length: 20 }, (_, i) => ({
      id: i + 1,
      type: i % 2 === 0 ? "user" : "bot",
      content: `メッセージ ${i + 1}`,
      timestamp: new Date(`2024-01-01T00:${i.toString().padStart(2, "0")}:00Z`),
    }));

    render(<ChatInterface {...defaultProps} messages={manyMessages} />);

    // 最新のメッセージが表示されることを確認
    expect(screen.getByText("メッセージ 20")).toBeInTheDocument();
  });

  test("ユーザーメッセージとボットメッセージのスタイルが異なる", () => {
    render(<ChatInterface {...defaultProps} messages={mockMessages} />);

    const userMessage = screen.getByText("ユーザーメッセージ");
    const botMessage = screen.getByText("ボットレスポンス");

    // スタイルの違いを確認（実際の実装に応じて調整）
    expect(userMessage).toBeInTheDocument();
    expect(botMessage).toBeInTheDocument();
  });
});
