import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Moon, Sun, ArrowLeft, Search, History, LogOut } from 'lucide-react';


interface WebResult {
    title: string;
    link: string;
    snippet: string;
}

interface SearchResult {
    web_results: WebResult[];
    ai_answer: string;
}

interface User {
    username: string;
    email: string;
}

interface Query {
    _id: string;
    query: string;
    created_at: string;
    ai_answer?: string;
}

const API_BASE_URL = 'http://localhost:8000';

const App: React.FC = () => {
    // Theme State
    const [darkMode, setDarkMode] = useState(() => {
        // Check local storage or system preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) return savedTheme === 'dark';
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    });

    // Authentication State
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState<User | null>(null);

    // Search State
    const [query, setQuery] = useState('');
    const [searchResults, setSearchResults] = useState<SearchResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Query History State
    const [queries, setQueries] = useState<Query[]>([]);
    const [queryPage, setQueryPage] = useState(1);
    const [queryDays, setQueryDays] = useState(7);
    const [queryLoading, setQueryLoading] = useState(false);

    // View Management
    const [currentView, setCurrentView] = useState<'login' | 'signup' | 'search' | 'history'>('login');

    // Theme Toggle Effect
    useEffect(() => {
        // Apply dark mode to the document
        if (darkMode) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    }, [darkMode]);


    // Token Management
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            setIsAuthenticated(true);
            setCurrentView('search');
        }
    }, []);

    const handleLogin = async (username: string, password: string) => {
        try {
            const response = await axios.post(`${API_BASE_URL}/login`, null, {
                params: { username, password }
            });

            localStorage.setItem('token', response.data.access_token);
            setIsAuthenticated(true);
            setUser({ username, email: '' }); // Basic user info
            setCurrentView('search');
            setError(null);
        } catch (err) {
            setError('Login failed. Check your credentials.');
        }
    };

    const handleSignup = async (username: string, email: string, password: string) => {
        try {
            await axios.post(`${API_BASE_URL}/signup`, {
                username,
                email,
                password
            });
            setCurrentView('login');
            alert('Signup successful! Please log in.');
        } catch (err) {
            setError('Signup failed. Username or email might already exist.');
        }
    };

    const handleSearch = async () => {
        if (!query.trim()) return;

        setLoading(true);
        setError(null);
        setSearchResults(null);

        try {
            const token = localStorage.getItem('token');
            const response = await axios.post<SearchResult>(
                `${API_BASE_URL}/search`,
                { query },
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );
            setSearchResults(response.data);
        } catch (err) {
            setError('Search failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const fetchQueryHistory = async () => {
        try {
            setQueryLoading(true);
            const token = localStorage.getItem('token');
            const response = await axios.get<Query[]>(`${API_BASE_URL}/queries`, {
                params: {
                    days: queryDays,
                    page: queryPage,
                    page_size: 10
                },
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            setQueries(response.data);
        } catch (err) {
            setError('Failed to fetch query history.');
        } finally {
            setQueryLoading(false);
        }
    };
    const handleLogout = () => {
        localStorage.removeItem('token');
        setIsAuthenticated(false);
        setUser(null);
        setCurrentView('login');
    };
    const renderThemeToggle = () => (
        <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition"
        >
            {darkMode ? <Sun className="text-yellow-500" /> : <Moon className="text-indigo-600" />}
        </button>
    );

    const renderLogin = () => (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white dark:bg-gray-800 p-8 rounded-xl shadow-2xl">
                <div className="flex justify-between items-center">
                    <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white">
                        Cerebro
                    </h2>
                    {renderThemeToggle()}
                </div>
                <form
                    className="mt-8 space-y-6"
                    onSubmit={(e) => {
                        e.preventDefault();
                        const formData = new FormData(e.currentTarget);
                        handleLogin(
                            formData.get('username') as string,
                            formData.get('password') as string
                        );
                    }}
                >
                    <input
                        type="text"
                        name="username"
                        required
                        placeholder="Username"
                        className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                    <input
                        type="password"
                        name="password"
                        required
                        placeholder="Password"
                        className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                    {error && <p className="text-red-500 text-center">{error}</p>}
                    <button
                        type="submit"
                        className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        Sign In
                    </button>
                    <div className="text-center">
                        <button
                            type="button"
                            onClick={() => setCurrentView('signup')}
                            className="text-indigo-600 hover:text-indigo-500"
                        >
                            Create an account
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );

    const renderSignup = () => (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Create your account
                    </h2>
                </div>
                <form
                    className="mt-8 space-y-6"
                    onSubmit={(e) => {
                        e.preventDefault();
                        const formData = new FormData(e.currentTarget);
                        handleSignup(
                            formData.get('username') as string,
                            formData.get('email') as string,
                            formData.get('password') as string
                        );
                    }}
                >
                    <input
                        type="text"
                        name="username"
                        required
                        placeholder="Username"
                        className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                    <input
                        type="email"
                        name="email"
                        required
                        placeholder="Email"
                        className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                    <input
                        type="password"
                        name="password"
                        required
                        placeholder="Password"
                        className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                    {error && <p className="text-red-500 text-center">{error}</p>}
                    <button
                        type="submit"
                        className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        Sign Up
                    </button>
                    <div className="text-center">
                        <button
                            type="button"
                            onClick={() => setCurrentView('login')}
                            className="text-indigo-600 hover:text-indigo-500"
                        >
                            Already have an account? Sign In
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );

    const renderQueryHistory = () => (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-8">
            <div className="container mx-auto max-w-4xl">
                <div className="flex justify-between items-center mb-8">
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={() => setCurrentView('search')}
                            className="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white p-2 rounded-full hover:bg-gray-300 dark:hover:bg-gray-600"
                        >
                            <ArrowLeft />
                        </button>
                        <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Query History</h1>
                    </div>
                    <div className="flex items-center space-x-4">
                        {user && <span className="text-gray-600 dark:text-gray-300">Welcome, {user.username}</span>}
                        {renderThemeToggle()}
                        <button
                            onClick={handleLogout}
                            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                        >
                            <LogOut />
                        </button>
                    </div>
                </div>
                <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
                    <div className="flex mb-6 space-x-4">
                        <select
                            value={queryDays}
                            onChange={(e) => setQueryDays(parseInt(e.target.value))}
                            className="flex-grow p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                            <option value={7}>Last 7 days</option>
                            <option value={30}>Last 30 days</option>
                            <option value={90}>Last 90 days</option>
                        </select>
                        <button
                            onClick={fetchQueryHistory}
                            disabled={queryLoading}
                            className="bg-indigo-600 text-white px-6 py-3 rounded hover:bg-indigo-700 disabled:opacity-50"
                        >
                            {queryLoading ? 'Loading...' : 'Fetch History'}
                        </button>
                    </div>

                    {queryLoading && (
                        <div className="text-center text-gray-600 animate-pulse">
                            Loading query history...
                        </div>
                    )}

                    {queries.length > 0 && (
                        <div>
                            {queries.map((queryItem) => (
                                <div
                                    key={queryItem._id}
                                    className="bg-white border-b border-gray-200 p-4 hover:bg-gray-50 transition"
                                >
                                    <div className="flex justify-between items-center">
                                        <div>
                                            <p className="text-gray-800 font-semibold">{queryItem.query}</p>
                                            <p className="text-gray-500 text-sm">
                                                {new Date(queryItem.created_at).toLocaleString()}
                                            </p>
                                        </div>
                                        {queryItem.ai_answer && (
                                            <button
                                                className="text-indigo-600 hover:underline"
                                                onClick={() => {
                                                    setSearchResults({
                                                        web_results: [],
                                                        ai_answer: queryItem.ai_answer || ''
                                                    });
                                                    setCurrentView('search');
                                                }}
                                            >
                                                View Answer
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );

    const renderSearch = () => (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-8">
            <div className="container mx-auto max-w-4xl">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Cerebro</h1>
                    <div className="flex items-center space-x-4">
                        {user && <span className="text-gray-600 dark:text-gray-300">Welcome, {user.username}</span>}
                        {renderThemeToggle()}
                        <button
                            onClick={() => {
                                fetchQueryHistory();
                                setCurrentView('history');
                            }}
                            className="bg-gray-500 dark:bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-600 dark:hover:bg-gray-600"
                        >
                            <History />
                        </button>
                        <button
                            onClick={handleLogout}
                            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                        >
                            <LogOut />
                        </button>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
                    <div className="flex mb-6">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Ask anything..."
                            className="flex-grow p-3 border border-gray-300 dark:border-gray-600 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                        <button
                            onClick={handleSearch}
                            disabled={loading}
                            className="bg-indigo-600 text-white px-6 py-3 rounded-r-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center"
                        >
                            <Search className="mr-2" />
                            {loading ? 'Searching...' : 'Search'}
                        </button>
                    </div>

                    {loading && (
                        <div className="text-center text-gray-600 dark:text-gray-300 animate-pulse">
                            Searching the web and generating AI answer...
                        </div>
                    )}

                    {error && (
                        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                            {error}
                        </div>
                    )}

                    {searchResults && (
                        <div>
                            <div className="mb-6">
                                <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4">AI Answer</h2>
                                <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg text-gray-900 dark:text-white">
                                    {searchResults.ai_answer}
                                </div>
                            </div>

                            <div>
                                <h2 className="text-2xl font-semibold text-gray-800 mb-4">Web Results</h2>
                                {searchResults.web_results.map((result, index) => (
                                    <div
                                        key={index}
                                        className="bg-white border-b border-gray-200 p-4 hover:bg-gray-50 transition"
                                    >
                                        <a
                                            href={result.link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-indigo-600 text-lg font-semibold hover:underline"
                                        >
                                            {result.title}
                                        </a>
                                        <p className="text-gray-600 mt-2">{result.snippet}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );

    return (
        <div className={darkMode ? 'dark' : ''}>
            {!isAuthenticated && currentView === 'login' && renderLogin()}
            {!isAuthenticated && currentView === 'signup' && renderSignup()}
            {isAuthenticated && currentView === 'search' && renderSearch()}
            {isAuthenticated && currentView === 'history' && renderQueryHistory()}
        </div>
    );
};

export default App;