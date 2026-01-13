/**
 * Rule: require-schema-validation
 *
 * Zod-typed parameters must have a corresponding .parse() or .safeParse() call.
 *
 * Supports three modes:
 * - recommended: Warn on missing validation (default)
 * - strict: Error on missing validation
 * - risk-based: Error only for high-risk functions (payment, auth, etc.)
 */
import type { Rule } from 'eslint';
export declare const requireSchemaValidation: Rule.RuleModule;
export default requireSchemaValidation;
//# sourceMappingURL=require-schema-validation.d.ts.map