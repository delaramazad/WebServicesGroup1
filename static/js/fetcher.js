export async function fetcher(request) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const resource = await response.json();
            return resource;
        }
    } catch (error) {
        console.warn(error);
    }
}