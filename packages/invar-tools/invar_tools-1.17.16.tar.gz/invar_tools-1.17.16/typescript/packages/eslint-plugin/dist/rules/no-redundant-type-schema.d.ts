/**
 * Rule: no-redundant-type-schema
 *
 * Detect Zod schemas that only repeat TypeScript types without adding semantic constraints.
 *
 * Detects:
 * - z.string() without .min/.max/.regex/.email/etc
 * - z.number() without .int/.min/.max/.positive/etc
 * - z.boolean() (almost always redundant)
 */
import type { Rule } from 'eslint';
export declare const noRedundantTypeSchema: Rule.RuleModule;
export default noRedundantTypeSchema;
//# sourceMappingURL=no-redundant-type-schema.d.ts.map