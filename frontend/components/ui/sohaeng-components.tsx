import * as React from "react"
import { cn } from "@/lib/utils"
import { Button } from "./button"

// 매칭 프로필 카드
interface MatchCardProps extends React.HTMLAttributes<HTMLDivElement> {
  name: string
  age: number
  location: string
  interests: string[]
  profileImage?: string
  compatibility?: number
}

const MatchCard = React.forwardRef<HTMLDivElement, MatchCardProps>(
  ({ className, name, age, location, interests, profileImage, compatibility, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "relative overflow-hidden rounded-3xl bg-gradient-to-br from-cream to-warm-beige shadow-warm hover:shadow-lg transition-all duration-300 hover:scale-[1.02] group",
        className
      )}
      {...props}
    >
      {/* 프로필 이미지 영역 */}
      <div className="aspect-[4/5] bg-warm-beige/50 flex items-center justify-center relative">
        {profileImage ? (
          <img
            src={profileImage}
            alt={name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-6xl text-warm-brown/30">
            ☕
          </div>
        )}

        {/* 매칭도 배지 */}
        {compatibility && (
          <div className="absolute top-4 right-4 bg-warm-pink/90 backdrop-blur-sm text-white px-3 py-1 rounded-full text-sm font-medium">
            {compatibility}% 매치
          </div>
        )}
      </div>

      {/* 프로필 정보 */}
      <div className="p-6">
        <div className="flex items-center gap-2 mb-3">
          <h3 className="text-xl font-bold text-coffee">{name}</h3>
          <span className="text-warm-coffee">#{age}</span>
        </div>

        <p className="text-sm text-warm-coffee mb-3 flex items-center gap-1">
          📍 {location}
        </p>

        {/* 관심사 태그 */}
        <div className="flex flex-wrap gap-1 mb-4">
          {interests.slice(0, 3).map((interest, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-warm-orange/20 text-warm-coffee text-xs rounded-full"
            >
              {interest}
            </span>
          ))}
        </div>

        {/* 액션 버튼들 */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1 border-warm-brown/30 text-warm-brown hover:bg-warm-brown hover:text-white"
          >
            💬 대화하기
          </Button>
          <Button
            variant="heart"
            size="sm"
            className="flex-1"
          >
            💕 관심있어요
          </Button>
        </div>
      </div>
    </div>
  )
)
MatchCard.displayName = "MatchCard"

// 채팅 메시지 버블
interface ChatBubbleProps extends React.HTMLAttributes<HTMLDivElement> {
  message: string
  isOwn?: boolean
  timestamp?: string
  avatar?: string
}

const ChatBubble = React.forwardRef<HTMLDivElement, ChatBubbleProps>(
  ({ className, message, isOwn = false, timestamp, avatar, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "flex gap-3 mb-4",
        isOwn ? "flex-row-reverse" : "flex-row",
        className
      )}
      {...props}
    >
      {/* 아바타 */}
      <div className="flex-shrink-0">
        {avatar ? (
          <img
            src={avatar}
            alt="profile"
            className="w-8 h-8 rounded-full object-cover"
          />
        ) : (
          <div className={cn(
            "w-8 h-8 rounded-full flex items-center justify-center text-white text-sm",
            isOwn ? "bg-warm-brown" : "bg-warm-orange"
          )}>
            {isOwn ? "🙋‍♀️" : "☕"}
          </div>
        )}
      </div>

      {/* 메시지 버블 */}
      <div className="flex flex-col max-w-[70%]">
        <div
          className={cn(
            "px-4 py-2 rounded-2xl shadow-cozy",
            isOwn
              ? "bg-warm-brown text-white rounded-br-sm"
              : "bg-white/80 text-warm-coffee rounded-bl-sm"
          )}
        >
          <p className="text-sm leading-relaxed">{message}</p>
        </div>

        {timestamp && (
          <span className={cn(
            "text-xs text-warm-coffee/60 mt-1",
            isOwn ? "text-right" : "text-left"
          )}>
            {timestamp}
          </span>
        )}
      </div>
    </div>
  )
)
ChatBubble.displayName = "ChatBubble"

// 채팅 입력 컴포넌트
interface ChatInputProps extends React.HTMLAttributes<HTMLDivElement> {
  placeholder?: string
  onSend?: (message: string) => void
}

const ChatInput = React.forwardRef<HTMLDivElement, ChatInputProps>(
  ({ className, placeholder = "따뜻한 메시지를 보내보세요...", onSend, ...props }, ref) => {
    const [message, setMessage] = React.useState("")

    const handleSend = () => {
      if (message.trim() && onSend) {
        onSend(message.trim())
        setMessage("")
      }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        handleSend()
      }
    }

    return (
      <div
        ref={ref}
        className={cn(
          "flex gap-2 p-4 bg-cream/50 backdrop-blur-sm border-t border-warm-brown/20",
          className
        )}
        {...props}
      >
        <div className="flex-1 relative">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            className="w-full px-4 py-3 bg-white/80 border border-warm-brown/20 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-warm-brown/30 focus:border-warm-brown/50 text-warm-coffee placeholder-warm-coffee/50"
            rows={1}
            style={{ minHeight: "48px", maxHeight: "120px" }}
          />
        </div>

        <Button
          onClick={handleSend}
          disabled={!message.trim()}
          variant="cozy"
          size="icon"
          className="self-end"
        >
          💌
        </Button>
      </div>
    )
  }
)
ChatInput.displayName = "ChatInput"

// 소확행 로딩 스피너
const CozySpinner = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "inline-flex items-center justify-center",
      className
    )}
    {...props}
  >
    <div className="relative">
      <div className="w-8 h-8 rounded-full border-4 border-warm-beige"></div>
      <div className="absolute top-0 left-0 w-8 h-8 rounded-full border-4 border-transparent border-t-warm-brown animate-spin"></div>
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-xs">
        ☕
      </div>
    </div>
  </div>
))
CozySpinner.displayName = "CozySpinner"

// 소확행 알림 토스트
interface CozyToastProps extends React.HTMLAttributes<HTMLDivElement> {
  type?: "success" | "error" | "info" | "heart"
  title?: string
  message: string
}

const CozyToast = React.forwardRef<HTMLDivElement, CozyToastProps>(
  ({ className, type = "info", title, message, ...props }, ref) => {
    const getToastStyles = () => {
      switch (type) {
        case "success":
          return "bg-green-50 border-green-200 text-green-800"
        case "error":
          return "bg-red-50 border-red-200 text-red-800"
        case "heart":
          return "bg-warm-pink/20 border-warm-pink/30 text-warm-coffee"
        default:
          return "bg-cream/80 border-warm-brown/20 text-warm-coffee"
      }
    }

    const getIcon = () => {
      switch (type) {
        case "success":
          return "✅"
        case "error":
          return "❌"
        case "heart":
          return "💕"
        default:
          return "☕"
      }
    }

    return (
      <div
        ref={ref}
        className={cn(
          "p-4 rounded-xl border backdrop-blur-sm shadow-cozy animate-in slide-in-from-top-2 duration-300",
          getToastStyles(),
          className
        )}
        {...props}
      >
        <div className="flex items-start gap-3">
          <span className="text-lg">{getIcon()}</span>
          <div className="flex-1">
            {title && (
              <h4 className="font-semibold mb-1">{title}</h4>
            )}
            <p className="text-sm leading-relaxed">{message}</p>
          </div>
        </div>
      </div>
    )
  }
)
CozyToast.displayName = "CozyToast"

export {
  MatchCard,
  ChatBubble,
  ChatInput,
  CozySpinner,
  CozyToast
}