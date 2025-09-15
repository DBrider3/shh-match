import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium font-cozy transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-warm-brown focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-warm-brown text-white shadow-warm hover:bg-warm-coffee hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]",
        destructive:
          "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90 hover:shadow-lg",
        outline:
          "border-2 border-warm-brown bg-transparent text-warm-brown shadow-cozy hover:bg-warm-brown hover:text-white hover:shadow-warm",
        secondary:
          "bg-warm-beige text-warm-coffee shadow-cozy hover:bg-warm-cream hover:shadow-warm",
        ghost: "text-warm-brown hover:bg-warm-cream hover:text-warm-coffee",
        link: "text-warm-brown underline-offset-4 hover:underline hover:text-warm-coffee",
        cozy: "bg-coffee-gradient text-white shadow-warm hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]",
        warm: "bg-warm-orange text-white shadow-cozy hover:bg-warm-orange/90 hover:shadow-warm hover:scale-[1.02]",
        heart: "bg-warm-pink text-white shadow-cozy hover:bg-warm-pink/90 hover:shadow-warm hover:scale-[1.02]",
      },
      size: {
        default: "h-10 px-4 py-2 rounded-lg",
        sm: "h-8 px-3 text-xs rounded-md",
        lg: "h-12 px-8 text-base rounded-xl",
        xl: "h-14 px-10 text-lg rounded-xl",
        icon: "h-10 w-10 rounded-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }