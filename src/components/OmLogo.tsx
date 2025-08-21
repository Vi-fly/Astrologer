import React from 'react';

interface OmLogoProps {
  size?: number;
  className?: string;
  animated?: boolean;
}

const OmLogo: React.FC<OmLogoProps> = ({ size = 32, className = "", animated = true }) => {
  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 100 100" 
      width={size} 
      height={size} 
      className={`${animated ? 'animate-pulse' : ''} ${className}`}
    >
      <defs>
        <linearGradient id="omGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{stopColor: '#3B82F6', stopOpacity: 1}} />
          <stop offset="50%" style={{stopColor: '#8B5CF6', stopOpacity: 1}} />
          <stop offset="100%" style={{stopColor: '#EC4899', stopOpacity: 1}} />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge> 
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* Background circle */}
      <circle cx="50" cy="50" r="45" fill="url(#omGradient)" opacity="0.1"/>
      
      {/* Om symbol */}
      <g transform="translate(50, 50)" filter="url(#glow)">
        {/* Main Om curve */}
        <path 
          d="M-25,-15 Q-15,-25 0,-25 Q15,-25 25,-15 Q25,-5 15,5 Q5,15 -5,15 Q-15,15 -25,5 Q-25,-5 -25,-15 Z" 
          fill="url(#omGradient)" 
          stroke="url(#omGradient)" 
          strokeWidth="2"
        />
        
        {/* Dot (bindu) */}
        <circle cx="0" cy="-10" r="3" fill="url(#omGradient)"/>
        
        {/* Crescent */}
        <path 
          d="M-20,-5 Q-10,-15 0,-15 Q10,-15 20,-5 Q20,5 10,15 Q0,15 -10,15 Q-20,5 -20,-5 Z" 
          fill="none" 
          stroke="url(#omGradient)" 
          strokeWidth="1.5" 
          opacity="0.7"
        />
        
        {/* Inner details */}
        <path 
          d="M-15,0 Q-5,-10 5,-10 Q15,-10 15,0 Q15,10 5,10 Q-5,10 -15,0 Z" 
          fill="none" 
          stroke="url(#omGradient)" 
          strokeWidth="1" 
          opacity="0.5"
        />
      </g>
      
      {/* Decorative elements */}
      <circle cx="20" cy="20" r="2" fill="url(#omGradient)" opacity="0.6"/>
      <circle cx="80" cy="30" r="1.5" fill="url(#omGradient)" opacity="0.4"/>
      <circle cx="25" cy="75" r="1.5" fill="url(#omGradient)" opacity="0.4"/>
      <circle cx="75" cy="70" r="2" fill="url(#omGradient)" opacity="0.6"/>
    </svg>
  );
};

export default OmLogo;
