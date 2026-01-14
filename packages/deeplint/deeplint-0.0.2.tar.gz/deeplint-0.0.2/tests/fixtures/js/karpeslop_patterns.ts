// TypeScript file with KarpeSlop-inspired AI slop patterns

// 1. Hallucinated React imports - CRITICAL
import { useRouter, Link, Image } from 'react';  // Wrong! These are from next/router, next/link, next/image
import { getServerSideProps } from 'react';  // Wrong! This is a page-level export, not an import

// 2. TypeScript 'any' type usage - HIGH
function processData(data: any): any {
  const items: Array<any> = [];
  const lookup: { [key: string]: any } = {};
  return data as any;
}

// 3. React anti-patterns - HIGH/MEDIUM
function MyComponent({ count, name }: { count: number; name: string }) {
  const [total, setTotal] = useState(0);
  const [derived, setDerived] = useState('');
  
  // useEffect setting derived state - should use useMemo
  useEffect(() => { setDerived(name.toUpperCase()); }, [name]);
  
  // useEffect with empty deps - might be missing dependencies
  useEffect(() => { console.log('Component mounted'); }, []);
  
  // setState in loop - causes multiple re-renders
  const updateItems = (items: any[]) => {
    for (let i = 0; i < items.length; i++) { setTotal(total + items[i]); }
  };
  
  // useCallback with empty deps - stale closure
  const handleClick = useCallback(() => { console.log(count); }, []);
  
  return <div>{total}</div>;
}

// 4. Style issues
// obviously this is the best way
const unnecessary = (async () => { return fetch('/api/data'); })();

// Nested ternary abuse
const status = loading ? "loading" : error ? "error" : success ? "success" : "idle";

// Magic CSS values
const styles = {
  width: '1024px',
  color: '#ff5733',
  padding: 'rgba(255, 87, 51, 0.5)'
};

// 5. Quality issues
// TODO: implement proper error handling here
// assuming this will always work
async function fetchData() {
  // Missing error handling
  const response = await fetch('/api/users');
  return response.json();
}

// 6. Noise issues
// This function processes the user data
function processUserData(user: any) {
  console.log("debug: processing user");  // Debug log with comment
  console.log('Starting process');  // Production console log
  
  // increment counter
  const count = user.count;
  const result = count + 1;
  
  return result;
}

// 7. More overconfident and hedging comments
// clearly this is the right approach
// should work hopefully
const value = calculateValue();
