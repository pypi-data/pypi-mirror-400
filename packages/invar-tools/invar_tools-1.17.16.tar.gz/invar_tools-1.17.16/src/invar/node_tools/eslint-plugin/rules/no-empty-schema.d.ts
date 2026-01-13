/**
 * Rule: no-empty-schema
 *
 * Detect Zod schemas that match everything, providing false security.
 *
 * Detects:
 * - z.object({}) with no properties
 * - .passthrough() calls (defeats validation)
 * - .loose() calls (ignores unknown properties)
 */
import type { Rule } from 'eslint';
export declare const noEmptySchema: Rule.RuleModule;
export default noEmptySchema;
//# sourceMappingURL=no-empty-schema.d.ts.map