import { useQuery } from '@tanstack/react-query';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';
import { apiClient } from '../lib/api';
import { format, subDays } from 'date-fns';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

function BalanceChart() {
    const { data: transactions = [] } = useQuery({
        queryKey: ['transactions'],
        queryFn: () => apiClient.getTransactions({ limit: 1000 }).then(res => res.data),
    });

    // Calculate daily balance for last 30 days
    const days = 30;
    const chartData = {
        labels: [] as string[],
        balances: [] as number[],
    };

    let runningBalance = 0;
    for (let i = days - 1; i >= 0; i--) {
        const date = subDays(new Date(), i);
        const dateStr = format(date, 'yyyy-MM-dd');

        // Calculate transactions for this day
        const dayTransactions = transactions.filter(t =>
            format(new Date(t.transaction_date), 'yyyy-MM-dd') === dateStr
        );

        const dayIncome = dayTransactions
            .filter(t => t.type === 'income')
            .reduce((sum, t) => sum + t.amount, 0);

        const dayExpense = dayTransactions
            .filter(t => t.type === 'expense')
            .reduce((sum, t) => sum + t.amount, 0);

        runningBalance += (dayIncome - dayExpense);

        chartData.labels.push(format(date, 'dd.MM'));
        chartData.balances.push(runningBalance);
    }

    const data = {
        labels: chartData.labels,
        datasets: [
            {
                label: 'Balans',
                data: chartData.balances,
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 6,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
            },
            tooltip: {
                callbacks: {
                    label: function (context: any) {
                        return new Intl.NumberFormat('uz-UZ').format(context.parsed.y) + ' UZS';
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function (value: any) {
                        return new Intl.NumberFormat('uz-UZ', { notation: 'compact' }).format(value);
                    }
                }
            }
        }
    };

    return (
        <div style={{ height: '300px' }}>
            <Line data={data} options={options} />
        </div>
    );
}

export default BalanceChart;
