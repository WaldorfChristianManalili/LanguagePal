import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'outline';
  className?: string;
  disabled?: boolean;
  hoverBg?: string;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  className = '',
  disabled = false,
  hoverBg,
}) => {
  const baseStyles = 'px-4 py-2 rounded-lg font-medium transition-colors';
  const defaultHoverBg = variant === 'outline' ? '#0EBE75' : '#0EBE75';
  const hoverStyles = hoverBg ? `hover:bg-[${hoverBg}]` : `hover:bg-[${defaultHoverBg}]`;
  const variantStyles =
    variant === 'outline'
      ? `border border-[#1079F1] bg-[#FFFFFF] text-[#252B2F] ${hoverStyles} hover:text-[#FFFFFF]`
      : `bg-[#1079F1] text-[#FFFFFF] ${hoverStyles}`;
  const disabledStyles = disabled ? 'opacity-50 cursor-not-allowed' : '';

  return (
    <button
      type={type}
      onClick={onClick}
      className={`${baseStyles} ${variantStyles} ${disabledStyles} ${className}`}
      disabled={disabled}
    >
      {children}
    </button>
  );
};