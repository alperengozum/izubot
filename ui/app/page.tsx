import Chatbot from "@/components/ui/chat/Chatbot";
import Image from "next/image";

export default function Home() {
	return (
		<div className={"flex w-[100vw] h-[100vh] flex-col gap-3 p-4 items-center justify-start"}>
			<Image src={"/izu.png"} alt={"logo"} width={100} height={100}/>
			<Chatbot/>
		</div>
	);
}
