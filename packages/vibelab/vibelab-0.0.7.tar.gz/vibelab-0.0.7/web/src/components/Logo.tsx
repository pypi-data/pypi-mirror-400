interface LogoProps {
  className?: string
  size?: number
}

export default function Logo({ className = '', size = 24 }: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Flask/beaker shape with "V" cutout */}
      <path
        d="M10 4h12v6l6 16a2 2 0 01-2 2H6a2 2 0 01-2-2l6-16V4z"
        fill="currentColor"
        opacity="0.15"
      />
      <path
        d="M10 4h12v6l6 16a2 2 0 01-2 2H6a2 2 0 01-2-2l6-16V4z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      {/* Flask neck */}
      <path
        d="M12 2h8M12 2v2M20 2v2"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      {/* Bubbles/dots inside */}
      <circle cx="11" cy="22" r="2" fill="currentColor" opacity="0.6" />
      <circle cx="16" cy="19" r="2.5" fill="currentColor" opacity="0.8" />
      <circle cx="21" cy="23" r="1.5" fill="currentColor" opacity="0.5" />
    </svg>
  )
}

