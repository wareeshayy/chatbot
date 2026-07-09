import { redirect } from "next/navigation";

/** /chat redirects to home — the chatbot lives at `/` */
export default function ChatRedirect() {
  redirect("/");
}
