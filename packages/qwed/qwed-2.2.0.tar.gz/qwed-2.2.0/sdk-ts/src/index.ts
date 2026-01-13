/**
 * @qwed-ai/sdk
 * TypeScript SDK for QWED Verification Protocol
 * 
 * @example
 * ```typescript
 * import { QWEDClient } from '@qwed-ai/sdk';
 * 
 * const client = new QWEDClient({ apiKey: 'qwed_...' });
 * const result = await client.verify('What is 2+2?');
 * console.log(result.verified); // true
 * ```
 */

// Re-export types
export * from './types';

// Re-export client and helpers
export {
    QWEDClient,
    QWEDError,
    QWEDAuthError,
    QWEDRateLimitError,
    isVerified,
    getErrorMessage,
    parseAttestation,
} from './client';

