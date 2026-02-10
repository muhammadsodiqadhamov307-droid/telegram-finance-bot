// Telegram WebApp types
interface TelegramWebApp {
    ready: () => void;
    expand: () => void;
    close: () => void;
    initData: string;
    initDataUnsafe: {
        user?: {
            id: number;
            first_name: string;
            last_name?: string;
            username?: string;
        };
    };
    colorScheme: 'light' | 'dark';
    BackButton: {
        show: () => void;
        hide: () => void;
        onClick: (callback: () => void) => void;
    };
    MainButton: {
        text: string;
        color: string;
        textColor: string;
        isVisible: boolean;
        isActive: boolean;
        show: () => void;
        hide: () => void;
        enable: () => void;
        disable: () => void;
        onClick: (callback: () => void) => void;
    };
    HapticFeedback: {
        impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
        notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
        selectionChanged: () => void;
    };
}

interface Window {
    Telegram: {
        WebApp: TelegramWebApp;
    };
}

// Transaction types
export interface Transaction {
    id: number;
    type: 'income' | 'expense';
    amount: number;
    category_id?: number;
    category_name?: string;
    description?: string;
    transaction_date: string;
    created_at: string;
}

export interface Category {
    id: number;
    name: string;
    type: 'income' | 'expense';
    icon: string;
    color: string;
    is_default: boolean;
}

export interface Summary {
    total_income: number;
    total_expense: number;
    balance: number;
    transaction_count: number;
}

export interface UserProfile {
    telegram_id: number;
    first_name: string;
    last_name?: string;
    username?: string;
    currency: string;
    theme: string;
    language: string;
}
