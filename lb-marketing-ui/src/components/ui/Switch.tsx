type Props = {
    id?: string;
  checked?: boolean;
  onCheckedChange?: (value: boolean) => void;
  className?: string;
};

export function Switch({ id, checked = false, onCheckedChange, className = "" }: Props) {
  return (
    <button
    id={id}
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onCheckedChange?.(!checked)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
        checked ? "bg-blue-600" : "bg-gray-300"
      } ${className}`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
          checked ? "translate-x-6" : "translate-x-1"
        }`}
      />
    </button>
  );
}
