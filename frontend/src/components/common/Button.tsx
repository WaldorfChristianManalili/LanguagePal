import { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline';
  className?: string;
}

function Button({ variant = 'primary', className = '', children, ...props }: ButtonProps) {
  const baseStyles = 'px-4 py-2 rounded font-semibold transition-colors';
  const variantStyles =
    variant === 'primary'
      ? 'bg-blue-600 text-white hover:bg-blue-700'
      : 'border border-blue-600 text-blue-600 hover:bg-blue-50';

  return (
    <button className={`${baseStyles} ${variantStyles} ${className}`} {...props}>
      {children}
    </button>
  );
}

export { Button };