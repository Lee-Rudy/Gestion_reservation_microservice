type Props = {
  type?: string;
  placeholder?: string;
  value: string | number; // ✅ accepte les deux
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
};

export default function Input({ type = "text", placeholder, value, onChange }: Props) {
  return (
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className="w-full border border-gray-700 p-2 rounded-lg bg-back text-white focus:outline-none focus:border-green-500"
    />
  );
}