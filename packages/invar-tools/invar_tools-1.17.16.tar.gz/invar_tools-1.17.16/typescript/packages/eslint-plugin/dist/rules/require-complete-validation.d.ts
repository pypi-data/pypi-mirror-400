/**
 * Rule: require-complete-validation
 *
 * Detect functions where some parameters have Zod schema validation but others don't.
 * Either all parameters should be validated, or none should be.
 *
 * Detects:
 * - Functions with mixed z.infer<typeof Schema> and plain types
 */
import type { Rule } from 'eslint';
export declare const requireCompleteValidation: Rule.RuleModule;
export default requireCompleteValidation;
//# sourceMappingURL=require-complete-validation.d.ts.map