import { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './pages/Dashboard';
import './index.css';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: false,
            retry: 1,
        },
    },
});

function App() {
    const [theme, setTheme] = useState<'light' | 'dark'>('light');

    useEffect(() => {
        const tgTheme = window.Telegram?.WebApp?.colorScheme || 'light';
        setTheme(tgTheme);
        window.Telegram?.WebApp?.ready();
        window.Telegram?.WebApp?.expand();
    }, []);

    return (
        <QueryClientProvider client={queryClient}>
            <div className={`min-h-screen ${theme === 'dark' ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
                <Dashboard />
            </div>
        </QueryClientProvider>
    );
}

export default App;
