import { useRef, useState } from "react"
import { Wrench } from "lucide-react"
import { AIChatInput } from "@/components/ui/ai-chat-input"

const TOOL_HOLD_MS = 3000

type Incident = {
  incident: string
  location: string
  date: string
  happened: string
}

type Stats = {
  columns: string[]
  rows: string[][]
}

type Step = {
  id: string
  kind: "thinking" | "tool"
  text: string
  active: boolean
}

type Message = {
  role: "user" | "assistant"
  text: string
  steps: Step[]
  incidents: Incident[]
  stats: Stats | null
  note: string
  pending: boolean
}

type TrailNode = {
  key: string
  kind: "thinking" | "tool"
  text: string
  active: boolean
}

const emptyAssistant = (): Message => ({
  role: "assistant",
  text: "",
  steps: [],
  incidents: [],
  stats: null,
  note: "",
  pending: true,
})

const splitThought = (text: string) => {
  const parts = text
    .split(/\n+|(?<=[.!?])\s+/)
    .map((part) => part.trim())
    .filter(Boolean)
  return parts.length > 0 ? parts : []
}

const trailNodes = (steps: Step[]): TrailNode[] => {
  const nodes: TrailNode[] = []
  for (const step of steps) {
    if (step.kind === "tool") {
      nodes.push({
        key: step.id,
        kind: "tool",
        text: "Calling tool",
        active: step.active,
      })
      continue
    }
    const sentences = splitThought(step.text)
    sentences.forEach((sentence, index) => {
      nodes.push({
        key: `${step.id}-${index}`,
        kind: "thinking",
        text: sentence,
        active: step.active && index === sentences.length - 1,
      })
    })
  }
  return nodes
}

