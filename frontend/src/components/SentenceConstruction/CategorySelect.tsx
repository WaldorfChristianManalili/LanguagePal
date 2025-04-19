interface CategorySelectProps {
  categories: string[];
  selectedCategory: string | null;
  onChange: (category: string) => void;
  disabled: boolean;
}

function CategorySelect({ categories, selectedCategory, onChange, disabled }: CategorySelectProps) {
  return (
    <select
      value={selectedCategory ?? ''}
      onChange={e => onChange(e.target.value)}
      disabled={disabled}
      className="mb-4 p-2 border rounded w-full max-w-xs"
    >
      <option value="" disabled>
        Select a category
      </option>
      {categories.map(category => (
        <option key={category} value={category}>
          {category}
        </option>
      ))}
    </select>
  );
}

export default CategorySelect;