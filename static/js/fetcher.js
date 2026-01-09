export async function fetcher(request, options = {}) {
    try {
        const response = await fetch(request, options);
        if (response.ok) {
            const resource = await response.json();
            return resource;
        }
    } catch (error) {
        console.warn(error);
    }
}