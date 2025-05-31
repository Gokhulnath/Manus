const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const fetcher = (url: string) =>
    fetch(`${API_BASE}${url}`).then((res) => {
        if (!res.ok) {
            throw new Error('An error occurred while fetching the data.');
        }
        return res.json();
    });

export const postData = async (url: string | URL | Request, data: unknown) => {
    const res = await fetch(`${API_BASE}${url}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });

    if (!res.ok) {
        const error = await res.json();
        throw new Error(error.message || 'Something went wrong');
    }

    return res.json();
};