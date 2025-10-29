import MainNav from '@/components/navigation/mainNav';
import { ReactNode } from 'react';

export default function AppLayout({ children }: { children: ReactNode }) {
    return (
        <div>
            <MainNav />
            {children}
        </div>
    );
}
