import { HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  className?: string;
}

function Card({ className = '', children, ...props }: CardProps) {
  return (
    <div
      className={`bg-white shadow-md rounded-lg p-6 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export { Card };