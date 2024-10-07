import React from 'react';
import { AppProps } from 'next/app';
import { AuthProvider } from '../contexts/AuthContext';
import RootLayout from '../components/layout';

const MyApp = ({ Component, pageProps }: AppProps) => {
  return (
    <AuthProvider>
      <RootLayout>
        <Component {...pageProps} />
      </RootLayout>
    </AuthProvider>
  );
};

export default MyApp;
