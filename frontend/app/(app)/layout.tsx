import MainNav from '@/components/navigation/mainNav';
import { SubscriptionBanner } from '@/components/subscription/SubscriptionBanner';
import { ReactNode } from 'react';

export default function AppLayout({ children }: { children: ReactNode }) {
    return (
        <div>
            <MainNav />
            <SubscriptionBanner />
            {children}
        </div>
    );
}
