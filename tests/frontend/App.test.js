import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import App from "../src/App";

// モックの設定
global.fetch = jest.fn();

describe("App Component", () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test("アプリケーションが正常にレンダリングされる", () => {
    render(<App />);

    // ヘッダーが表示されることを確認
    expect(screen.getByText("Multi-Cloud Info Agent")).toBeInTheDocument();
    expect(
      screen.getByText("AWS と Azure のリソース情報を自然言語で確認")
    ).toBeInTheDocument();
  });

  test("チャットメッセージの送信が正常に動作する", async () => {
    // モックレスポンスの設定
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: "テストレスポンス",
        timestamp: "2024-01-01T00:00:00Z",
      }),
    });

    render(<App />);

    // 入力フィールドを取得
    const input = screen.getByPlaceholderText(
      "AWSやAzureのリソースについて質問してください..."
    );
    const sendButton = screen.getByText("送信");

    // メッセージを入力
    fireEvent.change(input, { target: { value: "テストメッセージ" } });

    // 送信ボタンをクリック
    fireEvent.click(sendButton);

    // ユーザーメッセージが表示されることを確認
    expect(screen.getByText("テストメッセージ")).toBeInTheDocument();

    // API が呼び出されることを確認
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: "テストメッセージ" }),
      });
    });

    // ボットレスポンスが表示されることを確認
    await waitFor(() => {
      expect(screen.getByText("テストレスポンス")).toBeInTheDocument();
    });
  });

  test("エラーが発生した場合の処理", async () => {
    // エラーレスポンスのモック
    fetch.mockRejectedValueOnce(new Error("ネットワークエラー"));

    render(<App />);

    const input = screen.getByPlaceholderText(
      "AWSやAzureのリソースについて質問してください..."
    );
    const sendButton = screen.getByText("送信");

    fireEvent.change(input, { target: { value: "テストメッセージ" } });
    fireEvent.click(sendButton);

    // エラーメッセージが表示されることを確認
    await waitFor(() => {
      expect(
        screen.getByText("申し訳ございません。エラーが発生しました。")
      ).toBeInTheDocument();
    });
  });

  test("Enterキーでメッセージを送信できる", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: "Enterキーテスト",
        timestamp: "2024-01-01T00:00:00Z",
      }),
    });

    render(<App />);

    const input = screen.getByPlaceholderText(
      "AWSやAzureのリソースについて質問してください..."
    );

    fireEvent.change(input, { target: { value: "Enterキーテスト" } });
    fireEvent.keyPress(input, { key: "Enter", code: "Enter" });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: "Enterキーテスト" }),
      });
    });
  });

  test("Shift+Enterでは改行が挿入される", () => {
    render(<App />);

    const input = screen.getByPlaceholderText(
      "AWSやAzureのリソースについて質問してください..."
    );

    fireEvent.change(input, { target: { value: "テスト\nメッセージ" } });
    fireEvent.keyPress(input, { key: "Enter", code: "Enter", shiftKey: true });

    // メッセージが送信されないことを確認
    expect(fetch).not.toHaveBeenCalled();
  });

  test("空のメッセージは送信できない", () => {
    render(<App />);

    const input = screen.getByPlaceholderText(
      "AWSやAzureのリソースについて質問してください..."
    );
    const sendButton = screen.getByText("送信");

    // 空のメッセージで送信ボタンをクリック
    fireEvent.click(sendButton);

    // API が呼び出されないことを確認
    expect(fetch).not.toHaveBeenCalled();
  });

  test("ローディング中は送信ボタンが無効になる", async () => {
    // レスポンスを遅延させる
    fetch.mockImplementationOnce(
      () =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                ok: true,
                json: async () => ({
                  response: "遅延レスポンス",
                  timestamp: "2024-01-01T00:00:00Z",
                }),
              }),
            100
          )
        )
    );

    render(<App />);

    const input = screen.getByPlaceholderText(
      "AWSやAzureのリソースについて質問してください..."
    );
    const sendButton = screen.getByText("送信");

    fireEvent.change(input, { target: { value: "テストメッセージ" } });
    fireEvent.click(sendButton);

    // ローディング中は送信ボタンが無効になることを確認
    expect(sendButton).toBeDisabled();

    // レスポンスが返ってきたら送信ボタンが再有効になることを確認
    await waitFor(() => {
      expect(sendButton).not.toBeDisabled();
    });
  });
});
