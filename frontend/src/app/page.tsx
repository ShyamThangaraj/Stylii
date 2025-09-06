"use client";

import { useState, useEffect } from "react";

interface BackendStatus {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  uptime: string;
  endpoints: {
    health: string;
    status: string;
    docs: string;
  };
}

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<BackendStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await fetch("http://localhost:8000/status");
        if (response.ok) {
          const data = await response.json();
          setBackendStatus(data);
          setError(null);
        } else {
          setError(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (err) {
        setError("Backend is not reachable");
      } finally {
        setIsLoading(false);
      }
    };

    checkBackendStatus();
    
    // Check status every 5 seconds
    const interval = setInterval(checkBackendStatus, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              🍌 Nano Banana Hackathon
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Full-Stack Application Status Dashboard
            </p>
          </div>

          {/* Status Cards */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Frontend Status */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Frontend Status
                </h2>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-green-600 dark:text-green-400 font-medium">Running</span>
                </div>
              </div>
              <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <p><strong>Service:</strong> Next.js Frontend</p>
                <p><strong>URL:</strong> http://localhost:3000</p>
                <p><strong>Status:</strong> Active</p>
                <p><strong>Framework:</strong> Next.js with TypeScript</p>
              </div>
            </div>

            {/* Backend Status */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Backend Status
                </h2>
                <div className="flex items-center">
                  {isLoading ? (
                    <>
                      <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2 animate-pulse"></div>
                      <span className="text-yellow-600 dark:text-yellow-400 font-medium">Checking...</span>
                    </>
                  ) : error ? (
                    <>
                      <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                      <span className="text-red-600 dark:text-red-400 font-medium">Offline</span>
                    </>
                  ) : (
                    <>
                      <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                      <span className="text-green-600 dark:text-green-400 font-medium">Running</span>
                    </>
                  )}
                </div>
              </div>
              
              {isLoading ? (
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  <p>Checking backend connection...</p>
                </div>
              ) : error ? (
                <div className="space-y-2 text-sm">
                  <p className="text-red-600 dark:text-red-400"><strong>Error:</strong> {error}</p>
                  <p className="text-gray-600 dark:text-gray-300">
                    Make sure the backend is running on http://localhost:8000
                  </p>
                </div>
              ) : backendStatus ? (
                <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                  <p><strong>Service:</strong> {backendStatus.service}</p>
                  <p><strong>Version:</strong> {backendStatus.version}</p>
                  <p><strong>URL:</strong> http://localhost:8000</p>
                  <p><strong>Status:</strong> {backendStatus.status}</p>
                  <p><strong>Last Check:</strong> {new Date(backendStatus.timestamp).toLocaleTimeString()}</p>
                </div>
              ) : null}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Quick Actions
            </h2>
            <div className="grid md:grid-cols-3 gap-4">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="block p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
              >
                <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-1">
                  📚 API Documentation
                </h3>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  View FastAPI interactive docs
                </p>
              </a>
              
              <a
                href="http://localhost:8000/status"
                target="_blank"
                rel="noopener noreferrer"
                className="block p-4 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
              >
                <h3 className="font-medium text-green-900 dark:text-green-100 mb-1">
                  🔍 Backend Status
                </h3>
                <p className="text-sm text-green-700 dark:text-green-300">
                  Check detailed backend status
                </p>
              </a>
              
              <a
                href="http://localhost:8000/health"
                target="_blank"
                rel="noopener noreferrer"
                className="block p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
              >
                <h3 className="font-medium text-purple-900 dark:text-purple-100 mb-1">
                  ❤️ Health Check
                </h3>
                <p className="text-sm text-purple-700 dark:text-purple-300">
                  Simple health endpoint
                </p>
              </a>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center mt-8 text-sm text-gray-500 dark:text-gray-400">
            <p>Status updates every 5 seconds • Built with Next.js + FastAPI</p>
          </div>
        </div>
      </div>
    </div>
  );
}
