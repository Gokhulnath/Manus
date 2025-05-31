import createClient from 'openapi-fetch';
import { createQueryHook } from "swr-openapi";
import type { paths } from './openapi-types';

const client = createClient<paths>({
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

export const useQuery = createQueryHook(client, "manus-clone-api");
