'use client'
import React, {useState} from "react";
import {ChatMessageList} from "@/components/ui/chat/chat-message-list";
import {ChatBubble, ChatBubbleMessage} from "@/components/ui/chat/chat-bubble";
import {Button} from "@/components/ui/button";
import {Paperclip, Mic, CornerDownLeft} from "lucide-react";
import {Textarea} from "@/components/ui/textarea";

export default function Chatbot() {
	const [messages, setMessages] = useState<{ sender: string; text: string }[]>([
		{
			sender: "bot",
			text: "Merhaba,\nIZU hakkında merak ettiğin sorulara ben cevap verebilirim. Sana nasıl yardımcı olabilirim?"
		},
	]);

	const handleSendMessage = async (text: string) => {
		setMessages((prev) => [...prev, {sender: "user", text}]);

		try {
			const response = await fetch("http://localhost:8000/query", {
				method: "POST",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({question: text}),
			});

			if (!response.ok) {
				throw new Error("Failed to fetch response.");
			}

			const data = await response.json();
			setMessages((prev) => [
				...prev,
				{sender: "bot", text: data.cevap || "No answer found."},
			]);
		} catch (error) {
			setMessages((prev) => [
				...prev,
				{sender: "bot", text: "An error occurred. Please try again."},
			]);
		}
	};

	return (
		<div className="justify-center items-center border rounded shadow-lg p-4 flex-[0.7] w-[90vw] max-h-[60vh]">
			<ChatMessageList>
				{messages.map((message, index) => (
					<ChatBubble
						key={index}
						variant={message.sender === "bot" ? "received" : "sent"}
					>
						<ChatBubbleMessage>{message.text}</ChatBubbleMessage>
					</ChatBubble>
				))}
			</ChatMessageList>
			<form
				className="relative rounded-lg border bg-background focus-within:ring-1 focus-within:ring-ring p-1"
				onSubmit={(e) => {
					e.preventDefault();
					const input = (e.target as HTMLFormElement).querySelector(
						"textarea"
					) as HTMLTextAreaElement;
					if (input.value.trim()) {
						handleSendMessage(input.value);
						input.value = "";
					}
				}}
			>
				<Textarea
					placeholder="Type your message here..."
					className="min-h-12 resize-none rounded-lg bg-background border-0 p-3 shadow-none focus-visible:ring-0"
				/>
				<div className="flex items-center p-3 pt-0">
					<Button variant="ghost" size="icon" disabled>
						<Paperclip className="size-4"/>
						<span className="sr-only">Attach file</span>
					</Button>

					<Button variant="ghost" size="icon" disabled>
						<Mic className="size-4"/>
						<span className="sr-only">Use Microphone</span>
					</Button>

					<Button
						size="sm"
						className="ml-auto gap-1.5"
						type="submit"
					>
						Send Message
						<CornerDownLeft className="size-3.5"/>
					</Button>
				</div>
			</form>
		</div>
	);
}
