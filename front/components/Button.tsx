type Props = {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  variant?: "primary" | "outline";
  className?: string;
};

export default function Button({
  children,
  onClick,
  type = "button",
  variant = "primary",
  className = "",
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
      className={`${base} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
}