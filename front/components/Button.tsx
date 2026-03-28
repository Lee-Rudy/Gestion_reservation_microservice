type Props = {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  variant?: "primary" | "outline";
  className?: string;
  disabled?: boolean;
};

export default function Button({
  children,
  onClick,
  type = "button",
  variant = "primary",
  className = "",
  disabled = false,
}: Props) {
  const base = "px-4 py-2 rounded-lg transition font-semibold";

  const variants = {
    primary: "bg-green-500 hover:bg-green-600 text-black",
    outline: "border border-white text-white bg-transparent hover:bg-white hover:text-black",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${variants[variant]} ${className} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      {children}
    </button>
  );
}