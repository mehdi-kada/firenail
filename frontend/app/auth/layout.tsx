import LandingNav from '@/components/navigation/landingNav';
import { ReactNode } from 'react';

export default function AuthLayout({ children }: { children: ReactNode }) {
    return (
        <div>
            <LandingNav />
            {children}
        </div>
    );
}