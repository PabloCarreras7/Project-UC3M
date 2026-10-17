"use client"

import { useState, useEffect, useRef } from "react"
import { Paperclip, Send } from "lucide-react"
import { AnimatePresence, motion } from "motion/react"

const PLACEHOLDERS = [
  "Heridos trasladados a La Paz",
  "Accidentes con vertido de combustible",
  "Caídas de motorista en la M30",
  "Qué pasó en un alcance con grúa del seguro",
]

type AIChatInputProps = {
  onSend: (value: string) => void
  disabled?: boolean
}

const AIChatInput = ({ onSend, disabled = false }: AIChatInputProps) => {
  const [placeholderIndex, setPlaceholderIndex] = useState(0)
  const [showPlaceholder, setShowPlaceholder] = useState(true)
  const [isActive, setIsActive] = useState(false)
  const [inputValue, setInputValue] = useState("")
  const wrapperRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isActive || inputValue) return

    const interval = setInterval(() => {
      setShowPlaceholder(false)
      setTimeout(() => {
        setPlaceholderIndex((prev) => (prev + 1) % PLACEHOLDERS.length)
        setShowPlaceholder(true)
      }, 400)
    }, 3000)

    return () => clearInterval(interval)
  }, [isActive, inputValue])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target as Node)
      ) {
        if (!inputValue) setIsActive(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [inputValue])

  const handleActivate = () => setIsActive(true)

  const submit = () => {
    const value = inputValue.trim()
    if (!value || disabled) return
    onSend(value)
    setInputValue("")
  }

  const placeholderContainerVariants = {
    initial: {},
    animate: { transition: { staggerChildren: 0.025 } },
    exit: { transition: { staggerChildren: 0.015, staggerDirection: -1 } },
  }

  const letterVariants = {
    initial: {
      opacity: 0,
      filter: "blur(12px)",
      y: 10,
    },
    animate: {
      opacity: 1,
      filter: "blur(0px)",
      y: 0,
      transition: {
        opacity: { duration: 0.25 },
        filter: { duration: 0.4 },
        y: { type: "spring" as const, stiffness: 80, damping: 20 },
      },
    },
    exit: {
      opacity: 0,
      filter: "blur(12px)",
      y: -10,
      transition: {
        opacity: { duration: 0.2 },
        filter: { duration: 0.3 },
        y: { type: "spring" as const, stiffness: 80, damping: 20 },
      },
    },
  }

  return (
    <div className="w-full flex justify-center text-black">
      <div
        ref={wrapperRef}
        className="w-full max-w-2xl"
        style={{
          height: 52,
          overflow: "hidden",
          borderRadius: 26,
          background: "#fff",
          boxShadow: "0 2px 8px 0 rgba(0,0,0,0.08)",
        }}
        onClick={handleActivate}
      >
        <div className="flex flex-col items-stretch w-full h-full">
          <div className="flex h-full items-center gap-1.5 px-1.5 rounded-full bg-white w-full">
            <button
              className="p-2 rounded-full hover:bg-gray-100 transition"
              title="Attach file"
              type="button"
              tabIndex={-1}
            >
              <Paperclip size={16} />
            </button>

            <div className="relative flex-1">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") submit()
                }}
                className="flex-1 border-0 outline-0 rounded-md py-1 text-sm bg-transparent w-full font-normal"
                style={{ position: "relative", zIndex: 1 }}
                onFocus={handleActivate}
                disabled={disabled}
              />
              <div className="absolute left-0 top-0 w-full h-full pointer-events-none flex items-center px-3 py-2">
                <AnimatePresence mode="wait">
                  {showPlaceholder && !isActive && !inputValue && (
                    <motion.span
                      key={placeholderIndex}
                      className="absolute left-0 top-1/2 -translate-y-1/2 text-gray-400 select-none pointer-events-none"
                      style={{
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        zIndex: 0,
                      }}
                      variants={placeholderContainerVariants}
                      initial="initial"
                      animate="animate"
                      exit="exit"
                    >
                      {PLACEHOLDERS[placeholderIndex]
                        .split("")
                        .map((char, i) => (
                          <motion.span
                            key={i}
                            variants={letterVariants}
                            style={{ display: "inline-block" }}
                          >
                            {char === " " ? "\u00A0" : char}
                          </motion.span>
                        ))}
                    </motion.span>
                  )}
                </AnimatePresence>
              </div>
            </div>

            <button
              className="flex items-center gap-1 bg-black hover:bg-zinc-700 text-white p-2 rounded-full font-medium justify-center disabled:opacity-40"
              title="Send"
              type="button"
              disabled={disabled || !inputValue.trim()}
              onClick={(e) => {
                e.stopPropagation()
                submit()
              }}
            >
              <Send size={15} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export { AIChatInput }