const ProcessTrail = ({ steps }: { steps: Step[] }) => {
  const nodes = trailNodes(steps)
  if (nodes.length === 0) return null
  return (
    <div className="mb-3">
      {nodes.map((node, index) => (
        <div key={node.key} className="flex gap-3">
          <div className="flex w-4 shrink-0 flex-col items-center self-stretch">
            <span
              className={`mt-[7px] h-2 w-2 shrink-0 rounded-full ${
                node.active ? "animate-pulse bg-zinc-700" : "bg-zinc-400"
              }`}
            />
            {index < nodes.length - 1 && (
              <span
                className="my-1 w-px flex-1"
                style={{
                  backgroundImage:
                    "linear-gradient(to bottom, #d4d4d8 0 3px, transparent 3px 8px)",
                  backgroundSize: "1px 8px",
                }}
              />
            )}
          </div>
          <div
            className={`min-w-0 flex-1 text-sm leading-6 text-zinc-500 ${
              index < nodes.length - 1 ? "pb-3" : ""
            }`}
          >
            {node.kind === "tool" ? (
              <span className="inline-flex items-center gap-2 text-zinc-600">
                <Wrench size={14} className={node.active ? "animate-pulse" : ""} />
                Calling tool
              </span>
            ) : (
              <span className="whitespace-pre-wrap">{node.text}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

const Demo = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [threadId, setThreadId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const toolQueue = useRef<string[]>([])

  const patchAssistant = (patch: (message: Message) => Message) => {
    setMessages((current) => {
      const next = [...current]
      const last = next[next.length - 1]
      if (!last || last.role !== "assistant") return current
      next[next.length - 1] = patch(last)
      return next
    })
  }

  const ask = async (pregunta: string) => {
    setMessages((current) => [
      ...current,
      {
        role: "user",
        text: pregunta,
        steps: [],
        incidents: [],
        stats: null,
        note: "",
        pending: false,
      },
      emptyAssistant(),
    ])
    setLoading(true)
    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pregunta, thread_id: threadId }),
      })
      if (!response.ok || !response.body) {
        throw new Error(`El agente respondió ${response.status}`)
      }
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const chunks = buffer.split("\n\n")
        buffer = chunks.pop() ?? ""
        for (const chunk of chunks) {
          const line = chunk.split("\n").find((item) => item.startsWith("data: "))
          if (!line) continue
          const event = JSON.parse(line.slice(6)) as {
            type: string
            thread_id?: string
            text?: string
            status?: string
            note?: string
            stats?: Stats | null
            incidents?: Incident[]
          }
          if (event.type === "thread" && event.thread_id) {
            setThreadId(event.thread_id)
          } else if (event.type === "thinking" && event.text) {
            patchAssistant((message) => {
              const steps = [...message.steps]
              const last = steps[steps.length - 1]
              if (last?.kind === "thinking" && last.active) {
                steps[steps.length - 1] = { ...last, text: last.text + event.text }
              } else {
                steps.push({
                  id: crypto.randomUUID(),
                  kind: "thinking",
                  text: event.text ?? "",
                  active: true,
                })
              }
              return { ...message, steps }
            })
          } else if (event.type === "tool" && event.status === "start") {
            const id = crypto.randomUUID()
            toolQueue.current.push(id)
            patchAssistant((message) => ({
              ...message,
              steps: [
                ...message.steps.map((step) =>
                  step.kind === "thinking" ? { ...step, active: false } : step,
                ),
                { id, kind: "tool", text: "", active: true },
              ],
            }))
          } else if (event.type === "tool") {
            const id = toolQueue.current.shift()
            if (id) {
              window.setTimeout(() => {
                setMessages((current) =>
                  current.map((message) => ({
                    ...message,
                    steps: message.steps.map((step) =>
                      step.id === id ? { ...step, active: false } : step,
                    ),
                  })),
                )
              }, TOOL_HOLD_MS)
            }
          } else if (event.type === "answer") {
            patchAssistant((message) => ({
              ...message,
              steps: message.steps.map((step) =>
                step.kind === "thinking" ? { ...step, active: false } : step,
              ),
              note: event.note ?? "",
              stats: event.stats ?? null,
              incidents: event.incidents ?? [],
              pending: false,
            }))
          }
        }
      }
      patchAssistant((message) => ({ ...message, pending: false }))
    } catch (error) {
      const text =
        error instanceof Error
          ? error.message
          : "No se pudo contactar con el agente"
      patchAssistant((message) => ({
        ...message,
        note: text,
        pending: false,
      }))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#f7f7f8]">
      <main className="flex-1 overflow-y-auto px-4 pt-10 pb-4">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
          {messages.map((message, index) =>
            message.role === "user" ? (
              <div key={index} className="flex items-center justify-end gap-2">
                <div className="max-w-[60%] rounded-2xl bg-[#ececec] px-3 py-1.5 text-[13px] leading-5 text-[#0d0d0d]">
                  {message.text}
                </div>
                <img
                  src="/user.svg"
                  alt=""
                  className="h-6 w-6 shrink-0 rounded-full"
                />
              </div>
            ) : (
              <div key={index} className="flex items-start gap-2">
                <img
                  src="/avatar.svg"
                  alt=""
                  className="mt-0.5 h-6 w-6 shrink-0 rounded-full"
                />
                <div className="min-w-0 flex-1">
                  <ProcessTrail steps={message.steps} />
                  {message.pending && message.steps.length === 0 && (
                    <span className="inline-flex h-6 items-center gap-1">
                      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-400 [animation-delay:0ms]" />
                      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-400 [animation-delay:150ms]" />
                      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-zinc-400 [animation-delay:300ms]" />
                    </span>
                  )}
                  {message.note && (
                    <p className="mb-3 text-[15px] leading-6 text-[#0d0d0d]">
                      {message.note}
                    </p>
                  )}
                  {message.stats && (
                    <div className="mb-3 overflow-x-auto rounded-2xl border border-zinc-200 bg-white shadow-sm">
                      <table className="w-full border-collapse text-left text-sm">
                        <thead className="bg-zinc-50 text-xs uppercase tracking-wide text-zinc-500">
                          <tr>
                            {message.stats.columns.map((column, index) => (
                              <th
                                key={index}
                                className={`px-4 py-3 font-medium ${index > 0 ? "text-right" : ""}`}
                              >
                                {column}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {message.stats.rows.map((row, rowIndex) => (
                            <tr key={rowIndex} className="border-t border-zinc-100">
                              {row.map((cell, index) => (
                                <td
                                  key={index}
                                  className={
                                    index > 0
                                      ? "px-4 py-2.5 text-right tabular-nums text-zinc-700"
                                      : "px-4 py-2.5 font-medium text-zinc-900"
                                  }
                                >
                                  {cell}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  {message.incidents.length > 0 && (
                    <div className="overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm">
                      <table className="w-full border-collapse text-left text-sm">
                        <thead className="bg-zinc-50 text-xs uppercase tracking-wide text-zinc-500">
                          <tr>
                            <th className="px-4 py-3 font-medium">Incidente</th>
                            <th className="px-4 py-3 font-medium">Ubicación</th>
                            <th className="px-4 py-3 font-medium">Fecha</th>
                            <th className="px-4 py-3 font-medium">Descripción</th>
                          </tr>
                        </thead>
                        <tbody>
                          {message.incidents.map((row) => (
                            <tr
                              key={row.incident}
                              className="border-t border-zinc-100 align-top"
                            >
                              <td className="whitespace-nowrap px-4 py-3 font-medium text-zinc-900">
                                {row.incident}
                              </td>
                              <td className="whitespace-nowrap px-4 py-3 text-zinc-700">
                                {row.location}
                              </td>
                              <td className="whitespace-nowrap px-4 py-3 text-zinc-700">
                                {row.date}
                              </td>
                              <td className="px-4 py-3 leading-6 text-zinc-800">
                                {row.happened}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            ),
          )}
        </div>
      </main>
      <div className="px-4 pb-8">
        {messages.length === 0 && (
          <div className="mx-auto mb-3 flex max-w-2xl flex-col items-center gap-3">
            <img
              src="/salud-ai.png"
              alt="SaludMadridAI"
              className="h-16 w-auto"
            />
            <p className="text-center text-sm text-zinc-500">
              ¿Qué quieres saber sobre los informes de accidentes?
            </p>
          </div>
        )}
        <AIChatInput onSend={ask} disabled={loading} />
      </div>
    </div>
  )
}

export { Demo }
