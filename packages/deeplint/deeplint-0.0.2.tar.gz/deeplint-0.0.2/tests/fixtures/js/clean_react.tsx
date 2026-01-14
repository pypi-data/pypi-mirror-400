// Clean React/TypeScript code - should have minimal or no issues

import { useRouter } from 'next/router';
import Link from 'next/link';
import Image from 'next/image';
import { useState, useEffect, useCallback, useMemo } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
}

interface Props {
  initialCount: number;
}

function CleanComponent({ initialCount }: Props) {
  const [count, setCount] = useState(initialCount);
  const router = useRouter();
  
  // Proper derived state using useMemo
  const displayName = useMemo(() => {
    return `Count: ${count}`;
  }, [count]);
  
  // Proper useCallback with dependencies
  const handleIncrement = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);
  
  // Proper error handling
  const fetchUsers = async (): Promise<User[]> => {
    try {
      const response = await fetch('/api/users');
      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching users:', error);
      return [];
    }
  };
  
  // Proper batch state update
  const updateMultiple = (items: number[]) => {
    const total = items.reduce((sum, item) => sum + item, 0);
    setCount(total);
  };
  
  return (
    <div>
      <h1>{displayName}</h1>
      <button onClick={handleIncrement}>Increment</button>
      <Link href="/about">
        About
      </Link>
    </div>
  );
}

// Proper typing without 'any'
function processData<T>(data: T[]): T[] {
  return data.filter(item => item !== null);
}

// Design tokens instead of magic values
const theme = {
  colors: {
    primary: '#007bff',
    secondary: '#6c757d'
  },
  spacing: {
    medium: '16px',
    large: '24px'
  }
};

export default CleanComponent;
