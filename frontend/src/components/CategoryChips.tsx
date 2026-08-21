import type { PoiCategory } from "../types";

const categories: Array<{ value: PoiCategory; label: string; icon: string }> = [
  { value: "shelter", label: "Shelters", icon: "⌂" },
  { value: "hospital", label: "Hospitals", icon: "+" },
  { value: "police_station", label: "Police", icon: "◈" },
  { value: "petrol_bunk", label: "Petrol", icon: "◉" },
  { value: "pharmacy", label: "Pharmacies", icon: "✚" },
  { value: "fire_station", label: "Fire", icon: "♨" },
  { value: "school", label: "Schools", icon: "▣" },
];

const headerCategories = categories.filter(
  (category) => !["pharmacy", "fire_station", "school"].includes(category.value),
);

interface CategoryChipsProps {
  selected: PoiCategory | null;
  onSelect: (category: PoiCategory | null) => void;
}

export function CategoryChips({ selected, onSelect }: CategoryChipsProps) {
  return (
    <div className="category-chips" aria-label="Filter place categories">
      {headerCategories.map((category) => (
        <button
          className={`category-chip ${selected === category.value ? "selected" : ""}`}
          key={category.value}
          onClick={() => onSelect(selected === category.value ? null : category.value)}
          type="button"
        >
          <span aria-hidden="true">{category.icon}</span>
          {category.label}
        </button>
      ))}
    </div>
  );
}

export function categoryLabel(category: PoiCategory): string {
  return categories.find((item) => item.value === category)?.label ?? category.replace(/_/g, " ");
}

export function categoryIcon(category: PoiCategory): string {
  return categories.find((item) => item.value === category)?.icon ?? "●";
}
