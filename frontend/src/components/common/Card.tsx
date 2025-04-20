import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ children, className = '' }) => {
  return (
    <div className={`bg-[#ffffff] border border-[#aacdf9] rounded-lg shadow-sm p-6 ${className}`}>
      {children}
    </div>
  );
};