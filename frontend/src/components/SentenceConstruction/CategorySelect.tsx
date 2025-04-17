import React from 'react';

interface CategorySelectProps {
  categories: string[];
  selectedCategory: string;
  onChange: (category: string) => void;
  disabled?: boolean;
}

const CategorySelect: React.FC<CategorySelectProps> = ({
  categories,
  selectedCategory,
  onChange,
  disabled = false,
}) => {
  return (
    <div className="category-select mb-6">
      <label htmlFor="category-select" className="text-gray-700 mr-2">
        Select Category:
      </label>
      <select
        id="category-select"
        value={selectedCategory}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="border rounded p-2"
      >
        {categories.length === 0 ? (
          <option value="">No categories available</option>
        ) : (
          categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))
        )}
      </select>
    </div>
  );
};

export default CategorySelect;