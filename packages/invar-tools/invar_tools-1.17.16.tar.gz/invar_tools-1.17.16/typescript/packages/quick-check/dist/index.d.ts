/**
 * @invar/quick-check - Fast pre-commit verification for TypeScript projects
 *
 * Provides sub-second verification using tsc --incremental and eslint --cache.
 * Designed for git pre-commit hooks where speed is critical.
 */
import { z } from 'zod';
export declare const QuickCheckOptionsSchema: z.ZodObject<{
    path: z.ZodDefault<z.ZodString>;
    skipTsc: z.ZodDefault<z.ZodBoolean>;
    skipEslint: z.ZodDefault<z.ZodBoolean>;
    verbose: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    path: string;
    skipTsc: boolean;
    skipEslint: boolean;
    verbose: boolean;
}, {
    path?: string | undefined;
    skipTsc?: boolean | undefined;
    skipEslint?: boolean | undefined;
    verbose?: boolean | undefined;
}>;
export type QuickCheckOptions = z.infer<typeof QuickCheckOptionsSchema>;
export declare const CheckResultSchema: z.ZodObject<{
    passed: z.ZodBoolean;
    cached: z.ZodBoolean;
    duration_ms: z.ZodNumber;
    error: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    passed: boolean;
    cached: boolean;
    duration_ms: number;
    error?: string | undefined;
}, {
    passed: boolean;
    cached: boolean;
    duration_ms: number;
    error?: string | undefined;
}>;
export type CheckResult = z.infer<typeof CheckResultSchema>;
export declare const QuickCheckResultSchema: z.ZodObject<{
    passed: z.ZodBoolean;
    duration_ms: z.ZodNumber;
    checks: z.ZodObject<{
        tsc: z.ZodOptional<z.ZodObject<{
            passed: z.ZodBoolean;
            cached: z.ZodBoolean;
            duration_ms: z.ZodNumber;
            error: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            passed: boolean;
            cached: boolean;
            duration_ms: number;
            error?: string | undefined;
        }, {
            passed: boolean;
            cached: boolean;
            duration_ms: number;
            error?: string | undefined;
        }>>;
        eslint: z.ZodOptional<z.ZodObject<{
            passed: z.ZodBoolean;
            cached: z.ZodBoolean;
            duration_ms: z.ZodNumber;
            error: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            passed: boolean;
            cached: boolean;
            duration_ms: number;
            error?: string | undefined;
        }, {
            passed: boolean;
            cached: boolean;
            duration_ms: number;
            error?: string | undefined;
        }>>;
    }, "strip", z.ZodTypeAny, {
        tsc?: {
            passed: boolean;
            cached: boolean;
            duration_ms: number;
            error?: string | undefined;
        } | undefined;
        eslint?: {
            passed: boolean;
            cached: boolean;
            duration_ms: number;
            error?: string | undefined;
        } | undefined;
    }, {
        tsc?: {
            passed: boolean;
            cached: boolean;
            duration_ms: number;
            error?: string | undefined;
        } | undefined;
        eslint?: {
            passed: boolean;
            cached: boolean;
            duration_ms: number;
            error?: string | undefined;
        } | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    passed: boolean;
    duration_ms: number;
    checks: {
        tsc?: {
            passed: boolean;
            cached: boolean;
            duration_ms: number;
            error?: string | undefined;
        } | undefined;
        eslint?: {
            passed: boolean;
            cached: boolean;
            duration_ms: number;
            error?: string | undefined;
        } | undefined;
    };
}, {
    passed: boolean;
    duration_ms: number;
    checks: {
        tsc?: {
            passed: boolean;
            cached: boolean;
            duration_ms: number;
            error?: string | undefined;
        } | undefined;
        eslint?: {
            passed: boolean;
            cached: boolean;
            duration_ms: number;
            error?: string | undefined;
        } | undefined;
    };
}>;
export type QuickCheckResult = z.infer<typeof QuickCheckResultSchema>;
/**
 * Run quick verification checks.
 *
 * @param options - Configuration options
 * @returns Result object with pass/fail status and timing
 *
 * @example
 * ```typescript
 * import { quickCheck } from '@invar/quick-check';
 *
 * const result = await quickCheck({ path: './my-project' });
 * if (result.passed) {
 *   console.log(`Checks passed in ${result.duration_ms}ms`);
 * }
 * ```
 */
export declare function quickCheck(options?: Partial<QuickCheckOptions>): QuickCheckResult;
export default quickCheck;
//# sourceMappingURL=index.d.ts.map