"use client"

import { useState } from "react"
import { Send, ChevronRight, ChevronLeft } from "lucide-react"

export interface QBQuestion {
  question: string
  question_type: string
  why_asked: string
}

interface QuestionBuilderProps {
  questions: QBQuestion[]
  onSubmit: (answers: Record<string, string>) => void
}

interface ParsedQuestion {
  text: string
  options: string[]
  questionType: string
  whyAsked: string
  rawQuestion: string
}

/**
 * Parses embedded options from a question string.
 * Input:  "What is the goal? a) Predict outcome b) Understand factors c) Group records"
 * Output: { text: "What is the goal?", options: ["Predict outcome", "Understand factors", "Group records"] }
 */
function parseQuestion(q: QBQuestion): ParsedQuestion {
  const raw = q.question

  // Match pattern: split on letter followed by ) — e.g. "a) ", "b) ", etc.
  const optionPattern = /\s*[a-eA-E]\)\s*/
  const parts = raw.split(optionPattern).filter(Boolean)

  if (parts.length > 1) {
    // First part is the question text, rest are options
    return {
      text: parts[0].trim(),
      options: parts.slice(1).map(o => o.trim()),
      questionType: q.question_type,
      whyAsked: q.why_asked,
      rawQuestion: raw,
    }
  }

  // No embedded options found — plain text question
  return {
    text: raw.trim(),
    options: [],
    questionType: q.question_type,
    whyAsked: q.why_asked,
    rawQuestion: raw,
  }
}

const TYPE_LABELS: Record<string, string> = {
  goal: "Goal",
  stakeholder: "Stakeholder",
  priority: "Priority",
  time: "Time Horizon",
  single_select: "Single Select",
}

export function QuestionBuilder({ questions, onSubmit }: QuestionBuilderProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [currentIdx, setCurrentIdx] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const parsed = questions.map(parseQuestion)
  const current = parsed[currentIdx]
  const isLast = currentIdx === parsed.length - 1
  const isFirst = currentIdx === 0
  const currentAnswer = answers[current?.rawQuestion] || ""

  const handleSelect = (option: string) => {
    setAnswers(prev => ({ ...prev, [current.rawQuestion]: option }))
  }

  const handleTextAnswer = (value: string) => {
    setAnswers(prev => ({ ...prev, [current.rawQuestion]: value }))
  }

  const handleNext = () => {
    if (!isLast) setCurrentIdx(prev => prev + 1)
  }

  const handlePrev = () => {
    if (!isFirst) setCurrentIdx(prev => prev - 1)
  }

  const handleSubmit = () => {
    setIsSubmitting(true)
    setTimeout(() => {
      onSubmit(answers)
      setIsSubmitting(false)
    }, 400)
  }

  const allAnswered = parsed.every(q => answers[q.rawQuestion]?.trim())

  if (!current) return null

  return (
    <div className="w-full max-w-4xl mx-auto mt-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <h2 className="text-3xl font-black text-[var(--alabaster-grey)] tracking-tight">Question Builder</h2>
          <div className="h-px flex-1 bg-gradient-to-r from-[var(--dusk-blue)] to-transparent" />
        </div>
        <span className="text-sm font-mono text-[var(--dusty-denim)]">
          {currentIdx + 1} / {parsed.length}
        </span>
      </div>

      {/* Question Card */}
      <div className="glass-card p-8 border border-[var(--dusk-blue)] relative overflow-hidden">
        <div className="flex gap-4 mb-6">
          <div className="shrink-0">
            <span className="flex items-center justify-center w-10 h-10 rounded-lg bg-[var(--prussian-blue)] border border-[var(--dusk-blue)] text-[var(--dusty-denim)] font-bold font-mono">
              Q{currentIdx + 1}
            </span>
          </div>
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] uppercase tracking-wider font-mono px-2 py-0.5 rounded bg-[var(--prussian-blue)] border border-[var(--dusk-blue)] text-[var(--dusty-denim)]">
                {TYPE_LABELS[current.questionType] || current.questionType}
              </span>
            </div>
            <h3 className="text-xl font-medium text-[var(--alabaster-grey)] leading-relaxed">
              {current.text}
            </h3>
            {current.whyAsked && (
              <p className="text-xs text-[var(--dusty-denim)] italic leading-relaxed">
                {current.whyAsked}
              </p>
            )}
          </div>
        </div>

        {/* Options or Text Input */}
        {current.options.length > 0 ? (
          <div className="grid grid-cols-1 gap-3 mt-4">
            {current.options.map((opt, oIdx) => {
              const isSelected = currentAnswer === opt
              const letter = String.fromCharCode(65 + oIdx) // A, B, C, D, E

              return (
                <button
                  key={oIdx}
                  onClick={() => handleSelect(opt)}
                  className={`p-4 rounded-xl border transition-all duration-200 text-left flex items-center gap-4 ${
                    isSelected
                      ? "bg-[var(--prussian-blue)] border-[var(--alabaster-grey)]/40"
                      : "bg-[var(--ink-black)] border-[var(--dusk-blue)] hover:border-[var(--dusty-denim)] hover:bg-[var(--prussian-blue)]/30"
                  }`}
                >
                  <span className={`flex items-center justify-center w-8 h-8 rounded-lg border text-sm font-bold font-mono shrink-0 transition-colors ${
                    isSelected
                      ? "border-[var(--alabaster-grey)]/40 bg-[var(--dusk-blue)] text-[var(--alabaster-grey)]"
                      : "border-[var(--dusk-blue)] text-[var(--dusty-denim)]"
                  }`}>
                    {letter}
                  </span>
                  <span className={`font-medium text-sm ${isSelected ? "text-[var(--alabaster-grey)]" : "text-[var(--dusty-denim)]"}`}>
                    {opt}
                  </span>
                </button>
              )
            })}
          </div>
        ) : (
          <textarea
            className="w-full bg-[var(--ink-black)] border border-[var(--dusk-blue)] rounded-xl p-4 text-[var(--alabaster-grey)] focus:outline-none focus:border-[var(--dusty-denim)] transition-all resize-y min-h-[120px] text-sm mt-4"
            placeholder="Type your answer here..."
            value={currentAnswer}
            onChange={(e) => handleTextAnswer(e.target.value)}
          />
        )}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between mt-6">
        <button
          onClick={handlePrev}
          disabled={isFirst}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-[var(--dusty-denim)] hover:text-[var(--alabaster-grey)] transition-colors disabled:opacity-30 disabled:pointer-events-none"
        >
          <ChevronLeft className="w-4 h-4" />
          Previous
        </button>

        {isLast ? (
          <button
            onClick={handleSubmit}
            disabled={isSubmitting || !allAnswered}
            className="flex items-center gap-3 bg-[var(--dusk-blue)] hover:bg-[var(--dusty-denim)] text-[var(--alabaster-grey)] px-8 py-3 rounded-xl font-bold transition-all disabled:opacity-50 disabled:pointer-events-none"
          >
            {isSubmitting ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Processing...
              </>
            ) : (
              <>
                Submit Answers
                <Send className="w-5 h-5" />
              </>
            )}
          </button>
        ) : (
          <button
            onClick={handleNext}
            disabled={!currentAnswer}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[var(--dusk-blue)] hover:bg-[var(--dusty-denim)] text-[var(--alabaster-grey)] font-semibold transition-all disabled:opacity-50 disabled:pointer-events-none"
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  )
}
