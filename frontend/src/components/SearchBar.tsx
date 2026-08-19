import { useEffect, useRef } from "react";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onClear: () => void;
}

export function SearchBar({ value, onChange, onClear }: SearchBarProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <label className="search-bar" aria-label="Search important places">
      <span className="search-icon" aria-hidden="true">⌕</span>
      <input
        ref={inputRef}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Search hospitals, shelters, police…"
      />
      {value ? (
        <button type="button" className="icon-button subtle" onClick={onClear} aria-label="Clear search">
          ×
        </button>
      ) : (
        <kbd>Ctrl K</kbd>
      )}
    </label>
  );
}
